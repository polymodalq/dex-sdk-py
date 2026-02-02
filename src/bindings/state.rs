//! State Management Bindings
//!
//! This module provides Python wrappers for the core state types:
//! - Exchange: Root state object
//! - Perpetual: Perpetual contract state
//! - Account: User account state
//! - Position: Trading position
//! - Order: Order book entry
//! - L2Book: Aggregated order book view
//!
//! ## Architecture
//!
//! The SDK uses an immutable snapshot model where Exchange owns all state.
//! For Python, we wrap the SDK types directly and provide dict-like access
//! to nested collections.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use dex_sdk::state as sdk_state;
use crate::ffi::numeric::{PyUD64, PyUD128, PyD256, PyConverter};
use crate::bindings::types::StateInstant;
use crate::bindings::chain::Chain;
use alloy::primitives::Address;
use std::collections::HashMap;
use std::num::NonZeroU16;
use fastnum::UD64;

// =============================================================================
// Exchange - Root State Object
// =============================================================================

/// Exchange state snapshot
///
/// This is the root object containing all tracked perpetual contracts and accounts.
/// It can be kept up-to-date by applying events from the blockchain.
///
/// Use `SnapshotBuilder` to create an Exchange snapshot.
#[pyclass(name = "Exchange", module = "perpl_sdk")]
pub struct Exchange {
    pub(crate) inner: sdk_state::Exchange,
}

#[pymethods]
impl Exchange {
    /// Revision of the exchange smart contract
    #[staticmethod]
    fn revision() -> &'static str {
        sdk_state::Exchange::revision()
    }
    
    /// Chain the snapshot was collected from
    #[getter]
    fn chain(&self) -> Chain {
        Chain(self.inner.chain().clone())
    }
    
    /// Instant the snapshot is consistent with or was last updated at
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// Converter for collateral token amounts
    #[getter]
    fn collateral_converter(&self) -> PyConverter {
        PyConverter(self.inner.collateral_converter())
    }
    
    /// Funding interval in blocks
    #[getter]
    fn funding_interval_blocks(&self) -> u32 {
        self.inner.funding_interval_blocks()
    }
    
    /// Minimal amount in collateral token that can be posted to the book
    #[getter]
    fn min_post(&self) -> PyUD128 {
        PyUD128(self.inner.min_post())
    }
    
    /// Minimal amount in collateral token that can be settled
    #[getter]
    fn min_settle(&self) -> PyUD128 {
        PyUD128(self.inner.min_settle())
    }
    
    /// Amount locked with each posted order for recycling
    #[getter]
    fn recycle_fee(&self) -> PyUD128 {
        PyUD128(self.inner.recycle_fee())
    }
    
    /// Indicates if exchange is halted
    #[getter]
    fn is_halted(&self) -> bool {
        self.inner.is_halted()
    }
    
    /// Get perpetual by ID
    ///
    /// Args:
    ///     perp_id: Perpetual contract ID
    ///
    /// Returns:
    ///     Perpetual or None if not found
    fn get_perpetual(&self, perp_id: u32) -> Option<Perpetual> {
        self.inner.perpetuals().get(&perp_id).map(|p| Perpetual {
            inner: p.clone(),
        })
    }
    
    /// Get all perpetual IDs
    ///
    /// Returns:
    ///     List of perpetual IDs
    fn perpetual_ids(&self) -> Vec<u32> {
        self.inner.perpetuals().keys().copied().collect()
    }
    
    /// Get all perpetuals
    ///
    /// Returns:
    ///     Dict mapping perpetual ID to Perpetual
    fn perpetuals(&self, py: Python) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new_bound(py);
        for (id, perp) in self.inner.perpetuals() {
            let perp_obj = Bound::new(py, Perpetual {
                inner: perp.clone(),
            })?;
            dict.set_item(id, perp_obj)?;
        }
        Ok(dict.unbind())
    }
    
    /// Get account by ID
    ///
    /// Args:
    ///     account_id: Account ID
    ///
    /// Returns:
    ///     Account or None if not found
    fn get_account(&self, account_id: u32) -> Option<Account> {
        self.inner.accounts().get(&account_id).map(|a| Account {
            inner: a.clone(),
        })
    }
    
    /// Get all account IDs
    ///
    /// Returns:
    ///     List of account IDs
    fn account_ids(&self) -> Vec<u32> {
        self.inner.accounts().keys().copied().collect()
    }
    
    /// Get all accounts
    ///
    /// Returns:
    ///     Dict mapping account ID to Account
    fn accounts(&self, py: Python) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new_bound(py);
        for (id, account) in self.inner.accounts() {
            let account_obj = Bound::new(py, Account {
                inner: account.clone(),
            })?;
            dict.set_item(id, account_obj)?;
        }
        Ok(dict.unbind())
    }
    
    /// Apply raw blockchain events to update the exchange state
    ///
    /// This method updates the exchange state by processing a block of raw events.
    /// Events must be applied in order, and duplicate blocks are ignored.
    ///
    /// Args:
    ///     events: RawBlockEvents from the blockchain
    ///
    /// Returns:
    ///     StateBlockEvents with the processed state mutations, or None if block was already applied
    ///
    /// Raises:
    ///     DexError: If events are out of order or processing fails
    ///
    /// Example:
    ///     ```python
    ///     # Fetch events from blockchain
    ///     raw_events = ... # Get RawBlockEvents
    ///     
    ///     # Apply to exchange
    ///     state_events = exchange.apply_events(raw_events)
    ///     if state_events:
    ///         print(f"Applied {len(state_events)} state mutations")
    ///     ```
    fn apply_events(&mut self, events: &crate::bindings::stream::RawBlockEvents) -> PyResult<Option<crate::bindings::stream::StateBlockEvents>> {
        use crate::ffi::error::to_py_err;
        
        let result = self.inner.apply_events(&events.inner)
            .map_err(|e| to_py_err(format!("{}", e)))?;
        
        Ok(result.map(|inner| crate::bindings::stream::StateBlockEvents { inner }))
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Exchange(perpetuals={}, accounts={}, block={})",
            self.inner.perpetuals().len(),
            self.inner.accounts().len(),
            self.inner.instant().block_number()
        )
    }
}

// =============================================================================
// Perpetual - Perpetual Contract State
// =============================================================================

/// Perpetual contract state
///
/// Provides access to contract configuration, market data, and order book.
#[pyclass(name = "Perpetual", module = "perpl_sdk", frozen)]
#[derive(Clone)]
pub struct Perpetual {
    pub(crate) inner: sdk_state::Perpetual,
}

#[pymethods]
impl Perpetual {
    /// Instant the perpetual state is consistent with
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// Perpetual contract ID
    #[getter]
    fn id(&self) -> u32 {
        self.inner.id()
    }
    
    /// Contract name
    #[getter]
    fn name(&self) -> String {
        self.inner.name()
    }
    
    /// Contract symbol
    #[getter]
    fn symbol(&self) -> String {
        self.inner.symbol()
    }
    
    /// Indicates if the contract is paused
    #[getter]
    fn is_paused(&self) -> bool {
        self.inner.is_paused()
    }
    
    /// Price converter for this perpetual
    #[getter]
    fn price_converter(&self) -> PyConverter {
        PyConverter(self.inner.price_converter())
    }
    
    /// Size converter for this perpetual
    #[getter]
    fn size_converter(&self) -> PyConverter {
        PyConverter(self.inner.size_converter())
    }
    
    /// Leverage converter for this perpetual
    #[getter]
    fn leverage_converter(&self) -> PyConverter {
        PyConverter(self.inner.leverage_converter())
    }
    
    /// Fee converter for this perpetual
    #[getter]
    fn fee_converter(&self) -> PyConverter {
        PyConverter(self.inner.fee_converter())
    }
    
    /// Funding rate converter for this perpetual
    #[getter]
    fn funding_rate_converter(&self) -> PyConverter {
        PyConverter(self.inner.funding_rate_converter())
    }
    
    /// Maker fee
    #[getter]
    fn maker_fee(&self) -> PyUD64 {
        PyUD64(self.inner.maker_fee())
    }
    
    /// Taker fee
    #[getter]
    fn taker_fee(&self) -> PyUD64 {
        PyUD64(self.inner.taker_fee())
    }
    
    /// Initial margin requirement
    #[getter]
    fn initial_margin(&self) -> PyUD64 {
        PyUD64(self.inner.initial_margin())
    }
    
    /// Maintenance margin requirement
    #[getter]
    fn maintenance_margin(&self) -> PyUD64 {
        PyUD64(self.inner.maintenance_margin())
    }
    
    /// Last traded price
    #[getter]
    fn last_price(&self) -> PyUD64 {
        PyUD64(self.inner.last_price())
    }
    
    /// Instant the last trade was executed at
    ///
    /// Block number is available only from real-time events, not from initial snapshot.
    #[getter]
    fn last_price_instant(&self) -> StateInstant {
        StateInstant(self.inner.last_price_instant())
    }
    
    /// Unix timestamp (in seconds) of the last trade
    #[getter]
    fn last_price_timestamp(&self) -> u64 {
        self.inner.last_price_timestamp()
    }
    
    /// Mark price (used for liquidations)
    #[getter]
    fn mark_price(&self) -> PyUD64 {
        PyUD64(self.inner.mark_price())
    }
    
    /// Instant the mark price was updated at
    ///
    /// Block number is available only from real-time events, not from initial snapshot.
    #[getter]
    fn mark_price_instant(&self) -> StateInstant {
        StateInstant(self.inner.mark_price_instant())
    }
    
    /// Unix timestamp (in seconds) of the most recent mark price update
    #[getter]
    fn mark_price_timestamp(&self) -> u64 {
        self.inner.mark_price_timestamp()
    }
    
    /// Indicates that the mark price is obsolete and will not be accepted
    /// during order/position settlement
    #[getter]
    fn is_mark_price_obsolete(&self) -> bool {
        self.inner.is_mark_price_obsolete()
    }
    
    /// Oracle price
    #[getter]
    fn oracle_price(&self) -> PyUD64 {
        PyUD64(self.inner.oracle_price())
    }
    
    /// Instant the oracle price was updated at
    ///
    /// Block number is available only from real-time events, not from initial snapshot.
    #[getter]
    fn oracle_price_instant(&self) -> StateInstant {
        StateInstant(self.inner.oracle_price_instant())
    }
    
    /// Unix timestamp (in seconds) of the most recent oracle price update
    #[getter]
    fn oracle_price_timestamp(&self) -> u64 {
        self.inner.oracle_price_timestamp()
    }
    
    /// Indicates that the oracle price is obsolete and will not be accepted
    /// during order/position settlement
    #[getter]
    fn is_oracle_price_obsolete(&self) -> bool {
        self.inner.is_oracle_price_obsolete()
    }
    
    /// Feed ID of ChainLink DataStreams price oracle (hex string)
    #[getter]
    fn oracle_feed_id(&self) -> String {
        format!("{:?}", self.inner.oracle_feed_id())
    }
    
    /// If perpetual contract relies on oracle prices
    #[getter]
    fn is_oracle_used(&self) -> bool {
        self.inner.is_oracle_used()
    }
    
    /// Max age in seconds for oracle/mark prices
    #[getter]
    fn price_max_age_sec(&self) -> u64 {
        self.inner.price_max_age_sec()
    }
    
    /// Open interest size
    #[getter]
    fn open_interest(&self) -> PyUD128 {
        PyUD128(self.inner.open_interest())
    }
    
    /// Open interest amount (size * last_price)
    #[getter]
    fn open_interest_amount(&self) -> PyUD128 {
        PyUD128(self.inner.open_interest_amount())
    }
    
    /// Current funding rate
    #[getter]
    fn funding_rate(&self) -> PyD256 {
        PyD256(self.inner.funding_rate().resize())
    }
    
    /// If the next funding rate has been set (and is scheduled for a future block)
    #[getter]
    fn has_next_funding_rate(&self) -> bool {
        self.inner.has_next_funding_rate()
    }
    
    /// Block number when the next funding event is scheduled
    #[getter]
    fn next_funding_event_block(&self) -> Option<u64> {
        self.inner.next_funding_event_block()
    }
    
    /// Starting block number of funding intervals
    #[getter]
    fn funding_start_block(&self) -> u64 {
        self.inner.funding_start_block()
    }
    
    /// Get order by ID
    ///
    /// Args:
    ///     order_id: Order ID (must be > 0)
    ///
    /// Returns:
    ///     Order or None if not found
    fn get_order(&self, order_id: u16) -> Option<Order> {
        NonZeroU16::new(order_id).and_then(|id| {
            self.inner.get_order(id).map(|o| Order {
                inner: *o,
            })
        })
    }
    
    /// Get all order IDs
    ///
    /// Returns:
    ///     List of order IDs
    fn order_ids(&self) -> Vec<u16> {
        self.inner.l3_book().all_orders()
            .keys()
            .map(|id| id.get())
            .collect()
    }
    
    /// Get all orders
    ///
    /// Returns:
    ///     Dict mapping order ID to Order
    fn orders(&self, py: Python) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new_bound(py);
        for (id, order) in self.inner.l3_book().all_orders() {
            let order_obj = Bound::new(py, Order {
                inner: **order,
            })?;
            dict.set_item(id.get(), order_obj)?;
        }
        Ok(dict.unbind())
    }
    
    /// Total number of orders in the book
    #[getter]
    fn total_orders(&self) -> usize {
        self.inner.total_orders()
    }
    
    /// Get L2 order book (aggregated by price level)
    ///
    /// Returns:
    ///     L2Book with aggregated bid/ask levels
    fn l2_book(&self) -> L2Book {
        L2Book::from_order_book(self.inner.l3_book())
    }
    
    /// Get order by client order ID (O(1) lookup)
    ///
    /// Args:
    ///     account_id: Account ID that placed the order
    ///     client_id: Client order ID (original request_id when order was placed)
    ///
    /// Returns:
    ///     Order or None if not found
    fn get_order_by_client_id(&self, account_id: u32, client_id: u64) -> Option<Order> {
        self.inner.l3_book()
            .get_order_by_client_id(account_id, client_id)
            .map(|o| Order { inner: **o })
    }
    
    /// Calculate ask side market impact for a given size
    ///
    /// Returns the worst price, fillable size, and volume-weighted average price
    /// if the given size were to be executed against the ask side of the book.
    ///
    /// Args:
    ///     size: Size to calculate impact for
    ///
    /// Returns:
    ///     Tuple of (worst_price, fillable_size, avg_price) or None if book is empty
    fn ask_impact(&self, size: &PyUD64) -> Option<(PyUD64, PyUD64, PyUD64)> {
        self.inner.l3_book().ask_impact(size.0)
            .map(|(price, filled, avg)| (PyUD64(price), PyUD64(filled), PyUD64(avg)))
    }
    
    /// Calculate bid side market impact for a given size
    ///
    /// Returns the worst price, fillable size, and volume-weighted average price
    /// if the given size were to be executed against the bid side of the book.
    ///
    /// Args:
    ///     size: Size to calculate impact for
    ///
    /// Returns:
    ///     Tuple of (worst_price, fillable_size, avg_price) or None if book is empty
    fn bid_impact(&self, size: &PyUD64) -> Option<(PyUD64, PyUD64, PyUD64)> {
        self.inner.l3_book().bid_impact(size.0)
            .map(|(price, filled, avg)| (PyUD64(price), PyUD64(filled), PyUD64(avg)))
    }
    
    /// Get all ask orders in price-time priority order (L3 view)
    ///
    /// Returns orders sorted by price ascending (best ask first), then by
    /// time priority (FIFO) within each price level.
    ///
    /// Returns:
    ///     List of Order objects sorted by price-time priority
    fn ask_orders(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for order in self.inner.l3_book().ask_orders() {
            let order_obj = Bound::new(py, Order { inner: **order })?;
            list.append(order_obj)?;
        }
        Ok(list.unbind())
    }
    
    /// Get all bid orders in price-time priority order (L3 view)
    ///
    /// Returns orders sorted by price descending (best bid first), then by
    /// time priority (FIFO) within each price level.
    ///
    /// Returns:
    ///     List of Order objects sorted by price-time priority
    fn bid_orders(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for order in self.inner.l3_book().bid_orders() {
            let order_obj = Bound::new(py, Order { inner: **order })?;
            list.append(order_obj)?;
        }
        Ok(list.unbind())
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Perpetual(id={}, symbol='{}', mark_price={})",
            self.inner.id(),
            self.inner.symbol(),
            self.inner.mark_price()
        )
    }
}

// =============================================================================
// Account - User Account State
// =============================================================================

/// Exchange account state
///
/// Contains balance, locked balance, and positions for a user.
#[pyclass(name = "Account", module = "perpl_sdk", frozen)]
#[derive(Clone)]
pub struct Account {
    pub(crate) inner: sdk_state::Account,
}

#[pymethods]
impl Account {
    /// Instant the account state is consistent with
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// Account ID
    #[getter]
    fn id(&self) -> u32 {
        self.inner.id()
    }
    
    /// Account address
    #[getter]
    fn address(&self) -> String {
        format!("{:?}", self.inner.address())
    }
    
    /// Current balance of collateral tokens
    #[getter]
    fn balance(&self) -> PyUD128 {
        PyUD128(self.inner.balance())
    }
    
    /// Balance locked by existing orders
    #[getter]
    fn locked_balance(&self) -> PyUD128 {
        PyUD128(self.inner.locked_balance())
    }
    
    /// Balance available for trading (balance - locked_balance)
    ///
    /// This is the amount that can be used for new orders.
    #[getter]
    fn available_balance(&self) -> PyUD128 {
        PyUD128(self.inner.available_balance())
    }
    
    /// Total unrealized PnL of all positions
    ///
    /// Sum of PnL from all open positions in the account.
    #[getter]
    fn unrealized_pnl(&self) -> PyD256 {
        PyD256(self.inner.unrealized_pnl())
    }
    
    /// Indicates if the account is frozen
    #[getter]
    fn frozen(&self) -> bool {
        self.inner.frozen()
    }
    
    /// Get position for a perpetual
    ///
    /// Args:
    ///     perpetual_id: Perpetual contract ID
    ///
    /// Returns:
    ///     Position or None if no position exists
    fn get_position(&self, perpetual_id: u32) -> Option<Position> {
        self.inner.positions().get(&perpetual_id).map(|p| Position {
            inner: p.clone(),
        })
    }
    
    /// Get all perpetual IDs with positions
    ///
    /// Returns:
    ///     List of perpetual IDs
    fn position_perpetual_ids(&self) -> Vec<u32> {
        self.inner.positions().keys().copied().collect()
    }
    
    /// Get all positions
    ///
    /// Returns:
    ///     Dict mapping perpetual ID to Position
    fn positions(&self, py: Python) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new_bound(py);
        for (perp_id, position) in self.inner.positions() {
            let pos_obj = Bound::new(py, Position {
                inner: position.clone(),
            })?;
            dict.set_item(perp_id, pos_obj)?;
        }
        Ok(dict.unbind())
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Account(id={}, balance={}, positions={})",
            self.inner.id(),
            self.inner.balance(),
            self.inner.positions().len()
        )
    }
}

// =============================================================================
// Position - Trading Position
// =============================================================================

/// Trading position in a perpetual contract
#[pyclass(name = "Position", module = "perpl_sdk", frozen)]
#[derive(Clone)]
pub struct Position {
    pub(crate) inner: sdk_state::Position,
}

#[pymethods]
impl Position {
    /// Instant the position state is consistent with
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// Perpetual contract ID
    #[getter]
    fn perpetual_id(&self) -> u32 {
        self.inner.perpetual_id()
    }
    
    /// Account ID
    #[getter]
    fn account_id(&self) -> u32 {
        self.inner.account_id()
    }
    
    /// Position size
    #[getter]
    fn size(&self) -> PyUD64 {
        PyUD64(self.inner.size())
    }
    
    /// Collateral deposit/margin locked in the position
    #[getter]
    fn deposit(&self) -> PyUD128 {
        PyUD128(self.inner.deposit())
    }
    
    /// Entry price
    #[getter]
    fn entry_price(&self) -> PyUD64 {
        PyUD64(self.inner.entry_price())
    }
    
    /// Position type (Long or Short)
    #[getter]
    fn r#type(&self) -> String {
        format!("{:?}", self.inner.r#type())
    }
    
    /// Unrealized Delta PnL
    #[getter]
    fn delta_pnl(&self) -> PyD256 {
        PyD256(self.inner.delta_pnl())
    }
    
    /// Unrealized Premium PnL
    #[getter]
    fn premium_pnl(&self) -> PyD256 {
        PyD256(self.inner.premium_pnl())
    }
    
    /// Total unrealized PnL
    #[getter]
    fn pnl(&self) -> PyD256 {
        PyD256(self.inner.pnl())
    }
    
    /// Liquidation price of the position
    ///
    /// Price at which the position would be liquidated.
    #[getter]
    fn liquidation_price(&self) -> PyUD64 {
        PyUD64(self.inner.liquidation_price())
    }
    
    /// Bankruptcy price of the position
    ///
    /// Price at which the position would have zero equity.
    #[getter]
    fn bankruptcy_price(&self) -> PyUD64 {
        PyUD64(self.inner.bankruptcy_price())
    }
    
    /// Maintenance margin requirement
    ///
    /// The minimum margin required to keep the position open.
    #[getter]
    fn maintenance_margin_requirement(&self) -> PyUD128 {
        PyUD128(self.inner.maintenance_margin_requirement())
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Position(perp={}, size={}, deposit={}, entry_price={}, pnl={}, liq_price={})",
            self.inner.perpetual_id(),
            self.inner.size(),
            self.inner.deposit(),
            self.inner.entry_price(),
            self.inner.pnl(),
            self.inner.liquidation_price()
        )
    }
}

// =============================================================================
// Order - Order Book Entry
// =============================================================================

/// Order in the order book
#[pyclass(name = "Order", module = "perpl_sdk", frozen)]
#[derive(Clone, Copy)]
pub struct Order {
    pub(crate) inner: sdk_state::Order,
}

#[pymethods]
impl Order {
    /// Instant the order state is consistent with
    #[getter]
    fn instant(&self) -> StateInstant {
        StateInstant(self.inner.instant())
    }
    
    /// Order ID
    #[getter]
    fn order_id(&self) -> u16 {
        self.inner.order_id().get()
    }
    
    /// Account ID that placed the order
    #[getter]
    fn account_id(&self) -> u32 {
        self.inner.account_id()
    }
    
    /// Order price
    #[getter]
    fn price(&self) -> PyUD64 {
        PyUD64(self.inner.price())
    }
    
    /// Order size
    #[getter]
    fn size(&self) -> PyUD64 {
        PyUD64(self.inner.size())
    }
    
    /// Leverage
    #[getter]
    fn leverage(&self) -> PyUD64 {
        PyUD64(self.inner.leverage())
    }
    
    /// Expiry block
    #[getter]
    fn expiry_block(&self) -> u64 {
        self.inner.expiry_block()
    }
    
    /// Order type
    #[getter]
    fn r#type(&self) -> String {
        format!("{:?}", self.inner.r#type())
    }
    
    /// Request ID (available only from events, not snapshot)
    #[getter]
    fn request_id(&self) -> Option<u64> {
        self.inner.request_id()
    }
    
    /// Post-only flag (available only from events, not snapshot)
    #[getter]
    fn post_only(&self) -> Option<bool> {
        self.inner.post_only()
    }
    
    /// Fill-or-kill flag (available only from events, not snapshot)
    #[getter]
    fn fill_or_kill(&self) -> Option<bool> {
        self.inner.fill_or_kill()
    }
    
    /// Immediate-or-cancel flag (available only from events, not snapshot)
    #[getter]
    fn immediate_or_cancel(&self) -> Option<bool> {
        self.inner.immediate_or_cancel()
    }
    
    /// Client order ID - ID of the request this order was placed by
    ///
    /// Available only from real-time events, not from the initial snapshot.
    #[getter]
    fn client_order_id(&self) -> Option<u64> {
        self.inner.client_order_id()
    }
    
    /// Size of the order when it was placed
    ///
    /// Available only from real-time events, not from the initial snapshot.
    #[getter]
    fn placed_size(&self) -> Option<PyUD64> {
        self.inner.placed_size().map(PyUD64)
    }
    
    /// Size that has been filled (placed_size - current_size)
    ///
    /// Available only from real-time events, not from the initial snapshot.
    #[getter]
    fn filled_size(&self) -> Option<PyUD64> {
        self.inner.filled_size().map(PyUD64)
    }
    
    /// Check if the order is expired
    ///
    /// Valid only after the end of expiry block processing.
    #[getter]
    fn is_expired(&self) -> bool {
        self.inner.is_expired()
    }
    
    /// Previous order ID in the FIFO queue at this price level
    ///
    /// Available from snapshot, None for newly placed orders or if this is the first order.
    #[getter]
    fn prev_order_id(&self) -> Option<u16> {
        self.inner.prev_order_id().map(|id| id.get())
    }
    
    /// Next order ID in the FIFO queue at this price level
    ///
    /// Available from snapshot, None for newly placed orders or if this is the last order.
    #[getter]
    fn next_order_id(&self) -> Option<u16> {
        self.inner.next_order_id().map(|id| id.get())
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Order(id={}, type={}, price={}, size={})",
            self.inner.order_id(),
            format!("{:?}", self.inner.r#type()),
            self.inner.price(),
            self.inner.size()
        )
    }
}

// =============================================================================
// L2Book - Level 2 Order Book (Aggregated View)
// =============================================================================

/// Level 2 order book (aggregated by price level)
///
/// This is a snapshot view of the order book with prices aggregated at each level.
/// Bids are sorted best (highest) to worst (lowest).
/// Asks are sorted best (lowest) to worst (highest).
#[pyclass(name = "L2Book", module = "perpl_sdk", frozen)]
#[derive(Clone)]
pub struct L2Book {
    /// Bid levels: (price, size) sorted by price descending (best first)
    bids_vec: Vec<(UD64, UD64)>,
    /// Ask levels: (price, size) sorted by price ascending (best first)
    asks_vec: Vec<(UD64, UD64)>,
}

impl L2Book {
    /// Create an L2Book from the underlying L3 OrderBook
    pub fn from_order_book(book: &sdk_state::OrderBook) -> Self {
        // Extract bids sorted by price descending (best bid first)
        let bids_vec: Vec<(UD64, UD64)> = book.bids()
            .iter()
            .filter(|(_, level)| level.size() > UD64::ZERO)
            .map(|(rev_price, level)| (rev_price.0, level.size()))
            .collect();
        
        // Extract asks sorted by price ascending (best ask first)
        let asks_vec: Vec<(UD64, UD64)> = book.asks()
            .iter()
            .filter(|(_, level)| level.size() > UD64::ZERO)
            .map(|(price, level)| (*price, level.size()))
            .collect();
        
        Self { bids_vec, asks_vec }
    }
}

#[pymethods]
impl L2Book {
    /// Get bid side of the book
    ///
    /// Returns:
    ///     List of (price, size) tuples, sorted best (highest price) to worst
    fn bids(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for (price, size) in &self.bids_vec {
            let tuple: PyObject = (PyUD64(*price), PyUD64(*size)).into_py(py);
            list.append(tuple)?;
        }
        Ok(list.unbind())
    }
    
    /// Get ask side of the book
    ///
    /// Returns:
    ///     List of (price, size) tuples, sorted best (lowest price) to worst
    fn asks(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for (price, size) in &self.asks_vec {
            let tuple: PyObject = (PyUD64(*price), PyUD64(*size)).into_py(py);
            list.append(tuple)?;
        }
        Ok(list.unbind())
    }
    
    /// Get best bid (price, size)
    ///
    /// Returns:
    ///     Tuple of (price, size) or None if no bids
    fn best_bid(&self, py: Python) -> Option<PyObject> {
        self.bids_vec.first().map(|(price, size)| {
            (PyUD64(*price), PyUD64(*size)).into_py(py)
        })
    }
    
    /// Get best ask (price, size)
    ///
    /// Returns:
    ///     Tuple of (price, size) or None if no asks
    fn best_ask(&self, py: Python) -> Option<PyObject> {
        self.asks_vec.first().map(|(price, size)| {
            (PyUD64(*price), PyUD64(*size)).into_py(py)
        })
    }
    
    /// Get the spread (best_ask - best_bid)
    ///
    /// Returns:
    ///     Spread as UD64 or None if either side is empty
    fn spread(&self) -> Option<PyUD64> {
        match (self.asks_vec.first(), self.bids_vec.first()) {
            (Some((ask, _)), Some((bid, _))) if *ask > *bid => {
                Some(PyUD64(*ask - *bid))
            },
            _ => None,
        }
    }
    
    /// Get the mid price ((best_ask + best_bid) / 2)
    ///
    /// Returns:
    ///     Mid price as UD64 or None if either side is empty
    fn mid_price(&self) -> Option<PyUD64> {
        match (self.asks_vec.first(), self.bids_vec.first()) {
            (Some((ask, _)), Some((bid, _))) => {
                Some(PyUD64((*ask + *bid) / fastnum::udec64!(2)))
            },
            _ => None,
        }
    }
    
    /// Number of bid levels
    fn num_bid_levels(&self) -> usize {
        self.bids_vec.len()
    }
    
    /// Number of ask levels
    fn num_ask_levels(&self) -> usize {
        self.asks_vec.len()
    }
    
    fn __repr__(&self) -> String {
        let spread = self.spread().map(|s| format!("{}", s.0)).unwrap_or_else(|| "N/A".to_string());
        format!(
            "L2Book(bids={}, asks={}, spread={})",
            self.bids_vec.len(),
            self.asks_vec.len(),
            spread
        )
    }
}
