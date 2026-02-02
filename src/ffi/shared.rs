//! Shared State Infrastructure
//!
//! This module provides zero-copy reference wrappers for efficient state access.
//! Instead of cloning the entire state tree for each Python object, we use
//! Arc<RwLock<Exchange>> to share a single source of truth.
//!
//! ## Design
//!
//! - `SharedExchange` wraps the SDK Exchange with interior mutability
//! - Child objects (Perpetual, Account, Position, Order) hold a reference to
//!   the shared exchange and only store their ID
//! - Accessors use closures to safely borrow the state
//!
//! ## Benefits
//!
//! - O(1) memory per Python wrapper object (just Arc clone + ID)
//! - Single source of truth for all state
//! - Automatic consistency across all views
//! - Lock-free reads with RwLock (multiple concurrent readers)

use std::sync::Arc;
use parking_lot::RwLock;
use dex_sdk::state as sdk_state;
use pyo3::prelude::*;
use pyo3::exceptions::PyKeyError;

/// Shared exchange state with interior mutability.
///
/// This is the single source of truth for all exchange state.
/// All child wrappers (Perpetual, Account, etc.) hold a clone of this Arc.
#[derive(Clone)]
pub struct SharedExchange(pub Arc<RwLock<sdk_state::Exchange>>);

impl SharedExchange {
    /// Create a new shared exchange from an owned SDK exchange.
    pub fn new(exchange: sdk_state::Exchange) -> Self {
        Self(Arc::new(RwLock::new(exchange)))
    }
    
    /// Execute a read-only operation on the exchange.
    ///
    /// Acquires a read lock, executes the closure, and releases the lock.
    /// Multiple readers can hold the lock simultaneously.
    #[inline]
    pub fn read<F, R>(&self, f: F) -> R 
    where 
        F: FnOnce(&sdk_state::Exchange) -> R 
    {
        f(&*self.0.read())
    }
    
    /// Execute a mutation operation on the exchange.
    ///
    /// Acquires an exclusive write lock, executes the closure, and releases the lock.
    #[inline]
    pub fn write<F, R>(&self, f: F) -> R 
    where 
        F: FnOnce(&mut sdk_state::Exchange) -> R 
    {
        f(&mut *self.0.write())
    }
    
    /// Get a perpetual by ID with a closure.
    ///
    /// Returns PyErr if perpetual not found.
    pub fn with_perpetual<F, R>(&self, perp_id: u32, f: F) -> PyResult<R>
    where
        F: FnOnce(&sdk_state::Perpetual) -> R
    {
        self.read(|exch| {
            exch.perpetuals()
                .get(&perp_id)
                .map(f)
                .ok_or_else(|| PyKeyError::new_err(format!("Perpetual {} not found", perp_id)))
        })
    }
    
    /// Get an account by ID with a closure.
    ///
    /// Returns PyErr if account not found.
    pub fn with_account<F, R>(&self, account_id: u32, f: F) -> PyResult<R>
    where
        F: FnOnce(&sdk_state::Account) -> R
    {
        self.read(|exch| {
            exch.accounts()
                .get(&account_id)
                .map(f)
                .ok_or_else(|| PyKeyError::new_err(format!("Account {} not found", account_id)))
        })
    }
    
    /// Get a position by account and perpetual ID with a closure.
    ///
    /// Returns PyErr if account or position not found.
    pub fn with_position<F, R>(&self, account_id: u32, perp_id: u32, f: F) -> PyResult<R>
    where
        F: FnOnce(&sdk_state::Position) -> R
    {
        self.read(|exch| {
            let account = exch.accounts()
                .get(&account_id)
                .ok_or_else(|| PyKeyError::new_err(format!("Account {} not found", account_id)))?;
            account.positions()
                .get(&perp_id)
                .map(f)
                .ok_or_else(|| PyKeyError::new_err(format!("Position for perp {} not found", perp_id)))
        })
    }
}

impl std::fmt::Debug for SharedExchange {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.read(|exch| {
            f.debug_struct("SharedExchange")
                .field("perpetuals", &exch.perpetuals().len())
                .field("accounts", &exch.accounts().len())
                .field("block", &exch.instant().block_number())
                .finish()
        })
    }
}
