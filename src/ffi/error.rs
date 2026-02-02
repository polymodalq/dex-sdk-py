//! Error Handling and Python Exception Mapping
//!
//! Provides comprehensive error conversion between Rust and Python,
//! maintaining error semantics from the original SDK.

use pyo3::prelude::*;
use pyo3::exceptions::{PyException, PyValueError, PyRuntimeError};
use std::fmt;

// Create custom exception type using PyO3 0.21 API
pyo3::create_exception!(perpl_sdk, DexError, PyException, "Base exception for all DEX SDK errors");

// Helper function to convert SDK errors to Python exceptions
// Avoids conflicting From implementations
pub fn to_py_err<E: fmt::Display>(err: E) -> PyErr {
    DexError::new_err(format!("{}", err))
}

/// Error context for richer error messages
pub trait ErrorContext<T> {
    fn context(self, msg: &str) -> PyResult<T>;
}

impl<T, E: fmt::Display> ErrorContext<T> for Result<T, E> {
    fn context(self, msg: &str) -> PyResult<T> {
        self.map_err(|e| PyRuntimeError::new_err(format!("{}: {}", msg, e)))
    }
}

