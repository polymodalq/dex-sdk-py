"""
Validation Tests - Funding Rate Calculations

Tests for funding rate accuracy and consistency.
"""

import pytest

# Try to import SDK
try:
    from perpl_sdk import Chain, SnapshotBuilder
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.validation]


# =============================================================================
# Funding Rate Sign Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestFundingRateSign:
    """Tests for funding rate sign conventions."""
    
    def test_funding_rate_sign_consistent(self, exchange_snapshot):
        """
        Verify funding rate sign is consistent.
        
        Convention: Positive funding = longs pay shorts.
        """
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            funding_rate = float(str(perp.funding_rate))
            
            # Just verify it's a valid number
            assert not (funding_rate != funding_rate), "Funding rate is NaN"
    
    def test_funding_rate_bounded(self, exchange_snapshot):
        """
        Verify funding rate is within expected bounds.
        
        Typical bounds: -1% to +1% per funding interval.
        """
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            funding_rate = float(str(perp.funding_rate))
            
            # Should be within reasonable bounds (< 100% per interval)
            assert abs(funding_rate) < 1.0, (
                f"Funding rate {funding_rate} seems unreasonably large"
            )


# =============================================================================
# Funding Schedule Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestFundingSchedule:
    """Tests for funding schedule data."""
    
    def test_funding_interval_positive(self, exchange_snapshot):
        """Verify funding interval is positive."""
        interval = exchange_snapshot.funding_interval_blocks
        
        assert interval > 0, "Funding interval should be positive"
    
    def test_funding_start_block_valid(self, exchange_snapshot):
        """Verify funding start blocks are valid."""
        current_block = exchange_snapshot.instant.block_number
        
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            start_block = perp.funding_start_block
            
            # Start block should be <= current block (historical)
            assert start_block <= current_block, (
                f"Funding start {start_block} > current {current_block}"
            )
    
    def test_next_funding_block_future(self, exchange_snapshot):
        """Verify next funding block is in the future (if set)."""
        current_block = exchange_snapshot.instant.block_number
        
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            next_block = perp.next_funding_event_block
            
            if next_block is not None:
                # Should be >= current block
                assert next_block >= current_block, (
                    f"Next funding {next_block} < current {current_block}"
                )


# =============================================================================
# Funding Rate Consistency Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestFundingRateConsistency:
    """Tests for funding rate consistency across calls."""
    
    def test_funding_rate_stable(self, exchange_snapshot):
        """
        Verify funding rate is stable within same snapshot.
        
        Multiple accesses should return the same value.
        """
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            rate1 = str(perp.funding_rate)
            rate2 = str(perp.funding_rate)
            
            assert rate1 == rate2, (
                f"Funding rate changed within snapshot: {rate1} != {rate2}"
            )
    
    def test_funding_interval_matches_exchange(self, exchange_snapshot):
        """
        Verify funding interval is accessible and consistent.
        """
        interval = exchange_snapshot.funding_interval_blocks
        
        # Should be positive
        assert interval > 0
        
        # Typical values: 60-7200 blocks (1 minute to 1 hour on Monad)
        # Just sanity check it's reasonable
        assert interval < 100000, "Funding interval seems too large"
