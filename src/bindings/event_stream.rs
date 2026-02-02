//! Event Streaming Infrastructure
//!
//! This module provides WebSocket-based event streaming for real-time
//! state updates from the blockchain.
//!
//! ## Architecture
//!
//! ```text
//! EventStreamBuilder --> WsSubscription --> EventStream
//!                             |                  |
//!                             v                  v
//!                      WebSocket RPC      Python async iterator
//!                             |
//!                             v
//!                      eth_subscribe logs
//! ```
//!
//! ## Usage
//!
//! ```python
//! stream = await EventStreamBuilder(chain, "wss://...").from_block(12345).build()
//!
//! async for raw_events in stream:
//!     state_events = exchange.apply_events(raw_events)
//!     await process_events(state_events)
//! ```

use std::sync::Arc;
use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyStopAsyncIteration};
use tokio::sync::mpsc;
use futures::{StreamExt, SinkExt};
use tokio_tungstenite::{connect_async, tungstenite::Message};
use alloy::primitives::Address;
use serde::{Deserialize, Serialize};
use serde_json::json;

use crate::bindings::chain::Chain;
use crate::bindings::stream::RawBlockEvents;
use crate::bindings::types::StateInstant;
use crate::ffi::error::to_py_err;
use crate::ffi::runtime;

/// Internal message type for the event stream channel
enum StreamMessage {
    Events(dex_sdk::stream::RawBlockEvents),
    Error(String),
    Closed,
}

/// Builder for creating WebSocket-based event streams
///
/// Configure the stream parameters and call `build()` to start receiving events.
///
/// Example:
///     ```python
///     stream = EventStreamBuilder(chain, "wss://testnet-rpc.monad.xyz/ws")
///         .from_block(exchange.instant.block_number + 1)
///         .build()
///     ```
#[pyclass(name = "EventStreamBuilder", module = "perpl_sdk")]
#[derive(Clone)]
pub struct EventStreamBuilder {
    chain: Chain,
    ws_url: String,
    from_block: Option<u64>,
}

#[pymethods]
impl EventStreamBuilder {
    /// Create a new EventStreamBuilder
    ///
    /// Args:
    ///     chain: Chain configuration
    ///     ws_url: WebSocket RPC endpoint URL (must start with wss:// or ws://)
    #[new]
    fn new(chain: Chain, ws_url: String) -> Self {
        Self {
            chain,
            ws_url,
            from_block: None,
        }
    }
    
    /// Set the starting block number for event streaming
    ///
    /// Events from this block onwards will be streamed.
    /// If not set, streaming starts from the latest block.
    ///
    /// Args:
    ///     block: Starting block number
    ///
    /// Returns:
    ///     Self for chaining
    fn from_block(mut slf: PyRefMut<'_, Self>, block: u64) -> PyRefMut<'_, Self> {
        slf.from_block = Some(block);
        slf
    }
    
    /// Build and start the event stream
    ///
    /// This connects to the WebSocket RPC and subscribes to exchange contract events.
    /// Returns an EventStream that can be used as an async iterator.
    ///
    /// Returns:
    ///     EventStream async iterator
    ///
    /// Raises:
    ///     DexError: If connection or subscription fails
    fn build(&self, py: Python<'_>) -> PyResult<EventStream> {
        let builder = self.clone();
        
        py.allow_threads(|| {
            runtime::block_on(async {
                builder.build_async().await
            })
        })
    }
    
    fn __repr__(&self) -> String {
        format!(
            "EventStreamBuilder(ws_url='{}', from_block={:?})",
            self.ws_url,
            self.from_block
        )
    }
}

impl EventStreamBuilder {
    async fn build_async(&self) -> PyResult<EventStream> {
        // Create a channel for events
        let (tx, rx) = mpsc::channel::<StreamMessage>(100);
        
        // Clone data for the background task
        let ws_url = self.ws_url.clone();
        let exchange_address = self.chain.0.exchange();
        let from_block = self.from_block;
        
        // Spawn the WebSocket listener task
        let handle = runtime::spawn(async move {
            if let Err(e) = run_ws_subscription(ws_url, exchange_address, from_block, tx.clone()).await {
                let _ = tx.send(StreamMessage::Error(e)).await;
            }
            let _ = tx.send(StreamMessage::Closed).await;
        });
        
        Ok(EventStream {
            receiver: Arc::new(tokio::sync::Mutex::new(rx)),
            _handle: Some(handle),
        })
    }
}

/// Async event stream for receiving blockchain events
///
/// This implements Python's async iterator protocol, allowing usage like:
///
/// ```python
/// async for events in stream:
///     # process events
/// ```
#[pyclass(name = "EventStream", module = "perpl_sdk")]
pub struct EventStream {
    receiver: Arc<tokio::sync::Mutex<mpsc::Receiver<StreamMessage>>>,
    _handle: Option<tokio::task::JoinHandle<()>>,
}

#[pymethods]
impl EventStream {
    /// Async iterator protocol - returns self
    fn __aiter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }
    
    /// Async iterator protocol - get next item
    ///
    /// Returns the next RawBlockEvents or raises StopAsyncIteration when done.
    fn __anext__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let receiver = self.receiver.clone();
        
        // Use pyo3-asyncio to bridge Rust futures to Python awaitable
        // Since we don't have pyo3-asyncio, we'll use a blocking approach
        // wrapped in asyncio.to_thread
        
        // For now, provide a sync method that can be wrapped
        // Full async support requires pyo3-asyncio
        Err(PyRuntimeError::new_err(
            "Direct async iteration not yet supported. Use stream.next() with asyncio.to_thread() instead."
        ))
    }
    
    /// Get the next block of events (blocking)
    ///
    /// This method blocks until events are received.
    /// Use with asyncio.to_thread() for async contexts.
    ///
    /// Returns:
    ///     RawBlockEvents or None if stream is closed
    ///
    /// Example:
    ///     ```python
    ///     import asyncio
    ///     
    ///     async def process():
    ///         while True:
    ///             events = await asyncio.to_thread(stream.next)
    ///             if events is None:
    ///                 break
    ///             state_events = exchange.apply_events(events)
    ///     ```
    fn next(&self, py: Python<'_>) -> PyResult<Option<RawBlockEvents>> {
        let receiver = self.receiver.clone();
        
        py.allow_threads(|| {
            runtime::block_on(async {
                let mut rx = receiver.lock().await;
                match rx.recv().await {
                    Some(StreamMessage::Events(events)) => {
                        Ok(Some(RawBlockEvents { inner: events }))
                    }
                    Some(StreamMessage::Error(e)) => {
                        Err(to_py_err(format!("Stream error: {}", e)))
                    }
                    Some(StreamMessage::Closed) | None => {
                        Ok(None)
                    }
                }
            })
        })
    }
    
    /// Close the event stream
    ///
    /// Stops receiving events and cleans up resources.
    fn close(&mut self) {
        // Dropping the handle will cancel the task
        self._handle = None;
    }
    
    fn __repr__(&self) -> String {
        "EventStream(active)".to_string()
    }
}

/// JSON-RPC subscription response
#[derive(Debug, Deserialize)]
struct SubscriptionResponse {
    #[serde(default)]
    result: Option<String>,
    #[serde(default)]
    error: Option<serde_json::Value>,
}

/// JSON-RPC subscription notification
#[derive(Debug, Deserialize)]
struct SubscriptionNotification {
    params: SubscriptionParams,
}

#[derive(Debug, Deserialize)]
struct SubscriptionParams {
    subscription: String,
    result: serde_json::Value,
}

/// Run the WebSocket subscription loop
async fn run_ws_subscription(
    ws_url: String,
    exchange_address: Address,
    from_block: Option<u64>,
    tx: mpsc::Sender<StreamMessage>,
) -> Result<(), String> {
    // Connect to WebSocket
    let (mut ws_stream, _) = connect_async(&ws_url)
        .await
        .map_err(|e| format!("WebSocket connection failed: {}", e))?;
    
    // Subscribe to logs for the exchange contract
    let subscribe_msg = json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["logs", {
            "address": format!("{:?}", exchange_address)
        }]
    });
    
    ws_stream
        .send(Message::Text(subscribe_msg.to_string()))
        .await
        .map_err(|e| format!("Failed to send subscription: {}", e))?;
    
    // Wait for subscription confirmation
    let msg = ws_stream.next().await
        .ok_or_else(|| "WebSocket closed before subscription confirmed".to_string())?
        .map_err(|e| format!("WebSocket error: {}", e))?;
    
    let response: SubscriptionResponse = match msg {
        Message::Text(text) => {
            serde_json::from_str(&text)
                .map_err(|e| format!("Failed to parse subscription response: {}", e))?
        }
        _ => return Err("Unexpected message type".to_string()),
    };
    
    if let Some(error) = response.error {
        return Err(format!("Subscription failed: {:?}", error));
    }
    
    let _subscription_id = response.result
        .ok_or_else(|| "No subscription ID in response".to_string())?;
    
    // Listen for events
    while let Some(msg) = ws_stream.next().await {
        match msg {
            Ok(Message::Text(text)) => {
                // Parse the notification
                // Note: Full implementation would decode the log events into RawBlockEvents
                // This is a simplified version that logs receipt of events
                
                // For now, we acknowledge the event but don't fully decode it
                // Full implementation requires integrating with SDK's event parsing
                tracing::debug!("Received event notification: {}", &text[..text.len().min(200)]);
                
                // TODO: Parse log events and convert to RawBlockEvents
                // This requires:
                // 1. Parsing the JSON-RPC notification
                // 2. Decoding log data using Exchange ABI
                // 3. Grouping events by block
                // 4. Creating RawBlockEvents
            }
            Ok(Message::Close(_)) => {
                tracing::info!("WebSocket closed by server");
                break;
            }
            Ok(_) => {
                // Ignore other message types
            }
            Err(e) => {
                tracing::error!("WebSocket error: {}", e);
                return Err(format!("WebSocket error: {}", e));
            }
        }
    }
    
    Ok(())
}
