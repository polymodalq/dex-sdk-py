"""
Integration Tests for Converter Class

Tests for the precision converter:
- Decimals property
- String representation
- Access via Exchange.collateral_converter
- Access via Perpetual converters

Note: These tests require a live RPC connection to fetch converter data.
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import Converter, Chain, SnapshotBuilder
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.integration]


# =============================================================================
# Converter Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConverterBasic:
    """Basic tests for Converter class."""
    
    def test_converter_type_exists(self):
        """Verify Converter type is importable."""
        assert Converter is not None
    
    def test_converter_repr(self, exchange_snapshot):
        """Verify Converter has a string representation."""
        converter = exchange_snapshot.collateral_converter
        repr_str = repr(converter)
        
        assert "Converter" in repr_str
        assert "decimals" in repr_str


# =============================================================================
# Converter Decimals Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConverterDecimals:
    """Tests for Converter decimals property."""
    
    def test_collateral_converter_has_decimals(self, exchange_snapshot):
        """Verify collateral converter has decimals."""
        converter = exchange_snapshot.collateral_converter
        decimals = converter.decimals
        
        assert isinstance(decimals, int)
        assert decimals >= 0
        assert decimals <= 18  # Most tokens have <= 18 decimals
    
    def test_collateral_decimals_reasonable(self, exchange_snapshot):
        """Verify collateral decimals is a reasonable value."""
        converter = exchange_snapshot.collateral_converter
        decimals = converter.decimals
        
        # Common values: 6 (USDC/USDT), 8 (WBTC), 18 (ETH/most ERC20)
        assert decimals in [6, 8, 18], f"Unusual decimals value: {decimals}"


# =============================================================================
# Perpetual Converter Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualConverters:
    """Tests for Perpetual-specific converters."""
    
    def test_price_converter_exists(self, exchange_snapshot):
        """Verify perpetuals have price converters."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            converter = perp.price_converter
            
            assert converter is not None
            assert isinstance(converter.decimals, int)
    
    def test_size_converter_exists(self, exchange_snapshot):
        """Verify perpetuals have size converters."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            converter = perp.size_converter
            
            assert converter is not None
            assert isinstance(converter.decimals, int)
    
    def test_leverage_converter_exists(self, exchange_snapshot):
        """Verify perpetuals have leverage converters."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            converter = perp.leverage_converter
            
            assert converter is not None
            assert isinstance(converter.decimals, int)
    
    def test_fee_converter_exists(self, exchange_snapshot):
        """Verify perpetuals have fee converters."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            converter = perp.fee_converter
            
            assert converter is not None
            assert isinstance(converter.decimals, int)
    
    def test_funding_rate_converter_exists(self, exchange_snapshot):
        """Verify perpetuals have funding rate converters."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            converter = perp.funding_rate_converter
            
            assert converter is not None
            assert isinstance(converter.decimals, int)


# =============================================================================
# Converter Consistency Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestConverterConsistency:
    """Tests for converter consistency across perpetuals."""
    
    def test_all_perpetuals_have_same_leverage_decimals(self, exchange_snapshot):
        """Verify all perpetuals use consistent leverage decimals."""
        perp_ids = exchange_snapshot.perpetual_ids()
        if len(perp_ids) < 2:
            pytest.skip("Need at least 2 perpetuals for consistency check")
        
        decimals_values = []
        for perp_id in perp_ids:
            perp = exchange_snapshot.get_perpetual(perp_id)
            decimals_values.append(perp.leverage_converter.decimals)
        
        # All should be the same
        assert len(set(decimals_values)) == 1, (
            f"Inconsistent leverage decimals across perpetuals: {decimals_values}"
        )
    
    def test_converter_decimals_are_positive_or_zero(self, exchange_snapshot):
        """Verify all converter decimals are non-negative."""
        converter = exchange_snapshot.collateral_converter
        assert converter.decimals >= 0
        
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            assert perp.price_converter.decimals >= 0
            assert perp.size_converter.decimals >= 0
            assert perp.leverage_converter.decimals >= 0
            assert perp.fee_converter.decimals >= 0
            assert perp.funding_rate_converter.decimals >= 0
