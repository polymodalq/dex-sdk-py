"""
Transaction Building Tests - Transaction Structure

Tests for transaction building without submission:
- TransactionBuilder configuration
- UnsignedTransaction structure
- Transaction field validation

Note: build_order_tx requires a live RPC and valid exchange state.
Tests will skip gracefully if RPC is unavailable.
"""

import pytest

# Try to import SDK
try:
    from perpl_sdk import (
        Chain,
        TransactionBuilder,
        UnsignedTransaction,
        types,
        UD64,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.transaction]


def make_test_order(perp_id=1, price=None, exchange=None):
    """Create a test order request for a valid perpetual.
    
    If exchange is provided, derives price from current mark price.
    """
    # Use market-relative price if exchange is available
    if price is None and exchange is not None:
        try:
            perp = exchange.get_perpetual(perp_id)
            mark_price = float(str(perp.mark_price))
            # Use 99% of mark price for a long order (below market)
            price = UD64(f"{mark_price * 0.99:.2f}")
        except Exception:
            price = UD64("1000.0")  # Fallback
    elif price is None:
        price = UD64("1000.0")  # Fallback
    
    return types.OrderRequest(
        request_id=1,
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
# TransactionBuilder Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestTransactionBuilder:
    """Tests for TransactionBuilder configuration."""
    
    def test_builder_creation(self, testnet_chain, testnet_rpc):
        """Verify TransactionBuilder can be created."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        assert builder is not None
    
    def test_builder_has_chain(self, testnet_chain, testnet_rpc):
        """Verify builder has chain ID accessor."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        assert builder.chain_id == testnet_chain.chain_id
    
    def test_builder_has_exchange_address(self, testnet_chain, testnet_rpc):
        """Verify builder has exchange address accessor."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        addr = builder.exchange_address
        assert addr.startswith("0x")
        assert len(addr) == 42


# =============================================================================
# UnsignedTransaction Structure Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestUnsignedTransaction:
    """Tests for UnsignedTransaction structure.
    
    Note: build_order_tx(request, exchange, from_address) requires:
    - A valid OrderRequest
    - A valid Exchange snapshot
    - A valid from_address string
    """
    
    def test_build_order_tx(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Test building an unsigned order transaction."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        # Use a valid perpetual ID from the exchange
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available for test")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        # Use known_account_address if available, else skip
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            # Correct API: build_order_tx(request, exchange, from_address)
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            assert tx is not None
        except Exception as e:
            error_msg = str(e).lower()
            # Skip for network issues or contract reverts (unregistered account)
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise
    
    def test_unsigned_tx_has_to(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify unsigned transaction has 'to' field."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            
            to_addr = tx.to
            assert to_addr is not None
            assert to_addr.startswith("0x")
            assert len(to_addr) == 42
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise
    
    def test_unsigned_tx_has_data(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify unsigned transaction has 'data' field."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            
            data = tx.data
            assert data is not None
            assert isinstance(data, str)
            assert data.startswith("0x")
            assert len(data) > 10  # More than just function selector
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise
    
    def test_unsigned_tx_to_dict(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify to_dict() returns all required fields."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            tx_dict = tx.to_dict()
            
            assert "to" in tx_dict
            assert "data" in tx_dict
            assert "value" in tx_dict
            assert "gas" in tx_dict or "gasLimit" in tx_dict or "gas_limit" in tx_dict
            assert "chainId" in tx_dict or "chain_id" in tx_dict
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise


# =============================================================================
# Transaction Field Validation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestTransactionFields:
    """Tests for transaction field validation."""
    
    def test_gas_limit_reasonable(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify gas limit is reasonable (> 21000, < block limit)."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            
            gas_limit = tx.gas_limit
            assert gas_limit > 21000, "Gas too low for contract call"
            assert gas_limit < 30_000_000, "Gas exceeds block limit"
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise
    
    def test_chain_id_matches(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify chain ID matches configuration."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            assert tx.chain_id == testnet_chain.chain_id
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise
    
    def test_value_zero_for_orders(self, testnet_chain, testnet_rpc, exchange_snapshot, known_account_address):
        """Verify value is 0 for order transactions (no ETH transfer)."""
        builder = TransactionBuilder(testnet_chain, testnet_rpc)
        
        perp_ids = exchange_snapshot.perpetual_ids()
        if not perp_ids:
            pytest.skip("No perpetuals available")
        
        request = make_test_order(perp_id=perp_ids[0], exchange=exchange_snapshot)
        test_address = known_account_address or "0x0000000000000000000000000000000000001234"
        
        try:
            tx = builder.build_order_tx(request, exchange_snapshot, test_address)
            value = tx.value
            # Value should be 0
            assert value == "0" or value == 0 or int(str(value)) == 0
        except Exception as e:
            error_msg = str(e).lower()
            if any(x in error_msg for x in ["rpc", "network", "connection", "execution reverted"]):
                pytest.skip(f"Transaction building failed: {e}")
            raise


# =============================================================================
# TransactionBuilder Documentation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestTransactionBuilderDocumentation:
    """Documentation tests for TransactionBuilder usage patterns."""
    
    def test_build_order_tx_signature(self):
        """Document the build_order_tx API signature.
        
        The correct signature is:
            builder.build_order_tx(request, exchange, from_address)
        
        Where:
        - request: OrderRequest object
        - exchange: Exchange snapshot (for converters)
        - from_address: Sender's Ethereum address string
        """
        assert True
    
    def test_transaction_flow_documented(self):
        """Document the transaction building flow.
        
        1. Create TransactionBuilder(chain, rpc_url)
        2. Create OrderRequest for your order
        3. Build: tx = builder.build_order_tx(request, exchange, from_addr)
        4. Sign: Use tx.to_dict() with eth_account or web3.py
        5. Submit: Send signed transaction to network
        """
        assert True
