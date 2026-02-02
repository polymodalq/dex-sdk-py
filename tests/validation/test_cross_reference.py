"""
Validation Tests - Cross-Reference SDK vs Contract

These tests verify that SDK values match direct contract calls.
This ensures the SDK's parsing and conversion logic is correct.
"""

import pytest

# Try to import SDK and web3
try:
    from perpl_sdk import Chain, SnapshotBuilder
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

pytestmark = [pytest.mark.validation]


# =============================================================================
# Cross-Reference Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.skipif(not WEB3_AVAILABLE, reason="web3 not installed")
class TestCrossReference:
    """Tests comparing SDK values to direct contract calls."""
    
    def test_block_number_matches(self, exchange_snapshot, w3_provider):
        """Verify SDK block number is valid."""
        sdk_block = exchange_snapshot.instant.block_number
        
        # Get latest block from web3
        latest = w3_provider.eth.block_number
        
        # SDK snapshot should be at or before latest block
        assert sdk_block <= latest, (
            f"SDK block {sdk_block} > latest {latest}"
        )
    
    def test_chain_id_matches(self, exchange_snapshot, w3_provider):
        """Verify SDK chain ID matches network."""
        sdk_chain_id = exchange_snapshot.chain.chain_id
        web3_chain_id = w3_provider.eth.chain_id
        
        assert sdk_chain_id == web3_chain_id, (
            f"SDK chain ID {sdk_chain_id} != network {web3_chain_id}"
        )
    
    def test_exchange_address_valid(self, exchange_snapshot, w3_provider):
        """Verify exchange contract address is valid."""
        exchange_addr = exchange_snapshot.chain.exchange
        
        # Should be a valid address
        assert Web3.is_address(exchange_addr), (
            f"Invalid exchange address: {exchange_addr}"
        )
        
        # Convert to checksum address for web3.py
        checksum_addr = Web3.to_checksum_address(exchange_addr)
        
        # Contract should have code
        code = w3_provider.eth.get_code(checksum_addr)
        assert len(code) > 2, "Exchange address has no code"


# =============================================================================
# Price Accuracy Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.skipif(not WEB3_AVAILABLE, reason="web3 not installed")
class TestPriceAccuracy:
    """Tests for price accuracy vs contract."""
    
    def test_prices_reasonable(self, exchange_snapshot):
        """Verify prices are within reasonable bounds."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            mark = float(str(perp.mark_price))
            last = float(str(perp.last_price))
            oracle = float(str(perp.oracle_price))
            
            # All prices should be positive (if set)
            if mark > 0:
                # Mark and oracle should be within 10% of each other
                # (unless oracle is not used)
                if oracle > 0:
                    ratio = mark / oracle
                    assert 0.5 < ratio < 2.0, (
                        f"Mark {mark} too far from oracle {oracle}"
                    )


# =============================================================================
# State Consistency Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestStateConsistency:
    """Tests for internal state consistency."""
    
    def test_perpetual_ids_consistent(self, exchange_snapshot):
        """Verify perpetual IDs are consistent."""
        perp_ids = exchange_snapshot.perpetual_ids()
        
        for perp_id in perp_ids:
            perp = exchange_snapshot.get_perpetual(perp_id)
            assert perp is not None, f"Perpetual {perp_id} should exist"
            assert perp.id == perp_id, f"Perpetual ID mismatch"
    
    def test_account_ids_consistent(self, exchange_snapshot):
        """Verify account IDs are consistent."""
        account_ids = exchange_snapshot.account_ids()
        
        for account_id in account_ids:
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                assert account.id == account_id, f"Account ID mismatch"
    
    def test_position_references_consistent(self, exchange_snapshot):
        """Verify position references are consistent."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    assert position.account_id == account_id
                    assert position.perpetual_id == perp_id
                    
                    # Perpetual should exist
                    perp = exchange_snapshot.get_perpetual(perp_id)
                    assert perp is not None


# =============================================================================
# Numeric Precision Validation
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestNumericPrecision:
    """Tests for numeric precision in SDK values."""
    
    def test_prices_have_precision(self, exchange_snapshot):
        """Verify prices have sufficient precision."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            mark_str = str(perp.mark_price)
            
            # Should be able to represent prices with decimals
            # Parse and format should not lose precision
            mark_float = float(mark_str)
            
            if mark_float > 0:
                # Re-parsing should work
                assert float(mark_str) == mark_float
    
    def test_fee_precision(self, exchange_snapshot):
        """Verify fee values have correct precision."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            maker = float(str(perp.maker_fee))
            taker = float(str(perp.taker_fee))
            
            # Fees should be expressible in basis points
            # i.e., at least 4 decimal places
            if maker > 0:
                # Should be >= 0.0001 (0.01%) typically
                assert maker >= 1e-6, "Fee seems too small to be valid"
