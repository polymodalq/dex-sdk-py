//! Observability Configuration
//!
//! Production-grade logging and metrics configuration.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use tracing_subscriber::EnvFilter;

/// Configure logging for the SDK
///
/// # Arguments
/// * `level` - Log level: "trace", "debug", "info", "warn", "error"
///
/// # Example
/// ```python
/// import perpl_sdk
/// perpl_sdk.configure_logging("info")
/// ```
#[pyfunction]
pub fn configure_logging(level: String) -> PyResult<()> {
    let filter = EnvFilter::try_new(&level)
        .map_err(|e| PyValueError::new_err(format!("Invalid log level: {}", e)))?;
    
    tracing_subscriber::fmt()
        .with_env_filter(filter)
        .try_init()
        .map_err(|e| PyValueError::new_err(format!("Failed to initialize logging: {}", e)))?;
    
    Ok(())
}

