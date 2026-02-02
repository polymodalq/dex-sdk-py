"""
Unit Tests for Chain Configuration

Tests for:
- Chain.testnet() configuration
- Chain.custom() configuration
- Chain attributes
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import Chain
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


# =============================================================================
# Chain.testnet() Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestChainTestnet:
    """Tests for testnet chain configuration."""
    
    def test_testnet_creates_chain(self):
        """Verify Chain.testnet() returns a valid chain."""
        chain = Chain.testnet()
        assert chain is not None
    
    def test_testnet_has_chain_id(self):
        """Verify testnet has a chain ID."""
        chain = Chain.testnet()
        chain_id = chain.chain_id
        assert chain_id is not None
        assert isinstance(chain_id, int)
        assert chain_id > 0
    
    def test_testnet_has_exchange_address(self):
        """Verify testnet has an exchange address."""
        chain = Chain.testnet()
        exchange = chain.exchange
        assert exchange is not None
        assert isinstance(exchange, str)
        assert exchange.startswith("0x")
        assert len(exchange) == 42  # 0x + 40 hex chars
    
    def test_testnet_has_collateral_token(self):
        """Verify testnet has a collateral token address."""
        chain = Chain.testnet()
        token = chain.collateral_token
        assert token is not None
        assert isinstance(token, str)
        assert token.startswith("0x")
    
    def test_testnet_has_perpetuals(self):
        """Verify testnet has perpetual IDs configured."""
        chain = Chain.testnet()
        perps = chain.perpetuals
        assert perps is not None
        assert isinstance(perps, (list, tuple))
        assert len(perps) > 0
    
    def test_testnet_has_deployed_at_block(self):
        """Verify testnet has deployment block."""
        chain = Chain.testnet()
        block = chain.deployed_at_block
        assert block is not None
        assert isinstance(block, int)
        assert block >= 0
    
    def test_testnet_repr(self):
        """Test testnet string representation."""
        chain = Chain.testnet()
        repr_str = repr(chain)
        assert "Chain" in repr_str or "testnet" in repr_str.lower()


# =============================================================================
# Chain.custom() Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestChainCustom:
    """Tests for custom chain configuration."""
    
    def test_custom_creates_chain(self):
        """Verify Chain.custom() returns a valid chain."""
        chain = Chain.custom(
            chain_id=12345,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=1000000,
            exchange="0x0987654321098765432109876543210987654321",
            perpetuals=[0, 1, 2],
        )
        assert chain is not None
    
    def test_custom_chain_id(self):
        """Verify custom chain ID is set correctly."""
        expected_id = 54321
        chain = Chain.custom(
            chain_id=expected_id,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=1000000,
            exchange="0x0987654321098765432109876543210987654321",
            perpetuals=[0],
        )
        assert chain.chain_id == expected_id
    
    def test_custom_exchange_address(self):
        """Verify custom exchange address is set correctly."""
        expected_addr = "0xabcdef1234567890abcdef1234567890abcdef12"
        chain = Chain.custom(
            chain_id=1,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=0,
            exchange=expected_addr,
            perpetuals=[0],
        )
        assert chain.exchange.lower() == expected_addr.lower()
    
    def test_custom_perpetuals(self):
        """Verify custom perpetuals are set correctly."""
        expected_perps = [0, 1, 2, 3, 4]
        chain = Chain.custom(
            chain_id=1,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=0,
            exchange="0x0987654321098765432109876543210987654321",
            perpetuals=expected_perps,
        )
        assert list(chain.perpetuals) == expected_perps
    
    def test_custom_deployed_block(self):
        """Verify custom deployed block is set correctly."""
        expected_block = 5000000
        chain = Chain.custom(
            chain_id=1,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=expected_block,
            exchange="0x0987654321098765432109876543210987654321",
            perpetuals=[0],
        )
        assert chain.deployed_at_block == expected_block


# =============================================================================
# Chain Comparison Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestChainComparison:
    """Tests for chain comparison and equality."""
    
    def test_two_testnets_equal(self):
        """Two testnet chains should be equal."""
        chain1 = Chain.testnet()
        chain2 = Chain.testnet()
        # They should at least have the same attributes
        assert chain1.chain_id == chain2.chain_id
        assert chain1.exchange == chain2.exchange
    
    def test_custom_different_from_testnet(self):
        """Custom chain should be different from testnet."""
        testnet = Chain.testnet()
        custom = Chain.custom(
            chain_id=99999,
            collateral_token="0x0000000000000000000000000000000000000000",
            deployed_at_block=0,
            exchange="0x0000000000000000000000000000000000000001",
            perpetuals=[0],
        )
        assert testnet.chain_id != custom.chain_id


# =============================================================================
# Chain Validation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestChainValidation:
    """Tests for chain configuration validation."""
    
    def test_empty_perpetuals_allowed(self):
        """Empty perpetuals list should be allowed."""
        chain = Chain.custom(
            chain_id=1,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=0,
            exchange="0x0987654321098765432109876543210987654321",
            perpetuals=[],
        )
        assert len(chain.perpetuals) == 0
    
    def test_many_perpetuals(self):
        """Many perpetuals should be supported."""
        perps = list(range(100))
        chain = Chain.custom(
            chain_id=1,
            collateral_token="0x1234567890123456789012345678901234567890",
            deployed_at_block=0,
            exchange="0x0987654321098765432109876543210987654321",
            perpetuals=perps,
        )
        assert len(chain.perpetuals) == 100
