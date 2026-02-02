//! Numeric Type Conversions
//!
//! High-precision decimal type bridges between Rust (fastnum) and Python.
//!
//! ## Type Mapping
//!
//! | Rust Type | Python Class | Precision | Use Case |
//! |-----------|--------------|-----------|----------|
//! | UD64      | UD64         | 64-bit unsigned | Prices, sizes, fees |
//! | UD128     | UD128        | 128-bit unsigned | Collateral amounts |
//! | D256      | D256         | 256-bit signed | PnL calculations |
//! | Converter | Converter    | Fixed-point converter | Type conversions |
//!
//! ## Design Decisions
//!
//! 1. **String-Based Construction**: To avoid floating-point precision loss,
//!    all decimal numbers are constructed from strings.
//!
//! 2. **Lazy Python Decimal Conversion**: Python's `decimal.Decimal` is only
//!    created when explicitly requested via `to_decimal()`.
//!
//! 3. **Arithmetic in Rust**: All operations stay in Rust space for performance,
//!    only crossing FFI boundary when Python access is needed.

use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyTypeError, PyZeroDivisionError};
use pyo3::types::PyString;
use fastnum::{UD64, UD128, D256 as FastD256, decimal::{Sign, Context, RoundingMode}};
use std::str::FromStr;
use std::cmp::Ordering;

/// Default context for decimal operations (matches SDK behavior)
fn decimal_context() -> Context {
    Context::default().with_rounding_mode(RoundingMode::Floor)
}

// =============================================================================
// Unsigned 64-bit Decimal
// =============================================================================

/// Unsigned 64-bit decimal number
///
/// Used for prices, order sizes, fees, and other non-negative quantities.
/// Matches `fastnum::UD64` exactly.
#[pyclass(name = "UD64", module = "perpl_sdk")]
#[derive(Clone, Copy, Debug)]
pub struct PyUD64(pub UD64);

#[pymethods]
impl PyUD64 {
    #[new]
    fn new(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(s) = value.extract::<String>() {
            UD64::from_str(&s, decimal_context())
                .map(Self)
                .map_err(|e| PyValueError::new_err(format!("Invalid UD64 string: {}", e)))
        } else if let Ok(i) = value.extract::<u64>() {
            Ok(Self(UD64::from(i)))
        } else if let Ok(f) = value.extract::<f64>() {
            if f < 0.0 {
                Err(PyValueError::new_err("UD64 cannot be negative"))
            } else {
                UD64::try_from(f)
                    .map(Self)
                    .map_err(|e| PyValueError::new_err(format!("Invalid UD64 float: {}", e)))
            }
        } else {
            Err(PyTypeError::new_err("Expected str, int, or float"))
        }
    }
    
    fn __str__(&self) -> String {
        self.0.to_string()
    }
    
    fn __repr__(&self) -> String {
        format!("UD64('{}')", self.0)
    }
    
    fn __float__(&self) -> f64 {
        // Lossy conversion for plotting/display
        self.0.to_string().parse().unwrap_or(0.0)
    }
    
    fn __int__(&self) -> PyResult<u64> {
        self.0.to_string()
            .split('.')
            .next()
            .and_then(|s| s.parse().ok())
            .ok_or_else(|| PyValueError::new_err("Cannot convert to int"))
    }
    
    // Arithmetic operations
    fn __add__(&self, other: &Self) -> Self {
        Self(self.0 + other.0)
    }
    
    fn __sub__(&self, other: &Self) -> Self {
        Self(self.0 - other.0)
    }
    
    fn __mul__(&self, other: &Self) -> Self {
        Self(self.0 * other.0)
    }
    
    fn __truediv__(&self, other: &Self) -> PyResult<Self> {
        if other.0.is_zero() {
            Err(PyZeroDivisionError::new_err("Division by zero"))
        } else {
            Ok(Self(self.0 / other.0))
        }
    }
    
    fn __mod__(&self, other: &Self) -> PyResult<Self> {
        if other.0.is_zero() {
            Err(PyZeroDivisionError::new_err("Modulo by zero"))
        } else {
            Ok(Self(self.0 % other.0))
        }
    }
    
    // Comparison operations
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
        self.0.to_string().hash(&mut hasher);
        hasher.finish()
    }
    
    /// Convert to Python's decimal.Decimal for high-precision operations
    fn to_decimal(&self, py: Python) -> PyResult<PyObject> {
        let decimal_module = py.import_bound("decimal")?;
        let decimal_class = decimal_module.getattr("Decimal")?;
        Ok(decimal_class.call1((self.0.to_string(),))?.into())
    }
    
    /// Check if value is zero
    fn is_zero(&self) -> bool {
        self.0.is_zero()
    }
}

impl From<UD64> for PyUD64 {
    fn from(value: UD64) -> Self {
        Self(value)
    }
}

impl From<PyUD64> for UD64 {
    fn from(value: PyUD64) -> Self {
        value.0
    }
}

// =============================================================================
// Unsigned 128-bit Decimal
// =============================================================================

/// Unsigned 128-bit decimal number
///
/// Used for collateral amounts and large value calculations.
/// Matches `fastnum::UD128` exactly.
#[pyclass(name = "UD128", module = "perpl_sdk")]
#[derive(Clone, Copy, Debug)]
pub struct PyUD128(pub UD128);

#[pymethods]
impl PyUD128 {
    #[new]
    fn new(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(s) = value.extract::<String>() {
            UD128::from_str(&s, decimal_context())
                .map(Self)
                .map_err(|e| PyValueError::new_err(format!("Invalid UD128 string: {}", e)))
        } else if let Ok(i) = value.extract::<u64>() {
            Ok(Self(UD128::from(i)))
        } else if let Ok(f) = value.extract::<f64>() {
            if f < 0.0 {
                Err(PyValueError::new_err("UD128 cannot be negative"))
            } else {
                UD128::try_from(f)
                    .map(Self)
                    .map_err(|e| PyValueError::new_err(format!("Invalid UD128 float: {}", e)))
            }
        } else {
            Err(PyTypeError::new_err("Expected str, int, or float"))
        }
    }
    
    fn __str__(&self) -> String {
        self.0.to_string()
    }
    
    fn __repr__(&self) -> String {
        format!("UD128('{}')", self.0)
    }
    
    fn __float__(&self) -> f64 {
        self.0.to_string().parse().unwrap_or(0.0)
    }
    
    // Arithmetic operations
    fn __add__(&self, other: &Self) -> Self {
        Self(self.0 + other.0)
    }
    
    fn __sub__(&self, other: &Self) -> Self {
        Self(self.0 - other.0)
    }
    
    fn __mul__(&self, other: &Self) -> Self {
        Self(self.0 * other.0)
    }
    
    fn __truediv__(&self, other: &Self) -> PyResult<Self> {
        if other.0.is_zero() {
            Err(PyZeroDivisionError::new_err("Division by zero"))
        } else {
            Ok(Self(self.0 / other.0))
        }
    }
    
    // Comparison operations
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
        self.0.to_string().hash(&mut hasher);
        hasher.finish()
    }
    
    fn to_decimal(&self, py: Python) -> PyResult<PyObject> {
        let decimal_module = py.import_bound("decimal")?;
        let decimal_class = decimal_module.getattr("Decimal")?;
        Ok(decimal_class.call1((self.0.to_string(),))?.into())
    }
    
    fn is_zero(&self) -> bool {
        self.0.is_zero()
    }
}

impl From<UD128> for PyUD128 {
    fn from(value: UD128) -> Self {
        Self(value)
    }
}

impl From<PyUD128> for UD128 {
    fn from(value: PyUD128) -> Self {
        value.0
    }
}

// =============================================================================
// Signed 256-bit Decimal
// =============================================================================

/// Signed 256-bit decimal number
///
/// Used for PnL calculations and other signed quantities.
/// Matches `fastnum::D256` exactly.
#[pyclass(name = "D256", module = "perpl_sdk")]
#[derive(Clone, Copy, Debug)]
pub struct PyD256(pub FastD256);

#[pymethods]
impl PyD256 {
    #[new]
    fn new(value: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(s) = value.extract::<String>() {
            FastD256::from_str(&s, decimal_context())
                .map(Self)
                .map_err(|e| PyValueError::new_err(format!("Invalid D256 string: {}", e)))
        } else if let Ok(i) = value.extract::<i64>() {
            Ok(Self(FastD256::from(i)))
        } else if let Ok(f) = value.extract::<f64>() {
            FastD256::try_from(f)
                .map(Self)
                .map_err(|e| PyValueError::new_err(format!("Invalid D256 float: {}", e)))
        } else {
            Err(PyTypeError::new_err("Expected str, int, or float"))
        }
    }
    
    fn __str__(&self) -> String {
        self.0.to_string()
    }
    
    fn __repr__(&self) -> String {
        format!("D256('{}')", self.0)
    }
    
    fn __float__(&self) -> f64 {
        self.0.to_string().parse().unwrap_or(0.0)
    }
    
    fn __neg__(&self) -> Self {
        Self(-self.0)
    }
    
    fn __abs__(&self) -> Self {
        Self(self.0.abs())
    }
    
    // Arithmetic operations
    fn __add__(&self, other: &Self) -> Self {
        Self(self.0 + other.0)
    }
    
    fn __sub__(&self, other: &Self) -> Self {
        Self(self.0 - other.0)
    }
    
    fn __mul__(&self, other: &Self) -> Self {
        Self(self.0 * other.0)
    }
    
    fn __truediv__(&self, other: &Self) -> PyResult<Self> {
        if other.0.is_zero() {
            Err(PyZeroDivisionError::new_err("Division by zero"))
        } else {
            Ok(Self(self.0 / other.0))
        }
    }
    
    // Comparison operations
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
        self.0.to_string().hash(&mut hasher);
        hasher.finish()
    }
    
    fn to_decimal(&self, py: Python) -> PyResult<PyObject> {
        let decimal_module = py.import_bound("decimal")?;
        let decimal_class = decimal_module.getattr("Decimal")?;
        Ok(decimal_class.call1((self.0.to_string(),))?.into())
    }
    
    fn is_zero(&self) -> bool {
        self.0.is_zero()
    }
    
    fn is_positive(&self) -> bool {
        self.0 > FastD256::ZERO
    }
    
    fn is_negative(&self) -> bool {
        self.0 < FastD256::ZERO
    }
}

impl From<FastD256> for PyD256 {
    fn from(value: FastD256) -> Self {
        Self(value)
    }
}

impl From<PyD256> for FastD256 {
    fn from(value: PyD256) -> Self {
        value.0
    }
}

// =============================================================================
// Converter
// =============================================================================

/// Fixed-point to decimal converter
///
/// Handles conversion between blockchain fixed-point integers and
/// decimal representations. Matches `dex_sdk::num::Converter` exactly.
#[pyclass(name = "Converter", module = "perpl_sdk")]
#[derive(Clone, Copy, Debug)]
pub struct PyConverter(pub dex_sdk::num::Converter);

#[pymethods]
impl PyConverter {
    #[getter]
    fn decimals(&self) -> u8 {
        self.0.decimals()
    }
    
    fn __repr__(&self) -> String {
        format!("Converter(decimals={})", self.0.decimals())
    }
}

impl From<dex_sdk::num::Converter> for PyConverter {
    fn from(value: dex_sdk::num::Converter) -> Self {
        Self(value)
    }
}

impl From<PyConverter> for dex_sdk::num::Converter {
    fn from(value: PyConverter) -> Self {
        value.0
    }
}

