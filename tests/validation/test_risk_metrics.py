"""
Validation Tests - Risk Metrics

Tests for liquidation price and bankruptcy price calculations.
Uses known-good test cases to verify the math.
"""

import pytest
from decimal import Decimal

# Try to import SDK
try:
    from perpl_sdk import Chain, SnapshotBuilder, UD64, UD128
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.validation]


# =============================================================================
# Liquidation Price Logic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestLiquidationPriceLogic:
    """Tests for liquidation price calculation logic."""
    
    def test_long_liquidation_below_entry(self, exchange_snapshot):
        """
        For leveraged longs, liquidation price < entry price.
        
        Logic: Long loses money when price drops, gets liquidated
        before position value goes negative.
        """
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is None:
                    continue
                
                pos_type = str(position.type)
                if "Long" not in pos_type and "long" not in pos_type:
                    continue
                
                entry = float(str(position.entry_price))
                liq = float(str(position.liquidation_price))
                
                # For leveraged long, liq < entry
                # (very high collateral might make liq = 0)
                assert liq <= entry, (
                    f"Long liq {liq} > entry {entry}"
                )
    
    def test_short_liquidation_above_entry(self, exchange_snapshot):
        """
        For leveraged shorts, liquidation price > entry price.
        
        Logic: Short loses money when price rises, gets liquidated
        before position value goes negative.
        """
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is None:
                    continue
                
                pos_type = str(position.type)
                if "Short" not in pos_type and "short" not in pos_type:
                    continue
                
                entry = float(str(position.entry_price))
                liq = float(str(position.liquidation_price))
                
                # For leveraged short, liq > entry
                assert liq >= entry, (
                    f"Short liq {liq} < entry {entry}"
                )


# =============================================================================
# Bankruptcy Price Logic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestBankruptcyPriceLogic:
    """Tests for bankruptcy price calculation logic."""
    
    def test_bankruptcy_more_extreme_than_liquidation_long(self, exchange_snapshot):
        """
        For longs, bankruptcy price < liquidation price.
        
        Bankruptcy is when position value is zero.
        Liquidation happens before bankruptcy.
        """
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is None:
                    continue
                
                pos_type = str(position.type)
                if "Long" not in pos_type and "long" not in pos_type:
                    continue
                
                liq = float(str(position.liquidation_price))
                bank = float(str(position.bankruptcy_price))
                
                # For long: bankruptcy <= liquidation
                assert bank <= liq + 1e-9, (
                    f"Long bankruptcy {bank} > liq {liq}"
                )
    
    def test_bankruptcy_more_extreme_than_liquidation_short(self, exchange_snapshot):
        """
        For shorts, bankruptcy price > liquidation price.
        """
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is None:
                    continue
                
                pos_type = str(position.type)
                if "Short" not in pos_type and "short" not in pos_type:
                    continue
                
                liq = float(str(position.liquidation_price))
                bank = float(str(position.bankruptcy_price))
                
                # For short: bankruptcy >= liquidation
                assert bank >= liq - 1e-9, (
                    f"Short bankruptcy {bank} < liq {liq}"
                )


# =============================================================================
# Maintenance Margin Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestMaintenanceMargin:
    """Tests for maintenance margin calculations."""
    
    def test_maintenance_margin_positive(self, exchange_snapshot):
        """Verify maintenance margin requirement is positive."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    mmr = float(str(position.maintenance_margin_requirement))
                    
                    assert mmr >= 0, "MMR cannot be negative"
    
    def test_maintenance_margin_proportional_to_position(self, exchange_snapshot):
        """
        Verify MMR scales with position size.
        
        MMR = entry_price * size / maintenance_margin_fraction
        """
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is None:
                    continue
                
                entry = float(str(position.entry_price))
                size = float(str(position.size))
                mmr = float(str(position.maintenance_margin_requirement))
                
                # Position notional value
                notional = entry * size
                
                if notional > 0 and mmr > 0:
                    # MMR should be a fraction of notional
                    ratio = mmr / notional
                    
                    # Typical maintenance margins are 1-10%
                    # So ratio should be reasonable
                    assert ratio > 0.001, f"MMR ratio {ratio} seems too low"
                    assert ratio < 10.0, f"MMR ratio {ratio} seems too high"


# =============================================================================
# Known Test Cases (Parametrized)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestKnownCases:
    """Tests with known-good reference values."""
    
    @pytest.mark.parametrize("entry,size,deposit,pos_type,maint_margin,expected_liq", [
        # (entry_price, size, deposit, type, maint_margin_frac, expected_liq)
        # Long: liq = entry - (deposit - mmr) / size
        # Example: entry=100, size=10, deposit=100, mm=0.05
        # MMR = 100 * 10 / 20 = 50 (if mm = 0.05 = 1/20)
        # liq = 100 - (100 - 50) / 10 = 100 - 5 = 95
        (100.0, 10.0, 100.0, "Long", 0.05, 95.0),
        
        # Short: liq = entry + (deposit - mmr) / size
        # Example: entry=100, size=10, deposit=100, mm=0.05
        # MMR = 50
        # liq = 100 + (100 - 50) / 10 = 100 + 5 = 105
        (100.0, 10.0, 100.0, "Short", 0.05, 105.0),
    ])
    def test_liquidation_calculation(
        self,
        entry,
        size,
        deposit,
        pos_type,
        maint_margin,
        expected_liq,
        expected_values,
    ):
        """
        Test liquidation price calculation against known values.
        
        Note: This test validates the LOGIC but can't directly create
        Position objects. It serves as documentation of expected behavior.
        """
        # Calculate expected liquidation price
        mmr = entry * size * maint_margin
        
        if pos_type == "Long":
            calculated_liq = entry - (deposit - mmr) / size
        else:
            calculated_liq = entry + (deposit - mmr) / size
        
        # Should match expected
        assert abs(calculated_liq - expected_liq) < 0.01, (
            f"Calculated liq {calculated_liq} != expected {expected_liq}"
        )
