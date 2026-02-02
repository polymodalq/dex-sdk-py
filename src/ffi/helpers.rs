//! Helper Functions for Common Conversions
//!
//! Utility functions for parsing blockchain primitives from Python types.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use alloy::primitives::{Address, U256, I256};
use std::str::FromStr;

/// Parse Ethereum address from string
pub fn parse_address(value: &str) -> PyResult<Address> {
    Address::from_str(value)
        .map_err(|e| PyValueError::new_err(format!("Invalid address '{}': {}", value, e)))
}

/// Parse U256 from various Python types
pub fn parse_u256(value: &Bound<'_, PyAny>) -> PyResult<U256> {
    if let Ok(s) = value.extract::<String>() {
        // Try hex first (with or without 0x prefix)
        let s = s.trim_start_matches("0x");
        U256::from_str_radix(s, 16)
            .or_else(|_| U256::from_str_radix(s, 10))
            .map_err(|e| PyValueError::new_err(format!("Invalid U256 '{}': {}", s, e)))
    } else if let Ok(i) = value.extract::<u64>() {
        Ok(U256::from(i))
    } else if let Ok(i) = value.extract::<u128>() {
        Ok(U256::from(i))
    } else {
        Err(PyValueError::new_err("Expected str or int for U256"))
    }
}

/// Parse I256 from various Python types
pub fn parse_i256(value: &Bound<'_, PyAny>) -> PyResult<I256> {
    if let Ok(s) = value.extract::<String>() {
        let is_negative = s.starts_with('-');
        let s = s.trim_start_matches(&['-', '+'][..]).trim_start_matches("0x");
        
        let abs = U256::from_str_radix(s, 16)
            .or_else(|_| U256::from_str_radix(s, 10))
            .map_err(|e| PyValueError::new_err(format!("Invalid I256 '{}': {}", s, e)))?;
        
        let i256 = I256::try_from(abs)
            .map_err(|e| PyValueError::new_err(format!("Value out of range: {}", e)))?;
        
        Ok(if is_negative { -i256 } else { i256 })
    } else if let Ok(i) = value.extract::<i64>() {
        Ok(I256::try_from(i).unwrap())
    } else {
        Err(PyValueError::new_err("Expected str or int for I256"))
    }
}

/// Format address as checksummed hex string
pub fn format_address(addr: &Address) -> String {
    format!("{:?}", addr)
}

/// Format U256 as hex string
pub fn format_u256(value: &U256) -> String {
    format!("0x{:x}", value)
}

/// Format I256 as decimal string (for better readability)
pub fn format_i256(value: &I256) -> String {
    format!("{}", value)
}

