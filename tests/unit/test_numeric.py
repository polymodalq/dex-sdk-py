"""
Unit Tests for Numeric Types (UD64, UD128, D256)

These tests verify:
- String parsing and formatting
- Arithmetic precision
- Comparison operators
- Edge cases (zero, max values, negative for D256)
- Round-trip conversions
"""

import pytest
from decimal import Decimal

# Try to import SDK, skip if not available
try:
    from perpl_sdk import UD64, UD128, D256
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


# =============================================================================
# UD64 Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestUD64:
    """Tests for unsigned 64-bit decimal type."""
    
    def test_from_string_integer(self):
        """Test parsing integer strings."""
        val = UD64("100")
        assert str(val) == "100" or str(val) == "100.0"
    
    def test_from_string_decimal(self):
        """Test parsing decimal strings."""
        val = UD64("123.456")
        assert "123.456" in str(val) or str(val) == "123.456"
    
    def test_from_string_zero(self):
        """Test parsing zero."""
        val = UD64("0")
        assert float(str(val)) == 0.0
    
    def test_from_string_small(self):
        """Test parsing small decimal values."""
        val = UD64("0.000001")
        assert float(str(val)) == pytest.approx(0.000001, rel=1e-6)
    
    def test_arithmetic_addition(self):
        """Test addition."""
        a = UD64("100.5")
        b = UD64("50.25")
        result = a + b
        assert float(str(result)) == pytest.approx(150.75, rel=1e-9)
    
    def test_arithmetic_subtraction(self):
        """Test subtraction."""
        a = UD64("100.5")
        b = UD64("50.25")
        result = a - b
        assert float(str(result)) == pytest.approx(50.25, rel=1e-9)
    
    def test_arithmetic_multiplication(self):
        """Test multiplication."""
        a = UD64("10.5")
        b = UD64("2.0")
        result = a * b
        assert float(str(result)) == pytest.approx(21.0, rel=1e-9)
    
    def test_arithmetic_division(self):
        """Test division."""
        a = UD64("21.0")
        b = UD64("2.0")
        result = a / b
        assert float(str(result)) == pytest.approx(10.5, rel=1e-9)
    
    def test_comparison_equal(self):
        """Test equality comparison."""
        a = UD64("100.5")
        b = UD64("100.5")
        assert a == b
    
    def test_comparison_less_than(self):
        """Test less than comparison."""
        a = UD64("50.0")
        b = UD64("100.0")
        assert a < b
    
    def test_comparison_greater_than(self):
        """Test greater than comparison."""
        a = UD64("100.0")
        b = UD64("50.0")
        assert a > b
    
    def test_repr(self):
        """Test string representation."""
        val = UD64("123.456")
        repr_str = repr(val)
        assert "123.456" in repr_str or "UD64" in repr_str
    
    def test_is_zero(self):
        """Test is_zero method."""
        zero = UD64("0")
        non_zero = UD64("1")
        assert zero.is_zero() == True
        assert non_zero.is_zero() == False
    
    def test_float_conversion(self):
        """Test float conversion."""
        val = UD64("123.456")
        assert float(val) == pytest.approx(123.456, rel=1e-9)
    
    def test_int_conversion(self):
        """Test int conversion."""
        val = UD64("123.456")
        assert int(val) == 123


# =============================================================================
# UD128 Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestUD128:
    """Tests for unsigned 128-bit decimal type."""
    
    def test_from_string_large_value(self):
        """Test parsing large values."""
        val = UD128("1000000000000.123456789")
        assert float(str(val)) == pytest.approx(1000000000000.123456789, rel=1e-9)
    
    def test_from_string_zero(self):
        """Test parsing zero."""
        val = UD128("0")
        assert float(str(val)) == 0.0
    
    def test_arithmetic_precision(self):
        """Test that arithmetic maintains precision."""
        a = UD128("1000000000.123456789")
        b = UD128("0.000000001")
        result = a + b
        # Should be able to represent tiny additions to large numbers
        # Use string comparison to avoid float precision loss
        result_str = str(result)
        assert "1000000000.12345679" in result_str or result_str > str(a)
    
    def test_large_multiplication(self):
        """Test multiplication of large values."""
        a = UD128("1000000.0")
        b = UD128("1000000.0")
        result = a * b
        assert float(str(result)) == pytest.approx(1e12, rel=1e-9)
    
    def test_comparison(self):
        """Test comparison operators."""
        a = UD128("1000000000.0")
        b = UD128("999999999.0")
        assert a > b
        assert b < a
        assert a != b
    
    def test_is_zero(self):
        """Test is_zero method."""
        zero = UD128("0")
        non_zero = UD128("1")
        assert zero.is_zero() == True
        assert non_zero.is_zero() == False


# =============================================================================
# D256 Tests (Signed)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestD256:
    """Tests for signed 256-bit decimal type."""
    
    def test_from_string_positive(self):
        """Test parsing positive values."""
        val = D256("12345.6789")
        assert float(str(val)) == pytest.approx(12345.6789, rel=1e-9)
    
    def test_from_string_negative(self):
        """Test parsing negative values."""
        val = D256("-12345.6789")
        assert float(str(val)) == pytest.approx(-12345.6789, rel=1e-9)
    
    def test_from_string_zero(self):
        """Test parsing zero."""
        val = D256("0")
        assert float(str(val)) == 0.0
    
    def test_arithmetic_with_negatives(self):
        """Test arithmetic involving negative numbers."""
        a = D256("100.0")
        b = D256("-50.0")
        result = a + b
        assert float(str(result)) == pytest.approx(50.0, rel=1e-9)
    
    def test_negative_subtraction(self):
        """Test subtraction resulting in negative."""
        a = D256("50.0")
        b = D256("100.0")
        result = a - b
        assert float(str(result)) == pytest.approx(-50.0, rel=1e-9)
    
    def test_negative_multiplication(self):
        """Test multiplication with negatives."""
        a = D256("-10.0")
        b = D256("5.0")
        result = a * b
        assert float(str(result)) == pytest.approx(-50.0, rel=1e-9)
    
    def test_sign_check(self):
        """Test sign-related methods if available."""
        pos = D256("100.0")
        neg = D256("-100.0")
        zero = D256("0")
        
        # Just verify they parse correctly
        assert float(str(pos)) > 0
        assert float(str(neg)) < 0
        assert float(str(zero)) == 0
    
    def test_comparison_across_signs(self):
        """Test comparison across positive and negative."""
        pos = D256("100.0")
        neg = D256("-100.0")
        
        assert pos > neg
        assert neg < pos
    
    def test_is_zero(self):
        """Test is_zero method."""
        zero = D256("0")
        non_zero = D256("1")
        assert zero.is_zero() == True
        assert non_zero.is_zero() == False


# =============================================================================
# Cross-Type Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericInterop:
    """Tests for interactions between numeric types."""
    
    def test_ud64_to_string_round_trip(self):
        """Test round-trip conversion through string."""
        original = "123.456789"
        val = UD64(original)
        result = str(val)
        # Should be able to parse back
        val2 = UD64(result)
        assert float(str(val)) == float(str(val2))
    
    def test_ud128_precision_preserved(self):
        """Test that UD128 preserves precision through operations."""
        val = UD128("123456789.123456789")
        doubled = val + val
        halved = doubled / UD128("2.0")
        
        original_float = float(str(val))
        result_float = float(str(halved))
        
        assert result_float == pytest.approx(original_float, rel=1e-9)


# =============================================================================
# Edge Cases
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericEdgeCases:
    """Edge case tests for numeric types."""
    
    def test_ud64_very_small(self):
        """Test very small values."""
        val = UD64("0.0000001")
        assert float(str(val)) > 0
    
    def test_ud64_many_decimals(self):
        """Test parsing with many decimal places."""
        # Should truncate or round appropriately
        val = UD64("1.123456789012345")
        assert float(str(val)) > 1.0
    
    def test_ud128_zero_operations(self):
        """Test operations with zero."""
        zero = UD128("0")
        val = UD128("100")
        
        assert float(str(val + zero)) == float(str(val))
        assert float(str(val * zero)) == 0.0
    
    def test_d256_zero_sign(self):
        """Test that zero has no negative sign issues."""
        pos_zero = D256("0")
        neg_zero = D256("-0")
        
        # Both should be equal to zero
        assert float(str(pos_zero)) == 0.0
        assert float(str(neg_zero)) == 0.0


# =============================================================================
# Numeric Type Boundary Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericBoundaries:
    """Boundary tests for numeric types."""
    
    def test_ud64_max_practical_value(self):
        """Test near-maximum practical values for UD64."""
        # UD64 is 64-bit unsigned with decimals
        # Test a large but reasonable value
        val = UD64("1000000000000.0")
        assert float(str(val)) > 0
    
    def test_ud64_minimum_precision(self):
        """Test minimum precision for UD64."""
        # Should handle very small decimal values
        val = UD64("0.000001")
        assert val.is_zero() == False
    
    def test_ud128_large_value(self):
        """Test large values for UD128."""
        val = UD128("999999999999999999.0")
        assert float(str(val)) > 0
    
    def test_d256_large_positive(self):
        """Test large positive D256 values."""
        val = D256("999999999999999999.0")
        assert float(str(val)) > 0
    
    def test_d256_large_negative(self):
        """Test large negative D256 values."""
        val = D256("-999999999999999999.0")
        assert float(str(val)) < 0


# =============================================================================
# Numeric Error Handling Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericErrorHandling:
    """Tests for numeric type error handling."""
    
    def test_ud64_invalid_negative_raises(self):
        """Test that UD64 rejects negative values."""
        with pytest.raises(Exception):  # May be ValueError or DexError
            UD64("-100.0")
    
    def test_ud128_invalid_negative_raises(self):
        """Test that UD128 rejects negative values."""
        with pytest.raises(Exception):  # May be ValueError or DexError
            UD128("-100.0")
    
    def test_ud64_invalid_string_raises(self):
        """Test that invalid string raises error."""
        with pytest.raises(Exception):
            UD64("not_a_number")
    
    def test_ud128_invalid_string_raises(self):
        """Test that invalid string raises error."""
        with pytest.raises(Exception):
            UD128("invalid")
    
    def test_d256_invalid_string_raises(self):
        """Test that invalid string raises error."""
        with pytest.raises(Exception):
            D256("abc.def")


# =============================================================================
# Numeric Division Safety Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericDivisionSafety:
    """Tests for division safety."""
    
    def test_ud64_division_by_large(self):
        """Test division by large value doesn't overflow."""
        a = UD64("1.0")
        b = UD64("1000000.0")
        result = a / b
        assert float(str(result)) < 1.0
        assert float(str(result)) > 0.0
    
    def test_ud128_division_precision(self):
        """Test division maintains precision."""
        a = UD128("1000000000.0")
        b = UD128("3.0")
        result = a / b
        # 1e9 / 3 ≈ 333333333.333...
        assert float(str(result)) > 333333333.0
        assert float(str(result)) < 333333334.0
    
    def test_d256_division_sign_handling(self):
        """Test D256 division with signs."""
        pos = D256("100.0")
        neg = D256("-100.0")
        divisor = D256("10.0")
        
        pos_result = pos / divisor
        neg_result = neg / divisor
        
        assert float(str(pos_result)) == pytest.approx(10.0, rel=1e-9)
        assert float(str(neg_result)) == pytest.approx(-10.0, rel=1e-9)


# =============================================================================
# Numeric Hash and Identity Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericHashAndIdentity:
    """Tests for hash and identity operations."""
    
    def test_ud64_equality_reflexive(self):
        """Test UD64 equality is reflexive."""
        a = UD64("123.456")
        assert a == a
    
    def test_ud64_equality_symmetric(self):
        """Test UD64 equality is symmetric."""
        a = UD64("123.456")
        b = UD64("123.456")
        assert a == b
        assert b == a
    
    def test_ud128_equality_transitive(self):
        """Test UD128 equality is transitive."""
        a = UD128("123.456")
        b = UD128("123.456")
        c = UD128("123.456")
        assert a == b
        assert b == c
        assert a == c
    
    def test_d256_inequality_correct(self):
        """Test D256 inequality."""
        a = D256("100.0")
        b = D256("-100.0")
        assert a != b


# =============================================================================
# Division by Zero Error Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDivisionByZero:
    """Tests for division by zero error handling."""
    
    def test_ud64_division_by_zero_raises(self):
        """Test that UD64 division by zero raises ZeroDivisionError."""
        a = UD64("100.0")
        zero = UD64("0")
        with pytest.raises(ZeroDivisionError):
            _ = a / zero
    
    def test_ud128_division_by_zero_raises(self):
        """Test that UD128 division by zero raises ZeroDivisionError."""
        a = UD128("100.0")
        zero = UD128("0")
        with pytest.raises(ZeroDivisionError):
            _ = a / zero
    
    def test_d256_division_by_zero_raises(self):
        """Test that D256 division by zero raises ZeroDivisionError."""
        a = D256("100.0")
        zero = D256("0")
        with pytest.raises(ZeroDivisionError):
            _ = a / zero
    
    def test_ud64_modulo_by_zero_raises(self):
        """Test that UD64 modulo by zero raises ZeroDivisionError."""
        a = UD64("100.0")
        zero = UD64("0")
        with pytest.raises(ZeroDivisionError):
            _ = a % zero


# =============================================================================
# Numeric Conversion Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericConversions:
    """Tests for numeric type conversions."""
    
    def test_ud64_to_decimal(self):
        """Test UD64.to_decimal() method."""
        val = UD64("123.456789")
        dec = val.to_decimal()
        assert dec is not None
        # Should be a Python Decimal
        assert str(dec) == "123.456789" or "123.456789" in str(dec)
    
    def test_ud128_to_decimal(self):
        """Test UD128.to_decimal() method."""
        val = UD128("123456789.123456789")
        dec = val.to_decimal()
        assert dec is not None
    
    def test_d256_to_decimal(self):
        """Test D256.to_decimal() method."""
        val = D256("-123.456")
        dec = val.to_decimal()
        assert dec is not None
        # Should handle sign
        assert float(str(dec)) < 0


# =============================================================================
# D256 Sign Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestD256SignMethods:
    """Tests for D256 sign-related methods."""
    
    def test_d256_is_positive(self):
        """Test D256.is_positive() method."""
        pos = D256("100.0")
        neg = D256("-100.0")
        zero = D256("0")
        
        assert pos.is_positive() == True
        assert neg.is_positive() == False
        assert zero.is_positive() == False
    
    def test_d256_is_negative(self):
        """Test D256.is_negative() method."""
        pos = D256("100.0")
        neg = D256("-100.0")
        zero = D256("0")
        
        assert pos.is_negative() == False
        assert neg.is_negative() == True
        assert zero.is_negative() == False
    
    def test_d256_negation(self):
        """Test D256 negation operator."""
        val = D256("100.0")
        neg = -val
        assert float(str(neg)) == pytest.approx(-100.0, rel=1e-9)
    
    def test_d256_abs(self):
        """Test D256 abs() function."""
        neg = D256("-100.0")
        pos = abs(neg)
        assert float(str(pos)) == pytest.approx(100.0, rel=1e-9)


# =============================================================================
# Numeric from Integer Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericFromInteger:
    """Tests for creating numeric types from integers."""
    
    def test_ud64_from_int(self):
        """Test creating UD64 from integer."""
        val = UD64(100)
        assert float(val) == 100.0
    
    def test_ud128_from_int(self):
        """Test creating UD128 from integer."""
        val = UD128(100)
        assert float(val) == 100.0
    
    def test_d256_from_int(self):
        """Test creating D256 from integer."""
        val = D256(100)
        assert float(val) == 100.0
    
    def test_d256_from_negative_int(self):
        """Test creating D256 from negative integer."""
        val = D256(-100)
        assert float(val) == -100.0


# =============================================================================
# Numeric from Float Tests (lossy)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericFromFloat:
    """Tests for creating numeric types from floats (lossy conversion)."""
    
    def test_ud64_from_float(self):
        """Test creating UD64 from float."""
        val = UD64(100.5)
        assert float(val) == pytest.approx(100.5, rel=1e-9)
    
    def test_ud128_from_float(self):
        """Test creating UD128 from float."""
        val = UD128(100.5)
        assert float(val) == pytest.approx(100.5, rel=1e-9)
    
    def test_d256_from_float(self):
        """Test creating D256 from float."""
        val = D256(100.5)
        assert float(val) == pytest.approx(100.5, rel=1e-9)
    
    def test_d256_from_negative_float(self):
        """Test creating D256 from negative float."""
        val = D256(-100.5)
        assert float(val) == pytest.approx(-100.5, rel=1e-9)
