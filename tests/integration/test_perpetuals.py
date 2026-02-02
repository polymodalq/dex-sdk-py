"""
Integration Tests for Perpetual State

Tests for perpetual contract state:
- Price data (mark, last, oracle)
- Fee configuration
- Margin requirements
- Funding data
- Open interest
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
# Perpetual Basic State Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualBasicState:
    """Tests for basic perpetual state."""
    
    def test_perpetual_has_id(self, exchange_snapshot):
        """Verify perpetuals have IDs."""
        perp_ids = exchange_snapshot.perpetual_ids()
        assert len(perp_ids) > 0
        
        for perp_id in perp_ids:
            perp = exchange_snapshot.get_perpetual(perp_id)
            assert perp.id == perp_id
    
    def test_perpetual_has_symbol(self, exchange_snapshot):
        """Verify perpetuals have symbols."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            symbol = perp.symbol
            assert symbol is not None
            assert len(symbol) > 0
    
    def test_perpetual_has_name(self, exchange_snapshot):
        """Verify perpetuals have names."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            name = perp.name
            assert name is not None
            assert len(name) > 0


# =============================================================================
# Perpetual Price Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualPrices:
    """Tests for perpetual price data."""
    
    def test_mark_price_positive(self, exchange_snapshot):
        """Verify mark prices are positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            mark_price = float(str(perp.mark_price))
            
            # Mark price should be positive (or zero if no trades)
            assert mark_price >= 0
    
    def test_last_price_positive(self, exchange_snapshot):
        """Verify last prices are positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            last_price = float(str(perp.last_price))
            
            # Last price should be positive (or zero if no trades)
            assert last_price >= 0
    
    def test_oracle_price_positive(self, exchange_snapshot):
        """Verify oracle prices are positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            oracle_price = float(str(perp.oracle_price))
            
            # Oracle price should be positive (or zero if oracle not used)
            assert oracle_price >= 0
    
    def test_prices_in_reasonable_range(self, exchange_snapshot):
        """Verify prices are in reasonable ranges for crypto assets."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            mark_price = float(str(perp.mark_price))
            
            if mark_price > 0:
                # Prices should be reasonable (not obviously broken)
                # This catches overflow/underflow issues
                assert mark_price < 1e12, "Price seems unreasonably high"
                assert mark_price > 1e-12, "Price seems unreasonably low"


# =============================================================================
# Perpetual Fee Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualFees:
    """Tests for perpetual fee configuration."""
    
    def test_maker_fee_exists(self, exchange_snapshot):
        """Verify maker fees are accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            maker_fee = float(str(perp.maker_fee))
            
            # Maker fee should be non-negative
            assert maker_fee >= 0
    
    def test_taker_fee_exists(self, exchange_snapshot):
        """Verify taker fees are accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            taker_fee = float(str(perp.taker_fee))
            
            # Taker fee should be non-negative
            assert taker_fee >= 0
    
    def test_maker_fee_reasonable(self, exchange_snapshot):
        """Verify maker fees are reasonable (< 10%)."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            maker_fee = float(str(perp.maker_fee))
            
            # Fee should be less than 10% (0.10)
            assert maker_fee < 0.10, f"Maker fee {maker_fee} seems unreasonably high"
    
    def test_taker_fee_reasonable(self, exchange_snapshot):
        """Verify taker fees are reasonable (< 10%)."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            taker_fee = float(str(perp.taker_fee))
            
            # Fee should be less than 10% (0.10)
            assert taker_fee < 0.10, f"Taker fee {taker_fee} seems unreasonably high"


# =============================================================================
# Perpetual Margin Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualMargins:
    """Tests for perpetual margin requirements."""
    
    def test_initial_margin_positive(self, exchange_snapshot):
        """Verify initial margin is positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            initial_margin = float(str(perp.initial_margin))
            
            assert initial_margin > 0, "Initial margin should be positive"
    
    def test_maintenance_margin_positive(self, exchange_snapshot):
        """Verify maintenance margin is positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            maintenance_margin = float(str(perp.maintenance_margin))
            
            assert maintenance_margin > 0, "Maintenance margin should be positive"
    
    def test_maintenance_and_initial_margins_exist(self, exchange_snapshot):
        """Verify both maintenance and initial margins are accessible and positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            initial = float(str(perp.initial_margin))
            maintenance = float(str(perp.maintenance_margin))
            
            # Both should be positive
            assert initial > 0, f"Initial margin should be positive, got {initial}"
            assert maintenance > 0, f"Maintenance margin should be positive, got {maintenance}"
    
    def test_margin_implies_max_leverage(self, exchange_snapshot):
        """Verify margin implies reasonable max leverage."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            initial = float(str(perp.initial_margin))
            
            if initial > 0:
                max_leverage = 1.0 / initial
                # Max leverage should be reasonable (< 1000x)
                assert max_leverage < 1000, f"Implied leverage {max_leverage}x seems too high"


# =============================================================================
# Perpetual Funding Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualFunding:
    """Tests for perpetual funding data."""
    
    def test_funding_rate_accessible(self, exchange_snapshot):
        """Verify funding rate is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            funding_rate = perp.funding_rate
            
            # Should be accessible (value can be positive, negative, or zero)
            assert funding_rate is not None
    
    def test_funding_rate_reasonable(self, exchange_snapshot):
        """Verify funding rate is in reasonable range."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            funding_rate = float(str(perp.funding_rate))
            
            # Funding rate per interval should be < 100% (sanity check)
            assert abs(funding_rate) < 1.0, (
                f"Funding rate {funding_rate} seems unreasonably large"
            )
    
    def test_funding_start_block(self, exchange_snapshot):
        """Verify funding start block is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            start_block = perp.funding_start_block
            
            # Should be a non-negative integer
            assert start_block >= 0


# =============================================================================
# Perpetual Open Interest Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualOpenInterest:
    """Tests for perpetual open interest."""
    
    def test_open_interest_non_negative(self, exchange_snapshot):
        """Verify open interest is non-negative."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            oi = float(str(perp.open_interest))
            
            assert oi >= 0, "Open interest cannot be negative"
    
    def test_open_interest_amount_non_negative(self, exchange_snapshot):
        """Verify open interest amount (notional value) is non-negative."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            oi_amount = float(str(perp.open_interest_amount))
            
            assert oi_amount >= 0, "Open interest amount cannot be negative"
    
    def test_open_interest_amount_consistent(self, exchange_snapshot):
        """Verify open interest amount is approximately size * last_price."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            oi = float(str(perp.open_interest))
            oi_amount = float(str(perp.open_interest_amount))
            last_price = float(str(perp.last_price))
            
            # If there's OI and a last price, amount should be approximately size * price
            if oi > 0 and last_price > 0:
                expected = oi * last_price
                # Allow some tolerance for numerical precision
                assert abs(oi_amount - expected) < expected * 0.01 + 1e-6, (
                    f"OI amount {oi_amount} not consistent with OI {oi} * price {last_price}"
                )
    
    def test_total_orders_non_negative(self, exchange_snapshot):
        """Verify total orders count is non-negative."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            total = perp.total_orders
            
            assert total >= 0, "Total orders cannot be negative"


# =============================================================================
# Perpetual Price Timestamps Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualPriceTimestamps:
    """Tests for perpetual price timestamp/instant getters."""
    
    def test_last_price_timestamp_accessible(self, exchange_snapshot):
        """Verify last price timestamp is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            timestamp = perp.last_price_timestamp
            
            assert timestamp is not None
            assert isinstance(timestamp, int)
            assert timestamp >= 0
    
    def test_last_price_instant_accessible(self, exchange_snapshot):
        """Verify last price instant is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            instant = perp.last_price_instant
            
            assert instant is not None
            assert hasattr(instant, 'block_number')
            assert hasattr(instant, 'block_timestamp')
    
    def test_last_price_instant_consistent_with_timestamp(self, exchange_snapshot):
        """Verify last price instant timestamp matches the timestamp getter."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            timestamp = perp.last_price_timestamp
            instant = perp.last_price_instant
            
            assert instant.block_timestamp == timestamp
    
    def test_mark_price_timestamp_accessible(self, exchange_snapshot):
        """Verify mark price timestamp is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            timestamp = perp.mark_price_timestamp
            
            assert timestamp is not None
            assert isinstance(timestamp, int)
            assert timestamp >= 0
    
    def test_mark_price_instant_accessible(self, exchange_snapshot):
        """Verify mark price instant is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            instant = perp.mark_price_instant
            
            assert instant is not None
            assert hasattr(instant, 'block_number')
            assert hasattr(instant, 'block_timestamp')
    
    def test_oracle_price_timestamp_accessible(self, exchange_snapshot):
        """Verify oracle price timestamp is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            timestamp = perp.oracle_price_timestamp
            
            assert timestamp is not None
            assert isinstance(timestamp, int)
            assert timestamp >= 0
    
    def test_oracle_price_instant_accessible(self, exchange_snapshot):
        """Verify oracle price instant is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            instant = perp.oracle_price_instant
            
            assert instant is not None
            assert hasattr(instant, 'block_number')
            assert hasattr(instant, 'block_timestamp')


# =============================================================================
# Perpetual Price Staleness Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualPriceStaleness:
    """Tests for perpetual price staleness detection."""
    
    def test_is_mark_price_obsolete_accessible(self, exchange_snapshot):
        """Verify mark price obsolete flag is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            is_obsolete = perp.is_mark_price_obsolete
            
            assert is_obsolete is not None
            assert isinstance(is_obsolete, bool)
    
    def test_is_oracle_price_obsolete_accessible(self, exchange_snapshot):
        """Verify oracle price obsolete flag is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            is_obsolete = perp.is_oracle_price_obsolete
            
            assert is_obsolete is not None
            assert isinstance(is_obsolete, bool)
    
    def test_price_max_age_sec_accessible(self, exchange_snapshot):
        """Verify price max age is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            max_age = perp.price_max_age_sec
            
            assert max_age is not None
            assert isinstance(max_age, int)
            assert max_age >= 0
    
    def test_price_max_age_reasonable(self, exchange_snapshot):
        """Verify price max age is reasonable (< 1 day)."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            max_age = perp.price_max_age_sec
            
            # Max age should be less than 1 day (86400 seconds)
            assert max_age < 86400, f"Price max age {max_age}s seems unreasonably high"


# =============================================================================
# Perpetual Oracle Configuration Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualOracleConfig:
    """Tests for perpetual oracle configuration."""
    
    def test_oracle_feed_id_accessible(self, exchange_snapshot):
        """Verify oracle feed ID is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            feed_id = perp.oracle_feed_id
            
            assert feed_id is not None
            assert isinstance(feed_id, str)
            assert feed_id.startswith("0x")
    
    def test_is_oracle_used_accessible(self, exchange_snapshot):
        """Verify is_oracle_used flag is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            is_used = perp.is_oracle_used
            
            assert is_used is not None
            assert isinstance(is_used, bool)


# =============================================================================
# Perpetual Funding Extended Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPerpetualFundingExtended:
    """Extended tests for perpetual funding data."""
    
    def test_has_next_funding_rate_accessible(self, exchange_snapshot):
        """Verify has_next_funding_rate flag is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            has_next = perp.has_next_funding_rate
            
            assert has_next is not None
            assert isinstance(has_next, bool)
    
    def test_next_funding_event_block_optional(self, exchange_snapshot):
        """Verify next_funding_event_block can be None or a valid block."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            next_block = perp.next_funding_event_block
            
            # Can be None or a positive integer
            if next_block is not None:
                assert isinstance(next_block, int)
                assert next_block >= 0
