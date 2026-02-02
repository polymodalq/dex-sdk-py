//! Core Type System
//!
//! Fundamental types and enums from `dex_sdk::types`, maintaining exact semantics.

use pyo3::prelude::*;
use pyo3::types::PyList;
use dex_sdk::types as sdk_types;
use crate::ffi::numeric::{PyUD64, PyUD128};

// =============================================================================
// StateInstant - Block and timestamp marker
// =============================================================================

/// Instant in chain history
///
/// Immutable marker for state consistency. Matches `dex_sdk::types::StateInstant`.
#[pyclass(name = "StateInstant", module = "perpl_sdk")]
#[derive(Clone, Copy, Debug)]
pub struct StateInstant(pub sdk_types::StateInstant);

#[pymethods]
impl StateInstant {
    // Note: StateInstant::new is pub(crate) in the SDK, so we can't expose it
    // Users will receive StateInstant from SDK methods, not construct it directly
    
    #[getter]
    fn block_number(&self) -> u64 {
        self.0.block_number()
    }
    
    #[getter]
    fn block_timestamp(&self) -> u64 {
        self.0.block_timestamp()
    }
    
    fn __repr__(&self) -> String {
        format!(
            "StateInstant(block_number={}, block_timestamp={})",
            self.0.block_number(),
            self.0.block_timestamp()
        )
    }
    
    fn __str__(&self) -> String {
        format!("Block {} @ {}", self.0.block_number(), self.0.block_timestamp())
    }
    
    fn __richcmp__(&self, other: &Self, op: pyo3::basic::CompareOp) -> bool {
        match op {
            pyo3::basic::CompareOp::Lt => self.0 < other.0,
            pyo3::basic::CompareOp::Le => self.0 <= other.0,
            pyo3::basic::CompareOp::Eq => self.0 == other.0,
            pyo3::basic::CompareOp::Ne => self.0 != other.0,
            pyo3::basic::CompareOp::Gt => self.0 > other.0,
            pyo3::basic::CompareOp::Ge => self.0 >= other.0,
        }
    }
    
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        self.0.block_number().hash(&mut hasher);
        self.0.block_timestamp().hash(&mut hasher);
        hasher.finish()
    }
}

impl From<sdk_types::StateInstant> for StateInstant {
    fn from(value: sdk_types::StateInstant) -> Self {
        Self(value)
    }
}

impl From<StateInstant> for sdk_types::StateInstant {
    fn from(value: StateInstant) -> Self {
        value.0
    }
}

// =============================================================================
// OrderType - Order classification
// =============================================================================

/// Type of order placed on the book
///
/// Matches `dex_sdk::types::OrderType` exactly.
#[pyclass(name = "OrderType", module = "perpl_sdk.types")]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum OrderType {
    /// Open long position (or decrease/close/invert short)
    OpenLong,
    /// Open short position (or decrease/close/invert long)
    OpenShort,
    /// Close long position (reduce-only)
    CloseLong,
    /// Close short position (reduce-only)
    CloseShort,
}

#[pymethods]
impl OrderType {
    fn side(&self) -> OrderSide {
        match sdk_types::OrderType::from(*self as u8).side() {
            sdk_types::OrderSide::Bid => OrderSide::Bid,
            sdk_types::OrderSide::Ask => OrderSide::Ask,
        }
    }
    
    fn __repr__(&self) -> &'static str {
        match self {
            Self::OpenLong => "OrderType.OpenLong",
            Self::OpenShort => "OrderType.OpenShort",
            Self::CloseLong => "OrderType.CloseLong",
            Self::CloseShort => "OrderType.CloseShort",
        }
    }
    
    fn __str__(&self) -> &'static str {
        match self {
            Self::OpenLong => "OpenLong",
            Self::OpenShort => "OpenShort",
            Self::CloseLong => "CloseLong",
            Self::CloseShort => "CloseShort",
        }
    }
}

impl From<sdk_types::OrderType> for OrderType {
    fn from(value: sdk_types::OrderType) -> Self {
        match value {
            sdk_types::OrderType::OpenLong => Self::OpenLong,
            sdk_types::OrderType::OpenShort => Self::OpenShort,
            sdk_types::OrderType::CloseLong => Self::CloseLong,
            sdk_types::OrderType::CloseShort => Self::CloseShort,
        }
    }
}

impl From<OrderType> for sdk_types::OrderType {
    fn from(value: OrderType) -> Self {
        match value {
            OrderType::OpenLong => Self::OpenLong,
            OrderType::OpenShort => Self::OpenShort,
            OrderType::CloseLong => Self::CloseLong,
            OrderType::CloseShort => Self::CloseShort,
        }
    }
}

// =============================================================================
// OrderSide - Bid or Ask
// =============================================================================

/// Side of the order book
#[pyclass(name = "OrderSide", module = "perpl_sdk.types")]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum OrderSide {
    Ask,
    Bid,
}

#[pymethods]
impl OrderSide {
    fn __repr__(&self) -> &'static str {
        match self {
            Self::Ask => "OrderSide.Ask",
            Self::Bid => "OrderSide.Bid",
        }
    }
    
    fn __str__(&self) -> &'static str {
        match self {
            Self::Ask => "Ask",
            Self::Bid => "Bid",
        }
    }
}

// =============================================================================
// PositionType - Long or Short
// =============================================================================

/// Type of position held
#[pyclass(name = "PositionType", module = "perpl_sdk.types")]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum PositionType {
    Long,
    Short,
}

#[pymethods]
impl PositionType {
    fn is_long(&self) -> bool {
        matches!(self, Self::Long)
    }
    
    fn is_short(&self) -> bool {
        matches!(self, Self::Short)
    }
    
    fn __repr__(&self) -> &'static str {
        match self {
            Self::Long => "PositionType.Long",
            Self::Short => "PositionType.Short",
        }
    }
    
    fn __str__(&self) -> &'static str {
        match self {
            Self::Long => "Long",
            Self::Short => "Short",
        }
    }
}

impl From<dex_sdk::state::PositionType> for PositionType {
    fn from(value: dex_sdk::state::PositionType) -> Self {
        match value {
            dex_sdk::state::PositionType::Long => Self::Long,
            dex_sdk::state::PositionType::Short => Self::Short,
        }
    }
}

// =============================================================================
// RequestType - Operation type for OrderRequest
// =============================================================================

/// Type of order request operation
#[pyclass(name = "RequestType", module = "perpl_sdk.types")]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum RequestType {
    OpenLong,
    OpenShort,
    CloseLong,
    CloseShort,
    Cancel,
    IncreasePositionCollateral,
    Change,
}

#[pymethods]
impl RequestType {
    /// Returns the order side for this request type, if applicable.
    ///
    /// Returns `Some(side)` for order-placing types (OpenLong, OpenShort,
    /// CloseLong, CloseShort). Returns `None` for Cancel,
    /// IncreasePositionCollateral, and Change.
    ///
    /// Returns:
    ///     OrderSide.Bid for buy orders (OpenLong, CloseShort)
    ///     OrderSide.Ask for sell orders (OpenShort, CloseLong)
    ///     None for non-order operations
    fn try_side(&self) -> Option<OrderSide> {
        let sdk_type: sdk_types::RequestType = (*self).into();
        sdk_type.try_side().map(|side| match side {
            sdk_types::OrderSide::Bid => OrderSide::Bid,
            sdk_types::OrderSide::Ask => OrderSide::Ask,
        })
    }
    
    fn __repr__(&self) -> &'static str {
        match self {
            Self::OpenLong => "RequestType.OpenLong",
            Self::OpenShort => "RequestType.OpenShort",
            Self::CloseLong => "RequestType.CloseLong",
            Self::CloseShort => "RequestType.CloseShort",
            Self::Cancel => "RequestType.Cancel",
            Self::IncreasePositionCollateral => "RequestType.IncreasePositionCollateral",
            Self::Change => "RequestType.Change",
        }
    }
}

impl From<sdk_types::RequestType> for RequestType {
    fn from(value: sdk_types::RequestType) -> Self {
        match value {
            sdk_types::RequestType::OpenLong => Self::OpenLong,
            sdk_types::RequestType::OpenShort => Self::OpenShort,
            sdk_types::RequestType::CloseLong => Self::CloseLong,
            sdk_types::RequestType::CloseShort => Self::CloseShort,
            sdk_types::RequestType::Cancel => Self::Cancel,
            sdk_types::RequestType::IncreasePositionCollateral => Self::IncreasePositionCollateral,
            sdk_types::RequestType::Change => Self::Change,
        }
    }
}

impl From<RequestType> for sdk_types::RequestType {
    fn from(value: RequestType) -> Self {
        match value {
            RequestType::OpenLong => Self::OpenLong,
            RequestType::OpenShort => Self::OpenShort,
            RequestType::CloseLong => Self::CloseLong,
            RequestType::CloseShort => Self::CloseShort,
            RequestType::Cancel => Self::Cancel,
            RequestType::IncreasePositionCollateral => Self::IncreasePositionCollateral,
            RequestType::Change => Self::Change,
        }
    }
}

// =============================================================================
// OrderRequest - Order submission builder
// =============================================================================

/// Request to post/modify an order
///
/// Matches `dex_sdk::types::OrderRequest` exactly.
#[pyclass(name = "OrderRequest", module = "perpl_sdk.types")]
#[derive(Clone)]
pub struct OrderRequest {
    pub(crate) inner: sdk_types::OrderRequest,
}

#[pymethods]
impl OrderRequest {
    #[new]
    #[pyo3(signature = (
        request_id,
        perp_id,
        r#type,
        order_id,
        price,
        size,
        expiry_block,
        post_only,
        fill_or_kill,
        immediate_or_cancel,
        max_matches,
        leverage,
        last_exec_block,
        amount,
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        request_id: u64,
        perp_id: u32,
        r#type: RequestType,
        order_id: Option<u16>,
        price: &PyUD64,
        size: &PyUD64,
        expiry_block: Option<u64>,
        post_only: bool,
        fill_or_kill: bool,
        immediate_or_cancel: bool,
        max_matches: Option<u32>,
        leverage: &PyUD64,
        last_exec_block: Option<u64>,
        amount: Option<&PyUD128>,
    ) -> Self {
        // Convert u16 to NonZeroU16 for order_id
        let order_id_nz = order_id.and_then(std::num::NonZeroU16::new);
        
        Self {
            inner: sdk_types::OrderRequest::new(
                request_id,
                perp_id,
                r#type.into(),
                order_id_nz,
                price.0,
                size.0,
                expiry_block,
                post_only,
                fill_or_kill,
                immediate_or_cancel,
                max_matches,
                leverage.0,
                last_exec_block,
                amount.map(|a| a.0),
            ),
        }
    }
    
    fn __repr__(&self) -> String {
        format!("OrderRequest(perp_id={}, type={:?})", 
            0,  // We don't have a getter for perp_id currently
            "..."
        )
    }
    
    // ==========================================================================
    // Convenience Builder Methods
    // ==========================================================================
    
    /// Create an open long order request
    ///
    /// Args:
    ///     request_id: Unique request ID for tracking
    ///     perp_id: Perpetual contract ID
    ///     price: Order price
    ///     size: Order size
    ///     leverage: Position leverage
    ///     post_only: If True, order will only be placed if it doesn't match
    ///     expiry_blocks: Optional number of blocks until expiry
    ///
    /// Returns:
    ///     OrderRequest for opening a long position
    #[staticmethod]
    #[pyo3(signature = (request_id, perp_id, price, size, leverage, post_only=false, expiry_blocks=None))]
    fn open_long(
        request_id: u64,
        perp_id: u32,
        price: &PyUD64,
        size: &PyUD64,
        leverage: &PyUD64,
        post_only: bool,
        expiry_blocks: Option<u64>,
    ) -> Self {
        Self {
            inner: sdk_types::OrderRequest::new(
                request_id,
                perp_id,
                sdk_types::RequestType::OpenLong,
                None,
                price.0,
                size.0,
                expiry_blocks,
                post_only,
                false, // fill_or_kill
                false, // immediate_or_cancel
                None,  // max_matches
                leverage.0,
                None,  // last_exec_block
                None,  // amount
            ),
        }
    }
    
    /// Create an open short order request
    #[staticmethod]
    #[pyo3(signature = (request_id, perp_id, price, size, leverage, post_only=false, expiry_blocks=None))]
    fn open_short(
        request_id: u64,
        perp_id: u32,
        price: &PyUD64,
        size: &PyUD64,
        leverage: &PyUD64,
        post_only: bool,
        expiry_blocks: Option<u64>,
    ) -> Self {
        Self {
            inner: sdk_types::OrderRequest::new(
                request_id,
                perp_id,
                sdk_types::RequestType::OpenShort,
                None,
                price.0,
                size.0,
                expiry_blocks,
                post_only,
                false,
                false,
                None,
                leverage.0,
                None,
                None,
            ),
        }
    }
    
    /// Create a close long order request (reduce only)
    #[staticmethod]
    #[pyo3(signature = (request_id, perp_id, price, size, post_only=false, expiry_blocks=None))]
    fn close_long(
        request_id: u64,
        perp_id: u32,
        price: &PyUD64,
        size: &PyUD64,
        post_only: bool,
        expiry_blocks: Option<u64>,
    ) -> Self {
        Self {
            inner: sdk_types::OrderRequest::new(
                request_id,
                perp_id,
                sdk_types::RequestType::CloseLong,
                None,
                price.0,
                size.0,
                expiry_blocks,
                post_only,
                false,
                false,
                None,
                fastnum::UD64::ONE, // leverage not used for close
                None,
                None,
            ),
        }
    }
    
    /// Create a close short order request (reduce only)
    #[staticmethod]
    #[pyo3(signature = (request_id, perp_id, price, size, post_only=false, expiry_blocks=None))]
    fn close_short(
        request_id: u64,
        perp_id: u32,
        price: &PyUD64,
        size: &PyUD64,
        post_only: bool,
        expiry_blocks: Option<u64>,
    ) -> Self {
        Self {
            inner: sdk_types::OrderRequest::new(
                request_id,
                perp_id,
                sdk_types::RequestType::CloseShort,
                None,
                price.0,
                size.0,
                expiry_blocks,
                post_only,
                false,
                false,
                None,
                fastnum::UD64::ONE,
                None,
                None,
            ),
        }
    }
    
    /// Create a cancel order request
    ///
    /// Args:
    ///     request_id: Unique request ID for tracking
    ///     perp_id: Perpetual contract ID
    ///     order_id: ID of the order to cancel
    ///
    /// Returns:
    ///     OrderRequest for cancelling an existing order
    #[staticmethod]
    fn cancel(request_id: u64, perp_id: u32, order_id: u16) -> Self {
        Self {
            inner: sdk_types::OrderRequest::new(
                request_id,
                perp_id,
                sdk_types::RequestType::Cancel,
                std::num::NonZeroU16::new(order_id),
                fastnum::UD64::ZERO,
                fastnum::UD64::ZERO,
                None,
                false,
                false,
                false,
                None,
                fastnum::UD64::ONE,
                None,
                None,
            ),
        }
    }
}

impl From<sdk_types::OrderRequest> for OrderRequest {
    fn from(value: sdk_types::OrderRequest) -> Self {
        Self { inner: value }
    }
}

impl From<OrderRequest> for sdk_types::OrderRequest {
    fn from(value: OrderRequest) -> Self {
        value.inner
    }
}

// =============================================================================
// MakerFill - Individual maker fill within a trade
// =============================================================================

/// A single maker fill within a trade
///
/// Each maker fill represents one maker order that was matched against
/// a taker order. A single taker order may match against multiple makers.
#[pyclass(name = "MakerFill", module = "perpl_sdk.types", frozen)]
#[derive(Clone)]
pub struct MakerFill {
    pub(crate) inner: sdk_types::MakerFill,
}

#[pymethods]
impl MakerFill {
    /// Log index of this maker fill event
    #[getter]
    fn log_index(&self) -> u64 {
        self.inner.log_index
    }
    
    /// Maker account ID
    #[getter]
    fn maker_account_id(&self) -> u32 {
        self.inner.maker_account_id
    }
    
    /// Maker order ID
    #[getter]
    fn maker_order_id(&self) -> u16 {
        self.inner.maker_order_id.get()
    }
    
    /// Fill price (normalized decimal)
    #[getter]
    fn price(&self) -> PyUD64 {
        PyUD64(self.inner.price)
    }
    
    /// Fill size (normalized decimal)
    #[getter]
    fn size(&self) -> PyUD64 {
        PyUD64(self.inner.size)
    }
    
    /// Maker fee paid (normalized decimal, in collateral token)
    #[getter]
    fn fee(&self) -> PyUD64 {
        PyUD64(self.inner.fee)
    }
    
    fn __repr__(&self) -> String {
        format!(
            "MakerFill(maker_account={}, order={}, price={}, size={}, fee={})",
            self.inner.maker_account_id,
            self.inner.maker_order_id,
            self.inner.price,
            self.inner.size,
            self.inner.fee
        )
    }
}

impl From<sdk_types::MakerFill> for MakerFill {
    fn from(value: sdk_types::MakerFill) -> Self {
        Self { inner: value }
    }
}

impl From<MakerFill> for sdk_types::MakerFill {
    fn from(value: MakerFill) -> Self {
        value.inner
    }
}

// =============================================================================
// Trade - Complete trade event (taker matched against makers)
// =============================================================================

/// A complete trade event: one taker matched against one or more makers
///
/// Each Trade represents a single taker order execution that may have
/// matched against multiple maker orders. The maker_fills list contains
/// all individual maker fills that occurred as part of this trade.
#[pyclass(name = "Trade", module = "perpl_sdk.types", frozen)]
#[derive(Clone)]
pub struct Trade {
    pub(crate) inner: sdk_types::Trade,
}

#[pymethods]
impl Trade {
    /// Perpetual contract ID
    #[getter]
    fn perpetual_id(&self) -> u32 {
        self.inner.perpetual_id
    }
    
    /// Taker account ID
    #[getter]
    fn taker_account_id(&self) -> u32 {
        self.inner.taker_account_id
    }
    
    /// Taker side (Bid = buying, Ask = selling)
    #[getter]
    fn taker_side(&self) -> OrderSide {
        match self.inner.taker_side {
            sdk_types::OrderSide::Bid => OrderSide::Bid,
            sdk_types::OrderSide::Ask => OrderSide::Ask,
        }
    }
    
    /// Taker fee paid (normalized decimal, in collateral token)
    #[getter]
    fn taker_fee(&self) -> PyUD64 {
        PyUD64(self.inner.taker_fee)
    }
    
    /// All maker fills matched by this taker order
    ///
    /// Returns:
    ///     List of MakerFill objects
    fn maker_fills(&self, py: Python) -> PyResult<Py<PyList>> {
        let list = PyList::empty_bound(py);
        for fill in &self.inner.maker_fills {
            let fill_obj = Bound::new(py, MakerFill { inner: fill.clone() })?;
            list.append(fill_obj)?;
        }
        Ok(list.unbind())
    }
    
    /// Number of maker fills in this trade
    #[getter]
    fn num_fills(&self) -> usize {
        self.inner.maker_fills.len()
    }
    
    /// Total size filled across all makers
    fn total_size(&self) -> PyUD64 {
        PyUD64(self.inner.total_size())
    }
    
    /// Volume-weighted average price across all maker fills
    ///
    /// Returns:
    ///     Average price or None if there are no fills
    fn avg_price(&self) -> Option<PyUD64> {
        self.inner.avg_price().map(PyUD64)
    }
    
    /// Total maker fees paid across all fills
    fn total_maker_fees(&self) -> PyUD64 {
        PyUD64(self.inner.total_maker_fees())
    }
    
    /// Get volume-weighted average price, total size and total fees for a specific maker
    ///
    /// Args:
    ///     account_id: Maker account ID
    ///
    /// Returns:
    ///     Tuple of (avg_price, total_size, total_fee) or None if maker not in trade
    fn maker_total(&self, account_id: u32) -> Option<(PyUD64, PyUD64, PyUD64)> {
        self.inner.maker_total(account_id)
            .map(|(avg, size, fee)| (PyUD64(avg), PyUD64(size), PyUD64(fee)))
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Trade(perp={}, taker={}, side={:?}, size={}, fills={})",
            self.inner.perpetual_id,
            self.inner.taker_account_id,
            self.inner.taker_side,
            self.inner.total_size(),
            self.inner.maker_fills.len()
        )
    }
}

impl From<sdk_types::Trade> for Trade {
    fn from(value: sdk_types::Trade) -> Self {
        Self { inner: value }
    }
}

impl From<Trade> for sdk_types::Trade {
    fn from(value: Trade) -> Self {
        value.inner
    }
}

