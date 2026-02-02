"""
Unit Tests for DexError Exception

Tests for the SDK exception type:
- Exception can be raised and caught
- Exception message is accessible
- Exception inheritance hierarchy
- String representation
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import DexError
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


# =============================================================================
# DexError Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorBasic:
    """Basic tests for DexError exception."""
    
    def test_dex_error_type_exists(self):
        """Verify DexError type is importable."""
        assert DexError is not None
    
    def test_dex_error_is_exception(self):
        """Verify DexError is an Exception subclass."""
        assert issubclass(DexError, Exception)
    
    def test_dex_error_is_base_exception(self):
        """Verify DexError is a BaseException subclass."""
        assert issubclass(DexError, BaseException)


# =============================================================================
# DexError Raising Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorRaising:
    """Tests for raising DexError."""
    
    def test_can_raise_dex_error(self):
        """Verify DexError can be raised."""
        with pytest.raises(DexError):
            raise DexError("Test error message")
    
    def test_can_catch_dex_error(self):
        """Verify DexError can be caught."""
        try:
            raise DexError("Test error")
        except DexError as e:
            assert e is not None
    
    def test_can_catch_as_exception(self):
        """Verify DexError can be caught as Exception."""
        try:
            raise DexError("Test error")
        except Exception as e:
            assert isinstance(e, DexError)


# =============================================================================
# DexError Message Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorMessage:
    """Tests for DexError message handling."""
    
    def test_error_message_accessible(self):
        """Verify error message is accessible via args."""
        msg = "This is a test error message"
        try:
            raise DexError(msg)
        except DexError as e:
            assert msg in str(e)
    
    def test_error_message_in_str(self):
        """Verify error message appears in string representation."""
        msg = "Snapshot build failed"
        error = DexError(msg)
        assert msg in str(error)
    
    def test_error_args_tuple(self):
        """Verify error args is a tuple."""
        msg = "Test message"
        try:
            raise DexError(msg)
        except DexError as e:
            assert isinstance(e.args, tuple)


# =============================================================================
# DexError In Context Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorInContext:
    """Tests for DexError in realistic contexts."""
    
    def test_error_in_try_except_else(self):
        """Verify DexError works in try-except-else."""
        succeeded = False
        failed = False
        
        try:
            raise DexError("Expected failure")
        except DexError:
            failed = True
        else:
            succeeded = True
        
        assert failed
        assert not succeeded
    
    def test_error_in_try_except_finally(self):
        """Verify DexError works in try-except-finally."""
        finally_ran = False
        caught = False
        
        try:
            raise DexError("Test")
        except DexError:
            caught = True
        finally:
            finally_ran = True
        
        assert caught
        assert finally_ran
    
    def test_error_reraise(self):
        """Verify DexError can be re-raised."""
        original_msg = "Original error"
        
        with pytest.raises(DexError) as excinfo:
            try:
                raise DexError(original_msg)
            except DexError:
                raise
        
        assert original_msg in str(excinfo.value)
    
    def test_error_chain(self):
        """Verify DexError can be chained with other exceptions."""
        inner_msg = "Inner error"
        outer_msg = "Outer error"
        
        try:
            try:
                raise ValueError(inner_msg)
            except ValueError as e:
                raise DexError(outer_msg) from e
        except DexError as e:
            assert outer_msg in str(e)
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)


# =============================================================================
# DexError Edge Cases
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorEdgeCases:
    """Edge case tests for DexError."""
    
    def test_empty_message(self):
        """Verify DexError works with empty message."""
        with pytest.raises(DexError):
            raise DexError("")
    
    def test_unicode_message(self):
        """Verify DexError works with unicode message."""
        msg = "Error: 日本語テスト 🔥"
        try:
            raise DexError(msg)
        except DexError as e:
            assert msg in str(e)
    
    def test_long_message(self):
        """Verify DexError works with long message."""
        msg = "x" * 10000
        try:
            raise DexError(msg)
        except DexError as e:
            assert msg in str(e)
    
    def test_multiple_dex_errors_independent(self):
        """Verify multiple DexError instances are independent."""
        e1 = DexError("Error 1")
        e2 = DexError("Error 2")
        
        assert "Error 1" in str(e1)
        assert "Error 2" in str(e2)
        assert "Error 2" not in str(e1)
        assert "Error 1" not in str(e2)


# =============================================================================
# DexError Common Patterns Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorCommonPatterns:
    """Tests for common DexError usage patterns."""
    
    def test_error_with_context_manager(self):
        """Test DexError works with pytest.raises context manager."""
        with pytest.raises(DexError, match="expected"):
            raise DexError("This is an expected error")
    
    def test_error_comparison(self):
        """Test DexError comparison behavior."""
        e1 = DexError("Same message")
        e2 = DexError("Same message")
        
        # Two distinct exception instances are not equal even with same message
        assert e1 is not e2
    
    def test_error_repr_contains_message(self):
        """Test DexError repr contains message."""
        msg = "Snapshot failed"
        error = DexError(msg)
        repr_str = repr(error)
        
        # repr should include the error type and message
        assert "DexError" in repr_str or msg in repr_str
    
    def test_error_str_and_repr_consistent(self):
        """Test DexError str and repr are consistent."""
        msg = "Test error for consistency"
        error = DexError(msg)
        
        str_result = str(error)
        repr_result = repr(error)
        
        # Both should contain the message
        assert msg in str_result
        # repr might wrap it differently
        assert msg in repr_result or "DexError" in repr_result


# =============================================================================
# DexError Production Scenarios Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestDexErrorProductionScenarios:
    """Tests for production error handling scenarios."""
    
    def test_error_in_function_return(self):
        """Test returning DexError vs raising."""
        def might_fail(should_fail: bool):
            if should_fail:
                raise DexError("Operation failed")
            return "success"
        
        assert might_fail(False) == "success"
        
        with pytest.raises(DexError):
            might_fail(True)
    
    def test_error_logging_pattern(self):
        """Test common error logging pattern."""
        errors_logged = []
        
        def log_error(e):
            errors_logged.append(str(e))
        
        try:
            raise DexError("Connection timeout")
        except DexError as e:
            log_error(e)
        
        assert len(errors_logged) == 1
        assert "timeout" in errors_logged[0].lower()
    
    def test_error_recovery_pattern(self):
        """Test common error recovery pattern."""
        attempt_count = 0
        
        def operation_with_retry(max_attempts=3):
            nonlocal attempt_count
            
            for i in range(max_attempts):
                attempt_count += 1
                try:
                    if i < 2:
                        raise DexError(f"Attempt {i+1} failed")
                    return "success"
                except DexError:
                    if i == max_attempts - 1:
                        raise  # Re-raise on final attempt
                    continue  # Retry on earlier attempts
            return "success"
        
        result = operation_with_retry()
        assert result == "success"
        assert attempt_count == 3
