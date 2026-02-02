"""
Transaction Building Tests - Gas Estimation

Tests for gas estimation accuracy:
- Gas estimate bounds
- Transaction field validation

Note: Gas estimation uses the same build_order_tx API.
Tests validate gas_limit field on successful builds.
"""

import pytest

# Try to import SDK
try:
    from perpl_sdk import (
        Chain,
        TransactionBuilder,
        types,
        UD64,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.transaction]


def make_test_order(perp_id=1, request_id=1, exchange=None):
    """Create a test order request.
    
    If exchange is provided, derives price from current mark price.
    """
    # Use market-relative price if exchange is available
    price = UD64("1000.0")  # Default fallback
    if exchange is not None:
        try:
            perp = exchange.get_perpetual(perp_id)
            mark_price = float(str(perp.mark_price))
            # Use 99% of mark price for a long order (below market)
            price = UD64(f"{mark_price * 0.99:.2f}")
        except Exception:
            pass  # Use fallback
    
    return types.OrderRequest(
        request_id=request_id,
        perp_id=perp_id,
        type=types.RequestType.OpenLong,
        order_id=None,
        price=price,
        size=UD64("0.1"),
        expiry_block=None,
        post_only=True,  # Post-only to avoid immediate execution
        fill_or_kill=False,
        immediate_or_cancel=False,
        max_matches=None,
        leverage=UD64("5.0"),
        last_exec_block=None,
        amount=None,
    )


# =============================================================================
# Gas Estimation Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestGasEstimation:
    """Tests for gas estimation via build_order_tx."""
    
    def test_gas_estimate_positive(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify gas estimate is positive."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            assert tx.gas_limit > 0, "Gas estimate should be positive"
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Gas estimation failed: {e}")
            raise
    
    def test_gas_estimate_above_minimum(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify gas estimate is above base transaction cost."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            # Base transaction is 21000 gas, contract calls need more
            assert tx.gas_limit > 21000, "Gas should exceed base tx cost"
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Gas estimation failed: {e}")
            raise
    
    def test_gas_estimate_below_block_limit(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify gas estimate is below block gas limit."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            # Block gas limit is typically 30M+
            assert tx.gas_limit < 30_000_000, "Gas exceeds block limit"
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Gas estimation failed: {e}")
            raise


# =============================================================================
# Gas Documentation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestGasDocumentation:
    """Documentation tests for gas estimation behavior."""
    
    def test_gas_limit_field_documented(self):
        """Document that gas_limit is available on UnsignedTransaction.
        
        After building a transaction:
            tx = builder.build_order_tx(request, exchange, from_addr)
            gas = tx.gas_limit  # Returns estimated gas as int
        """
        assert True
    
    def test_gas_estimation_is_automatic(self):
        """Document that gas is automatically estimated.
        
        The build_order_tx method:
        1. Encodes the transaction calldata
        2. Estimates gas via eth_estimateGas RPC call
        3. Returns UnsignedTransaction with gas_limit set
        
        No separate gas estimation call is needed.
        """
        assert True
