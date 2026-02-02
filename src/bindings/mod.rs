//! Public API Bindings
//!
//! This module provides the Python-facing API surface, mirroring the
//! structure of `dex-sdk` exactly.

pub mod numeric;
pub mod types;
pub mod chain;
pub mod state;
pub mod builder;
pub mod stream;
pub mod event_stream;
pub mod tx_builder;
pub mod error;
pub mod observability;
pub mod fetch;

// Re-export for convenient access
pub use numeric::*;
pub use types::*;
pub use chain::*;
pub use state::*;
pub use builder::*;
pub use stream::*;
pub use event_stream::*;
pub use tx_builder::*;
pub use error::*;
pub use observability::*;
pub use fetch::*;

