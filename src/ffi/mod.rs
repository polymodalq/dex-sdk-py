//! FFI Utilities and Type Conversion Layer
//!
//! This module provides the foundational FFI infrastructure for converting
//! between Rust and Python types with zero semantic loss.
//!
//! ## Design Pattern
//!
//! All conversions follow a consistent pattern:
//! - Rust types are wrapped in newtype structs for PyO3
//! - Conversions are infallible where possible (From/Into)
//! - Fallible conversions use TryFrom with detailed error messages
//! - Zero-copy state sharing via Arc/RwLock for memory efficiency

pub mod numeric;
pub mod error;
pub mod helpers;
pub mod shared;
pub mod runtime;

// Re-export commonly used conversion utilities
pub use numeric::{PyUD64, PyUD128, PyD256, PyConverter};
pub use error::{DexError, ErrorContext};
pub use helpers::{parse_address, parse_u256, parse_i256};
pub use shared::SharedExchange;
pub use runtime::{block_on, spawn, handle, RUNTIME};

