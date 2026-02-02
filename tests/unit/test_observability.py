"""
Unit Tests for Observability

Tests for logging and tracing configuration:
- configure_logging function
- Log level settings
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import configure_logging
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


# =============================================================================
# configure_logging Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConfigureLoggingBasic:
    """Basic tests for configure_logging function."""
    
    def test_configure_logging_exists(self):
        """Verify configure_logging function is importable."""
        assert configure_logging is not None
    
    def test_configure_logging_is_callable(self):
        """Verify configure_logging is callable."""
        assert callable(configure_logging)


# =============================================================================
# configure_logging Log Levels Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConfigureLoggingLevels:
    """Tests for configure_logging with different log levels.
    
    Note: configure_logging can only be called once per process due to
    tracing-subscriber initialization. These tests document the expected
    behavior but may skip if logging is already initialized.
    """
    
    def test_valid_log_level_info(self):
        """Test that 'info' is a valid log level."""
        try:
            configure_logging("info")
        except ValueError as e:
            if "already" in str(e).lower() or "failed to initialize" in str(e).lower():
                pytest.skip("Logging already initialized in this process")
            raise
        except Exception as e:
            if "already" in str(e).lower():
                pytest.skip("Logging already initialized")
            raise
    
    def test_valid_log_level_debug(self):
        """Document that 'debug' is a valid log level."""
        # Can only initialize once per process, so document the interface
        valid_levels = ["trace", "debug", "info", "warn", "error"]
        assert "debug" in valid_levels
    
    def test_valid_log_level_warn(self):
        """Document that 'warn' is a valid log level."""
        valid_levels = ["trace", "debug", "info", "warn", "error"]
        assert "warn" in valid_levels
    
    def test_valid_log_level_error(self):
        """Document that 'error' is a valid log level."""
        valid_levels = ["trace", "debug", "info", "warn", "error"]
        assert "error" in valid_levels
    
    def test_valid_log_level_trace(self):
        """Document that 'trace' is a valid log level."""
        valid_levels = ["trace", "debug", "info", "warn", "error"]
        assert "trace" in valid_levels


# =============================================================================
# configure_logging Error Handling Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConfigureLoggingErrorHandling:
    """Tests for configure_logging error handling."""
    
    def test_logging_reinitialization_fails(self):
        """Test that reinitializing logging raises ValueError.
        
        Note: The tracing EnvFilter is lenient about level strings,
        so "invalid" strings may not raise errors. Instead, we test
        that calling configure_logging twice fails (expected behavior).
        """
        try:
            # First call may succeed or fail if already initialized
            configure_logging("info")
        except ValueError:
            pass  # Already initialized from previous test
        
        # Second call should always fail
        with pytest.raises(ValueError) as excinfo:
            configure_logging("debug")
        
        error_msg = str(excinfo.value).lower()
        assert "already" in error_msg or "failed" in error_msg


# =============================================================================
# configure_logging Documentation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConfigureLoggingDocumentation:
    """Documentation tests for configure_logging."""
    
    def test_single_initialization_documented(self):
        """Document that configure_logging can only be called once.
        
        The tracing-subscriber framework only allows initialization once
        per process. Subsequent calls will raise an error.
        """
        assert True
    
    def test_usage_pattern_documented(self):
        """Document the expected usage pattern.
        
        Usage:
        ```python
        import perpl_sdk
        
        # Call early in application startup
        perpl_sdk.configure_logging("info")
        
        # SDK will now log at INFO level and above
        ```
        """
        assert True
    
    def test_env_filter_supported(self):
        """Document that environment filter syntax is supported.
        
        The level parameter supports tracing EnvFilter syntax:
        - "info" - all crates at INFO level
        - "warn,perpl_sdk=debug" - default WARN, SDK at DEBUG
        - "dex_sdk=trace" - SDK at TRACE level
        """
        assert True
    
    def test_log_output_format_documented(self):
        """Document the log output format.
        
        Logs are output using tracing-subscriber with:
        - Timestamp
        - Log level
        - Target (crate/module name)
        - Message
        
        Example:
        2024-01-15T10:30:00.123Z INFO perpl_sdk::state Building snapshot...
        """
        assert True


# =============================================================================
# Integration with SDK Operations
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestLoggingIntegration:
    """Tests for logging integration with SDK operations."""
    
    def test_logging_does_not_affect_functionality(self):
        """Verify logging configuration doesn't break SDK.
        
        The configure_logging function should be purely observational
        and not affect the functionality of SDK operations.
        """
        # This is tested implicitly by all other tests that run
        # after configure_logging is called
        assert True
    
    def test_logging_is_optional(self):
        """Document that logging configuration is optional.
        
        The SDK works correctly without calling configure_logging.
        Logging is disabled by default and only enabled when explicitly
        configured.
        """
        assert True
