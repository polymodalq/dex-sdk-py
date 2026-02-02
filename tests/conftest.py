"""
Pytest Configuration and Fixtures

This module provides shared fixtures for all test categories:
- Unit tests: Mock data and offline fixtures
- Integration tests: Testnet RPC and snapshot fixtures
- Validation tests: Cross-reference helpers
- Transaction tests: Builder fixtures
"""

import os
import json
import pytest
from pathlib import Path
from decimal import Decimal
from typing import Optional, Dict, Any

# Import SDK - this will fail if not built, which is expected pre-build
try:
    from perpl_sdk import (
        Chain,
        SnapshotBuilder,
        Exchange,
        UD64,
        UD128,
        D256,
        types,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

# Default testnet RPC URL (can be overridden via environment)
DEFAULT_TESTNET_RPC = "https://testnet.monad.xyz"

# Fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers programmatically if needed
    pass


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    # Skip integration/validation tests if no RPC available
    rpc_url = os.environ.get("TESTNET_RPC", "")
    
    for item in items:
        # Skip SDK-dependent tests if SDK not available
        if not SDK_AVAILABLE and "unit" not in [m.name for m in item.iter_markers()]:
            item.add_marker(pytest.mark.skip(reason="SDK not built"))
        
        # Skip integration tests if no RPC URL
        if "integration" in [m.name for m in item.iter_markers()] and not rpc_url:
            item.add_marker(pytest.mark.skip(reason="TESTNET_RPC not set"))
        
        if "validation" in [m.name for m in item.iter_markers()] and not rpc_url:
            item.add_marker(pytest.mark.skip(reason="TESTNET_RPC not set"))


# =============================================================================
# Session-Scoped Fixtures (Expensive, shared across all tests)
# =============================================================================

@pytest.fixture(scope="session")
def testnet_rpc() -> str:
    """Get testnet RPC URL from environment or default."""
    return os.environ.get("TESTNET_RPC", DEFAULT_TESTNET_RPC)


@pytest.fixture(scope="session")
def testnet_chain():
    """Get testnet chain configuration."""
    if not SDK_AVAILABLE:
        pytest.skip("SDK not available")
    return Chain.testnet()


@pytest.fixture(scope="session")
def exchange_snapshot(testnet_chain, testnet_rpc):
    """
    Build and cache an exchange snapshot for the test session.
    
    This is expensive (network calls), so we cache it at session scope.
    All tests that need a snapshot share this single instance.
    """
    if not SDK_AVAILABLE:
        pytest.skip("SDK not available")
    
    builder = SnapshotBuilder(testnet_chain, testnet_rpc)
    # Fetch all perpetuals, no specific accounts
    try:
        exchange = builder.build()
    except Exception as e:
        error_msg = str(e).lower()
        if "not a contract" in error_msg or "returned no data" in error_msg:
            pytest.skip(
                f"Exchange contract not deployed at {testnet_chain.exchange}. "
                "Check Chain.testnet() configuration matches deployed contract."
            )
        # Handle HTTP errors (405, 429, etc.) and transport errors
        if "http error" in error_msg or "transport error" in error_msg:
            pytest.skip(
                f"RPC endpoint unavailable or returned error: {e}. "
                f"Check TESTNET_RPC environment variable or use a working RPC endpoint."
            )
        # Handle connection errors
        if "connection" in error_msg or "timeout" in error_msg:
            pytest.skip(f"Could not connect to RPC endpoint: {e}")
        raise
    return exchange


@pytest.fixture(scope="session")
def w3_provider(testnet_rpc):
    """
    Create a Web3 provider for cross-reference validation.
    
    This is used to make direct RPC calls to compare against SDK results.
    """
    try:
        from web3 import Web3
        return Web3(Web3.HTTPProvider(testnet_rpc))
    except ImportError:
        pytest.skip("web3 not installed")


# =============================================================================
# Function-Scoped Fixtures (Fresh per test)
# =============================================================================

@pytest.fixture
def sample_ud64():
    """Create a sample UD64 value for testing."""
    if not SDK_AVAILABLE:
        pytest.skip("SDK not available")
    return UD64("1234.567890")


@pytest.fixture
def sample_ud128():
    """Create a sample UD128 value for testing."""
    if not SDK_AVAILABLE:
        pytest.skip("SDK not available")
    return UD128("1000000000.123456789012345678")


@pytest.fixture
def sample_d256():
    """Create a sample D256 value for testing."""
    if not SDK_AVAILABLE:
        pytest.skip("SDK not available")
    return D256("-12345678901234567890.123456789")


@pytest.fixture
def sample_order_request(testnet_chain):
    """Create a sample order request for testing."""
    if not SDK_AVAILABLE:
        pytest.skip("SDK not available")
    
    return types.OrderRequest(
        request_id=1,
        perp_id=0,
        type=types.RequestType.OpenLong,
        order_id=None,
        price=UD64("100.0"),
        size=UD64("1.0"),
        expiry_block=None,
        post_only=True,
        fill_or_kill=False,
        immediate_or_cancel=False,
        max_matches=None,
        leverage=UD64("5.0"),
        last_exec_block=None,
        amount=None,
    )


@pytest.fixture
def known_account_address() -> str:
    """
    Return a known account address that exists on testnet.
    
    This should be an address that has positions for validation tests.
    Override via environment variable if needed.
    """
    return os.environ.get(
        "TEST_ACCOUNT_ADDRESS",
        "0x0000000000000000000000000000000000000000"  # Placeholder
    )


# =============================================================================
# Fixture Data Loading
# =============================================================================

@pytest.fixture
def expected_values() -> Dict[str, Any]:
    """Load expected values from fixtures file."""
    fixture_path = FIXTURES_DIR / "expected_values.json"
    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)
    return {}


@pytest.fixture
def liquidation_test_cases(expected_values) -> list:
    """Get liquidation price test cases from fixtures."""
    return expected_values.get("liquidation_test_cases", [])


# =============================================================================
# Helper Functions (Available to all tests)
# =============================================================================

def assert_decimal_equal(
    actual: Any,
    expected: Any,
    decimals: int = 6,
    msg: str = ""
) -> None:
    """
    Assert two decimal values are equal within precision.
    
    Args:
        actual: Actual value (UD64, UD128, D256, or numeric string)
        expected: Expected value
        decimals: Number of decimal places for comparison
        msg: Optional message on failure
    """
    # Convert to Decimal for comparison
    actual_dec = Decimal(str(actual))
    expected_dec = Decimal(str(expected))
    
    # Calculate tolerance
    tolerance = Decimal(10) ** (-decimals)
    
    diff = abs(actual_dec - expected_dec)
    assert diff <= tolerance, (
        f"{msg}\nExpected: {expected_dec}\nActual: {actual_dec}\n"
        f"Difference: {diff} > tolerance {tolerance}"
    )


def assert_price_ordered(bids: list, asks: list) -> None:
    """Assert order book is properly ordered (no crossed book)."""
    if bids and asks:
        best_bid = bids[0][0] if bids else None
        best_ask = asks[0][0] if asks else None
        
        if best_bid is not None and best_ask is not None:
            assert float(str(best_bid)) < float(str(best_ask)), (
                f"Crossed book: best bid {best_bid} >= best ask {best_ask}"
            )


def assert_sorted_descending(values: list, key=None) -> None:
    """Assert a list is sorted in descending order."""
    if key:
        extracted = [key(v) for v in values]
    else:
        extracted = list(values)
    
    for i in range(len(extracted) - 1):
        assert float(str(extracted[i])) >= float(str(extracted[i + 1])), (
            f"Not sorted descending at index {i}: {extracted[i]} < {extracted[i + 1]}"
        )


def assert_sorted_ascending(values: list, key=None) -> None:
    """Assert a list is sorted in ascending order."""
    if key:
        extracted = [key(v) for v in values]
    else:
        extracted = list(values)
    
    for i in range(len(extracted) - 1):
        assert float(str(extracted[i])) <= float(str(extracted[i + 1])), (
            f"Not sorted ascending at index {i}: {extracted[i]} > {extracted[i + 1]}"
        )


# Make helpers available to tests
@pytest.fixture
def decimal_assert():
    """Provide decimal assertion helper."""
    return assert_decimal_equal


@pytest.fixture
def orderbook_assert():
    """Provide order book assertion helpers."""
    return {
        "price_ordered": assert_price_ordered,
        "sorted_desc": assert_sorted_descending,
        "sorted_asc": assert_sorted_ascending,
    }
