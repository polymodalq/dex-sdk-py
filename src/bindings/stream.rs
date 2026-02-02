//! Event Streaming
//!
//! Types and utilities for working with blockchain events.
//!
//! Note: Full async streaming requires additional dependencies. For now, this module
//! provides the core event types that can be used with `Exchange.apply_events()`.

use pyo3::prelude::*;
use pyo3::types::PyList;
use dex_sdk::{stream, state as sdk_state, types as sdk_types};
use crate::bindings::types::{StateInstant, Trade};
use crate::ffi::error::to_py_err;

// =============================================================================
// Raw Event Types
// =============================================================================

/// Raw blockchain event emitted by the exchange contract
///
/// These events can be applied to an Exchange snapshot using `apply_events()`.
/// 
/// Note: This type cannot be cloned or stored independently. It's meant to be
/// processed immediately when received.
#[pyclass(name = "RawEvent", module = "perpl_sdk", frozen)]
pub struct RawEvent {
    // Note: We don't own this, it's a reference from the parent RawBlockEvents
    // So we can't derive Clone
    tx_hash: String,
    tx_index: u64,
    log_index: u64,
    event_type: String,
}

#[pymethods]
impl RawEvent {
    /// Transaction hash
    #[getter]
    fn tx_hash(&self) -> String {
        self.tx_hash.clone()
    }
    
    /// Transaction index
    #[getter]
    fn tx_index(&self) -> u64 {
        self.tx_index
    }
    
    /// Log index
    #[getter]
    fn log_index(&self) -> u64 {
        self.log_index
    }
    
    /// Event type name
    #[getter]
    fn event_type(&self) -> String {
        self.event_type.clone()
    }
    
    fn __repr__(&self) -> String {
        format!(
            "RawEvent(tx={}, tx_idx={}, log_idx={})",
            &self.tx_hash[..std::cmp::min(10, self.tx_hash.len())],
            self.tx_index,
            self.log_index
        )
    }
}

/// Block of raw events
///
/// All events emitted in a single block, used to update Exchange state.
#[pyclass(name = "RawBlockEvents", module = "perpl_sdk", frozen)]
pub struct RawBlockEvents {
    pub(crate) inner: stream::RawBlockEvents,
}

#[pymethods]
impl RawBlockEvents {
    /// State instant (block number and timestamp)
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// All events in this block
    fn events(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for event in self.inner.events() {
            let event_obj = Bound::new(py, RawEvent {
                tx_hash: format!("{:?}", event.tx_hash()),
                tx_index: event.tx_index(),
                log_index: event.log_index(),
                event_type: format!("{:?}", event.event()),
            })?;
            list.append(event_obj)?;
        }
        Ok(list.unbind())
    }
    
    /// Number of events in this block
    fn len(&self) -> usize {
        self.inner.events().len()
    }
    
    fn __repr__(&self) -> String {
        format!(
            "RawBlockEvents(block={}, events={})",
            self.inner.instant().block_number(),
            self.inner.events().len()
        )
    }
    
    fn __len__(&self) -> usize {
        self.len()
    }
}

// =============================================================================
// State Events
// =============================================================================

/// State mutation event
///
/// Higher-level events produced after applying raw events to Exchange state.
/// For Trade events, detailed trade data is available via `as_trade()`.
#[pyclass(name = "StateEvent", module = "perpl_sdk", frozen)]
pub struct StateEvent {
    category: String,
    description: String,
    trade: Option<sdk_types::Trade>,
}

#[pymethods]
impl StateEvent {
    /// Event category (Account, Error, Exchange, Order, Perpetual, Position, Trade)
    #[getter]
    fn category(&self) -> String {
        self.category.clone()
    }
    
    /// Event description (debug representation)
    #[getter]
    fn description(&self) -> String {
        self.description.clone()
    }
    
    /// Check if this is a trade event
    #[getter]
    fn is_trade(&self) -> bool {
        self.trade.is_some()
    }
    
    /// Get trade details if this is a Trade event
    ///
    /// Returns:
    ///     Trade object with full details, or None if not a trade event
    fn as_trade(&self) -> Option<Trade> {
        self.trade.as_ref().map(|t| Trade { inner: t.clone() })
    }
    
    fn __repr__(&self) -> String {
        if self.trade.is_some() {
            format!("StateEvent(category=Trade, is_trade=True)")
        } else {
            format!("StateEvent(category={})", self.category)
        }
    }
}

impl StateEvent {
    pub(crate) fn from_sdk_event(event: &sdk_state::StateEvents) -> Self {
        let (category, description, trade) = match event {
            sdk_state::StateEvents::Account(_) => ("Account".to_string(), format!("{:?}", event), None),
            sdk_state::StateEvents::Error(_) => ("Error".to_string(), format!("{:?}", event), None),
            sdk_state::StateEvents::Exchange(_) => ("Exchange".to_string(), format!("{:?}", event), None),
            sdk_state::StateEvents::Order(_) => ("Order".to_string(), format!("{:?}", event), None),
            sdk_state::StateEvents::Perpetual(_) => ("Perpetual".to_string(), format!("{:?}", event), None),
            sdk_state::StateEvents::Position(_) => ("Position".to_string(), format!("{:?}", event), None),
            sdk_state::StateEvents::Trade(t) => ("Trade".to_string(), format!("{:?}", event), Some(t.clone())),
        };
        Self { category, description, trade }
    }
}

/// Block of state events
///
/// State mutations produced after applying a block of raw events.
#[pyclass(name = "StateBlockEvents", module = "perpl_sdk", frozen)]
pub struct StateBlockEvents {
    pub(crate) inner: sdk_state::StateBlockEvents,
}

#[pymethods]
impl StateBlockEvents {
    /// State instant (block number and timestamp)
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// All state events in this block
    fn events(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for event_ctx in self.inner.events() {
            for event in event_ctx.event() {
                let event_obj = Bound::new(py, StateEvent::from_sdk_event(event))?;
                list.append(event_obj)?;
            }
        }
        Ok(list.unbind())
    }
    
    /// Number of events in this block
    fn len(&self) -> usize {
        self.inner.events().iter()
            .map(|ctx| ctx.event().len())
            .sum()
    }
    
    fn __repr__(&self) -> String {
        format!(
            "StateBlockEvents(block={}, events={})",
            self.inner.instant().block_number(),
            self.len()
        )
    }
    
    fn __len__(&self) -> usize {
        self.len()
    }
}

// Note: Full async streaming (EventStream) is not implemented yet as it requires
// complex Stream -> Python async iterator bridging. Users can implement their own
// event fetching using web3 libraries and then apply events via apply_events().
