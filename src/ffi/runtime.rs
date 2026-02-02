//! Global Tokio Runtime
//!
//! This module provides a shared Tokio runtime for all async operations.
//! Creating a new runtime per operation is expensive, so we use a global
//! lazily-initialized runtime that's shared across all SDK operations.
//!
//! ## Design
//!
//! - Uses `once_cell::sync::Lazy` for thread-safe lazy initialization
//! - Multi-threaded runtime with configurable worker threads
//! - Provides `block_on` for synchronous contexts
//! - Provides `spawn` for background tasks
//!
//! ## Usage
//!
//! ```rust
//! use crate::ffi::runtime::{block_on, spawn};
//!
//! // In a synchronous context (e.g., PyO3 sync method):
//! let result = block_on(async {
//!     // async code here
//! });
//!
//! // Spawn a background task:
//! spawn(async {
//!     // background work
//! });
//! ```

use once_cell::sync::Lazy;
use tokio::runtime::Runtime;

/// Default number of worker threads for the runtime.
const DEFAULT_WORKER_THREADS: usize = 4;

/// Global shared Tokio runtime.
///
/// This runtime is lazily initialized on first access and shared across
/// all SDK operations. It uses a multi-threaded scheduler for optimal
/// performance on modern systems.
pub static RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .worker_threads(DEFAULT_WORKER_THREADS)
        .enable_all()
        .thread_name("perpl-sdk-worker")
        .build()
        .expect("Failed to create Tokio runtime")
});

/// Execute an async operation on the shared runtime, blocking until complete.
///
/// This is the primary way to run async operations from synchronous Python code.
/// The GIL should be released before calling this to avoid deadlocks.
///
/// # Example
///
/// ```rust
/// fn build(&self, py: Python) -> PyResult<Exchange> {
///     py.allow_threads(|| {
///         block_on(self.build_async())
///     })
/// }
/// ```
#[inline]
pub fn block_on<F: std::future::Future>(future: F) -> F::Output {
    RUNTIME.block_on(future)
}

/// Spawn an async task on the shared runtime.
///
/// The task runs in the background and the handle can be used to await the result.
#[inline]
pub fn spawn<F>(future: F) -> tokio::task::JoinHandle<F::Output>
where
    F: std::future::Future + Send + 'static,
    F::Output: Send + 'static,
{
    RUNTIME.spawn(future)
}

/// Get a handle to the shared runtime.
///
/// Useful for creating runtime-bound resources like channels.
#[inline]
pub fn handle() -> tokio::runtime::Handle {
    RUNTIME.handle().clone()
}
