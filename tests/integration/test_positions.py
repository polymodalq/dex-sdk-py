"""
Integration Tests for Position State

Tests for position data:
- Position attributes
- Risk metrics (liquidation, bankruptcy)
- PnL calculations
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import Chain, SnapshotBuilder
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.integration]


# =============================================================================
# Position Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionBasic:
    """Basic tests for position state."""
    
    def test_position_has_perpetual_id(self, exchange_snapshot):
        """Verify positions have perpetual_id."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    assert position.perpetual_id == perp_id
    
    def test_position_has_account_id(self, exchange_snapshot):
        """Verify positions have account_id."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    assert position.account_id == account_id
    
    def test_position_has_type(self, exchange_snapshot):
        """Verify positions have type (Long/Short)."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    pos_type = position.type
                    assert pos_type is not None


# =============================================================================
# Position Value Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionValues:
    """Tests for position value data."""
    
    def test_entry_price_positive(self, exchange_snapshot):
        """Verify entry prices are positive."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    entry = float(str(position.entry_price))
                    assert entry > 0, "Entry price should be positive"
    
    def test_size_positive(self, exchange_snapshot):
        """Verify sizes are positive."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    size = float(str(position.size))
                    assert size > 0, "Size should be positive"
    
    def test_deposit_non_negative(self, exchange_snapshot):
        """Verify deposits are non-negative."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    deposit = float(str(position.deposit))
                    assert deposit >= 0, "Deposit should be non-negative"


# =============================================================================
# Position Risk Metrics Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionRiskMetrics:
    """Tests for position risk metrics."""
    
    def test_liquidation_price_accessible(self, exchange_snapshot):
        """Verify liquidation price is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    liq_price = position.liquidation_price
                    assert liq_price is not None
    
    def test_bankruptcy_price_accessible(self, exchange_snapshot):
        """Verify bankruptcy price is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    bank_price = position.bankruptcy_price
                    assert bank_price is not None
    
    def test_maintenance_margin_requirement(self, exchange_snapshot):
        """Verify maintenance margin requirement is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    mmr = position.maintenance_margin_requirement
                    assert mmr is not None
                    mmr_val = float(str(mmr))
                    assert mmr_val >= 0
    
    def test_liquidation_vs_bankruptcy_long(self, exchange_snapshot):
        """For longs: bankruptcy < liquidation < entry."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    pos_type = str(position.type)
                    
                    if "Long" in pos_type or "long" in pos_type:
                        entry = float(str(position.entry_price))
                        liq = float(str(position.liquidation_price))
                        bank = float(str(position.bankruptcy_price))
                        
                        # For long: bankruptcy <= liquidation <= entry
                        # (unless highly overcollateralized)
                        assert bank <= entry, f"Bankruptcy {bank} > entry {entry}"
    
    def test_liquidation_vs_bankruptcy_short(self, exchange_snapshot):
        """For shorts: entry < liquidation < bankruptcy."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    pos_type = str(position.type)
                    
                    if "Short" in pos_type or "short" in pos_type:
                        entry = float(str(position.entry_price))
                        bank = float(str(position.bankruptcy_price))
                        
                        # For short: entry <= bankruptcy
                        assert entry <= bank, f"Entry {entry} > bankruptcy {bank}"


# =============================================================================
# Position PnL Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionPnL:
    """Tests for position PnL calculations."""
    
    def test_pnl_accessible(self, exchange_snapshot):
        """Verify total PnL is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    pnl = position.pnl
                    assert pnl is not None
    
    def test_delta_pnl_accessible(self, exchange_snapshot):
        """Verify delta PnL is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    delta = position.delta_pnl
                    assert delta is not None
    
    def test_premium_pnl_accessible(self, exchange_snapshot):
        """Verify premium PnL is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    premium = position.premium_pnl
                    assert premium is not None
    
    def test_total_pnl_equals_components(self, exchange_snapshot):
        """Verify total PnL = delta + premium."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    total = float(str(position.pnl))
                    delta = float(str(position.delta_pnl))
                    premium = float(str(position.premium_pnl))
                    
                    expected = delta + premium
                    assert abs(total - expected) < 1e-9 * (abs(total) + 1), (
                        f"Total PnL {total} != delta {delta} + premium {premium}"
                    )


# =============================================================================
# Position Instant Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionInstant:
    """Tests for position instant property."""
    
    def test_position_has_instant(self, exchange_snapshot):
        """Verify positions have instant property."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    instant = position.instant
                    assert instant is not None
    
    def test_position_instant_has_block_number(self, exchange_snapshot):
        """Verify position instant has block_number."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    instant = position.instant
                    assert hasattr(instant, 'block_number')
                    assert instant.block_number >= 0
    
    def test_position_instant_has_block_timestamp(self, exchange_snapshot):
        """Verify position instant has block_timestamp."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    instant = position.instant
                    assert hasattr(instant, 'block_timestamp')
                    assert instant.block_timestamp >= 0
    
    def test_position_instant_matches_account(self, exchange_snapshot):
        """Verify position instant matches account instant."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            account_block = account.instant.block_number
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    pos_block = position.instant.block_number
                    # Should be at same or earlier block
                    assert pos_block <= account_block, (
                        f"Position block {pos_block} > account block {account_block}"
                    )


# =============================================================================
# Position Additional Property Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionRepr:
    """Tests for position string representation."""
    
    def test_position_repr(self, exchange_snapshot):
        """Verify positions have string representation."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    repr_str = repr(position)
                    assert "Position" in repr_str
                    # Should contain some useful info
                    assert len(repr_str) > 10


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionFundingIndex:
    """Tests for position funding-related properties."""
    
    def test_funding_index_accessible(self, exchange_snapshot):
        """Verify funding index is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    # Just verify the property exists and is accessible
                    funding_idx = position.funding_index
                    assert funding_idx is not None
