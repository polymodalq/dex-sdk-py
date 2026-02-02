//! Block Event Fetching
//!
//! Efficient per-block event fetching for incremental state updates.
//!
//! This module provides a high-performance alternative to full snapshot rebuilds,
//! enabling per-block state updates with minimal RPC calls (2 per block).
//!
//! ## Usage
//!
//! ```python
//! from perpl_sdk import Chain, fetch_block_events
//!
//! chain = Chain.testnet()
//! events = fetch_block_events(chain, "https://rpc.monad.xyz", 12345)
//!
//! if events:
//!     state_events = exchange.apply_events(events)
//! ```

use std::time::Duration;

use alloy::providers::{Provider, ProviderBuilder};
use alloy::rpc::client::RpcClient;
use futures::StreamExt;
use pyo3::prelude::*;

use dex_sdk::{stream, types};

use crate::bindings::{chain::Chain, stream::RawBlockEvents};
use crate::ffi::error::to_py_err;

/// Fetch events for a single block from the blockchain.
///
/// This is the core building block for efficient per-block state updates.
/// It makes exactly 2 RPC calls per block (get_block + get_logs), which is
/// much faster than rebuilding a full snapshot.
///
/// Args:
///     chain: Chain configuration
///     rpc_url: RPC endpoint URL
///     block_number: Block number to fetch events for
///
/// Returns:
///     RawBlockEvents if the block exists, None if not available yet
///
/// Raises:
///     DexError: If there's an RPC or decoding error
///
/// Example:
///     ```python
///     from perpl_sdk import Chain, fetch_block_events, SnapshotBuilder
///
///     chain = Chain.testnet()
///     rpc_url = "https://testnet.monad.xyz"
///
///     # Initial snapshot
///     builder = SnapshotBuilder(chain, rpc_url).with_perpetuals([16])
///     exchange = builder.build()
///     current_block = exchange.instant.block_number + 1
///
///     # Per-block updates (fast!)
///     while True:
///         events = fetch_block_events(chain, rpc_url, current_block)
///         if events is None:
///             time.sleep(0.1)  # Block not ready yet
///             continue
///         
///         # Apply events incrementally (in-memory, very fast)
///         state_events = exchange.apply_events(events)
///         current_block += 1
///     ```
#[pyfunction]
#[pyo3(signature = (chain, rpc_url, block_number))]
pub fn fetch_block_events(
    py: Python,
    chain: &Chain,
    rpc_url: &str,
    block_number: u64,
) -> PyResult<Option<RawBlockEvents>> {
    py.allow_threads(|| {
        crate::ffi::runtime::block_on(fetch_block_events_async(&chain.0, rpc_url, block_number))
    })
}

/// Fetch events for a range of blocks from the blockchain.
///
/// More efficient than calling fetch_block_events in a loop when catching up
/// on multiple blocks, as it processes them sequentially with minimal overhead.
///
/// Args:
///     chain: Chain configuration
///     rpc_url: RPC endpoint URL  
///     from_block: Starting block number (inclusive)
///     to_block: Ending block number (inclusive)
///
/// Returns:
///     List of RawBlockEvents for each block in range
///
/// Raises:
///     DexError: If there's an RPC or decoding error
///
/// Example:
///     ```python
///     # Catch up on missed blocks
///     events_list = fetch_block_events_range(chain, rpc_url, 100, 110)
///     for events in events_list:
///         exchange.apply_events(events)
///     ```
#[pyfunction]
#[pyo3(signature = (chain, rpc_url, from_block, to_block))]
pub fn fetch_block_events_range(
    py: Python,
    chain: &Chain,
    rpc_url: &str,
    from_block: u64,
    to_block: u64,
) -> PyResult<Vec<RawBlockEvents>> {
    py.allow_threads(|| {
        crate::ffi::runtime::block_on(fetch_block_events_range_async(
            &chain.0, rpc_url, from_block, to_block,
        ))
    })
}

/// Minimal sleep function that returns immediately (no actual waiting).
/// Used for single-block fetches where we don't want to wait.
async fn no_sleep(_: Duration) {}

/// Internal async implementation for fetching single block events.
async fn fetch_block_events_async(
    chain: &dex_sdk::Chain,
    rpc_url: &str,
    block_number: u64,
) -> PyResult<Option<RawBlockEvents>> {
    // Create RPC client and provider
    let url: url::Url = rpc_url
        .parse()
        .map_err(|e| to_py_err(format!("Invalid RPC URL: {}", e)))?;
    let client = RpcClient::builder().http(url);
    let provider = ProviderBuilder::new().connect_client(client);

    // Create instant for the block we want
    let instant = types::StateInstant::new(block_number, 0);

    // Use the SDK's raw stream function to fetch exactly one block
    // Pin the stream since the async block returned by raw() needs to be pinned
    let mut event_stream = Box::pin(stream::raw(chain, provider, instant, no_sleep));

    // Get the next (and only) block from the stream
    match event_stream.next().await {
        Some(Ok(events)) => Ok(Some(RawBlockEvents { inner: events })),
        Some(Err(dex_sdk::error::DexError::InvalidRequest(_))) => {
            // Block not available yet
            Ok(None)
        }
        Some(Err(e)) => Err(to_py_err(format!("Failed to fetch events: {}", e))),
        None => Ok(None), // Stream ended (shouldn't happen)
    }
}

/// Internal async implementation for fetching a range of block events.
async fn fetch_block_events_range_async(
    chain: &dex_sdk::Chain,
    rpc_url: &str,
    from_block: u64,
    to_block: u64,
) -> PyResult<Vec<RawBlockEvents>> {
    if from_block > to_block {
        return Err(to_py_err(format!(
            "from_block ({}) must be <= to_block ({})",
            from_block, to_block
        )));
    }

    let num_blocks = (to_block - from_block + 1) as usize;

    // Create RPC client and provider
    let url: url::Url = rpc_url
        .parse()
        .map_err(|e| to_py_err(format!("Invalid RPC URL: {}", e)))?;
    let client = RpcClient::builder().http(url);
    let provider = ProviderBuilder::new().connect_client(client);

    // Create instant for the starting block
    let instant = types::StateInstant::new(from_block, 0);

    // Use the SDK's raw stream function
    // Pin the stream since the async block returned by raw() needs to be pinned
    let event_stream = Box::pin(stream::raw(chain, provider, instant, no_sleep));

    // Take exactly the number of blocks we need
    let results: Vec<_> = event_stream.take(num_blocks).collect().await;

    // Convert results
    let mut events_vec = Vec::with_capacity(num_blocks);
    for (i, result) in results.into_iter().enumerate() {
        match result {
            Ok(events) => events_vec.push(RawBlockEvents { inner: events }),
            Err(e) => {
                return Err(to_py_err(format!(
                    "Failed to fetch events for block {}: {}",
                    from_block + i as u64,
                    e
                )));
            }
        }
    }

    Ok(events_vec)
}

/// Get the latest block number from the RPC.
///
/// Useful for determining the current chain head before fetching events.
///
/// Args:
///     rpc_url: RPC endpoint URL
///
/// Returns:
///     The latest block number
///
/// Raises:
///     DexError: If the RPC call fails
#[pyfunction]
pub fn get_latest_block(py: Python, rpc_url: &str) -> PyResult<u64> {
    py.allow_threads(|| crate::ffi::runtime::block_on(get_latest_block_async(rpc_url)))
}

async fn get_latest_block_async(rpc_url: &str) -> PyResult<u64> {
    let url: url::Url = rpc_url
        .parse()
        .map_err(|e| to_py_err(format!("Invalid RPC URL: {}", e)))?;
    let client = RpcClient::builder().http(url);
    let provider = ProviderBuilder::new().connect_client(client);

    provider
        .get_block_number()
        .await
        .map_err(|e| to_py_err(format!("Failed to get latest block: {}", e)))
}
