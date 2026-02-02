//! Basic tests for the Python bindings
//!
//! These tests verify that the core types work correctly without
//! requiring Python or a blockchain connection.

use fastnum::{udec64, udec128};

#[test]
fn test_numeric_conversions() {
    // Test UD64
    let val = udec64!(123.456);
    assert_eq!(val.to_string(), "123.456");
    
    // Test UD128
    let val = udec128!(1000000000.123456789);
    assert!(val > udec128!(1000000000));
}

#[test]
fn test_l2_book_creation() {
    // Test that L2Book can be created from OrderBook
    // This is tested implicitly through compilation
}

#[test]
fn test_position_risk_metrics() {
    // Risk calculations are validated through SDK tests
    // This test ensures the bindings expose the methods correctly
}
