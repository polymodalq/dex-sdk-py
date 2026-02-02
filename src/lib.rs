//! # Perpl DEX SDK - Python Bindings
//!
//! Production-grade Python bindings for the Perpl perpetual derivatives DEX SDK.
//!
//! ## Architecture
//!
//! This crate provides zero-overhead FFI bindings between Rust and Python, maintaining
//! exact semantic equivalence with the original Rust SDK. All naming conventions,
//! type semantics, and behavioral characteristics are preserved.
//!
//! ### Design Principles
//!
//! 1. **Zero-Touch Original Code**: The `dex-sdk` crate is used as a dependency with
//!    no modifications whatsoever.
//!
//! 2. **Exact Nomenclature Mapping**: All types, functions, and methods use identical
//!    names to their Rust counterparts (snake_case throughout).
//!
//! 3. **Performance First**: Minimal overhead through:
//!    - Arc/RwLock for shared state (lock-free reads where possible)
//!    - Batch operations to reduce FFI crossings
//!    - Lazy evaluation and zero-copy patterns
//!    - GIL release for CPU-intensive operations
//!
//! 4. **Production-Grade Observability**: Built-in tracing, metrics, and structured
//!    logging for enterprise deployments.
//!
//! 5. **Type Safety**: Full type information preserved through comprehensive `.pyi` stubs.
//!
//! ## Module Organization
//!
//! ```text
//! perpl_sdk/
//! ├── lib.rs               # This file - module definition and PyO3 registration
//! ├── ffi/
//! │   ├── mod.rs           # FFI utilities and conversion traits
//! │   ├── numeric.rs       # Decimal type conversions (UD64, UD128, D256)
//! │   ├── error.rs         # Error type conversions and Python exception mapping
//! │   ├── shared.rs        # SharedExchange reference wrapper
//! │   └── runtime.rs       # Global Tokio runtime
//! └── bindings/
//!     ├── mod.rs           # Public API surface
//!     ├── types.rs         # Core types (StateInstant, enums, primitives)
//!     ├── chain.rs         # Chain configuration
//!     ├── state.rs         # State management (Exchange, Perpetual, etc.)
//!     ├── stream.rs        # Event types
//!     ├── event_stream.rs  # WebSocket event streaming
//!     ├── tx_builder.rs    # Transaction building and signing
//!     └── builder.rs       # SnapshotBuilder
//! ```

use pyo3::prelude::*;

// FFI layer - type conversions and utilities
mod ffi;

// Public bindings - mirrors dex-sdk structure
mod bindings;

use bindings::*;

/// Python module initialization
///
/// Registers all types, functions, and submodules with Python. Module structure
/// mirrors the original Rust SDK exactly.
///
/// Note: This module is named `_native` to match the maturin configuration
/// in pyproject.toml (module-name = "perpl_sdk._native")
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Get Python token from the bound module
    let py = m.py();
    
    // Module metadata
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__doc__", "Perpl DEX SDK - High-performance perpetual DEX on Monad")?;
    m.add("DEX_REVISION", dex_sdk::abi::DEX_REVISION)?;
    
    // Core configuration types
    m.add_class::<chain::Chain>()?;
    
    // Numeric types - exact mapping of fastnum types
    m.add_class::<numeric::UD64>()?;
    m.add_class::<numeric::UD128>()?;
    m.add_class::<numeric::D256>()?;
    m.add_class::<numeric::Converter>()?;
    
    // Core types
    m.add_class::<types::StateInstant>()?;
    
    // State management types
    m.add_class::<state::Exchange>()?;
    m.add_class::<state::Perpetual>()?;
    m.add_class::<state::Account>()?;
    m.add_class::<state::Position>()?;
    m.add_class::<state::Order>()?;
    m.add_class::<state::L2Book>()?;
    
    // Builder pattern
    m.add_class::<builder::SnapshotBuilder>()?;
    m.add_function(wrap_pyfunction!(builder::snapshot, m)?)?;
    
    // Block event fetching (for incremental state updates)
    m.add_function(wrap_pyfunction!(fetch::fetch_block_events, m)?)?;
    m.add_function(wrap_pyfunction!(fetch::fetch_block_events_range, m)?)?;
    m.add_function(wrap_pyfunction!(fetch::get_latest_block, m)?)?;
    
    // Stream/Event types
    m.add_class::<stream::RawEvent>()?;
    m.add_class::<stream::RawBlockEvents>()?;
    m.add_class::<stream::StateEvent>()?;
    m.add_class::<stream::StateBlockEvents>()?;
    
    // Event streaming (WebSocket)
    m.add_class::<event_stream::EventStreamBuilder>()?;
    m.add_class::<event_stream::EventStream>()?;
    
    // Transaction building
    m.add_class::<tx_builder::Signer>()?;
    m.add_class::<tx_builder::TransactionBuilder>()?;
    m.add_class::<tx_builder::UnsignedTransaction>()?;
    m.add_class::<tx_builder::SignedTransaction>()?;
    m.add_class::<tx_builder::TransactionReceipt>()?;
    
    // Types submodule - enums, request types, and trade types
    let types_mod = PyModule::new_bound(py, "types")?;
    types_mod.add_class::<types::OrderType>()?;
    types_mod.add_class::<types::OrderSide>()?;
    types_mod.add_class::<types::PositionType>()?;
    types_mod.add_class::<types::RequestType>()?;
    types_mod.add_class::<types::OrderRequest>()?;
    types_mod.add_class::<types::MakerFill>()?;
    types_mod.add_class::<types::Trade>()?;
    m.add_submodule(&types_mod)?;
    
    // Error types
    m.add("DexError", py.get_type_bound::<error::DexError>())?;
    
    // Observability configuration
    m.add_function(wrap_pyfunction!(observability::configure_logging, m)?)?;
    
    Ok(())
}

