"""
Integration Tests for Market Impact Calculations

Tests for:
- ask_impact() method
- bid_impact() method

These methods calculate the market impact of executing a given size
against the order book.
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import Chain, SnapshotBuilder, UD64
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.integration]


# =============================================================================
# Ask Impact Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAskImpact:
    """Tests for perpetual.ask_impact() method."""
    
    def test_ask_impact_returns_tuple_or_none(self, exchange_snapshot):
        """Verify ask_impact returns tuple or None."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            # Try with a small size
            size = UD64("0.1")
            result = perp.ask_impact(size)
            
            # Either None (empty book) or tuple of 3 elements
            if result is not None:
                assert len(result) == 3, "Impact should return (price, filled, avg_price)"
    
    def test_ask_impact_with_zero_size(self, exchange_snapshot):
        """Verify ask_impact with zero size returns None."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            size = UD64("0")
            result = perp.ask_impact(size)
            
            # Zero size should return None (nothing to fill)
            assert result is None, "Zero size should return None"
    
    def test_ask_impact_price_within_book(self, exchange_snapshot):
        """Verify impact price is within book bounds."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            asks = l2_book.asks()
            
            if not asks:
                continue
            
            # Use a moderate size
            size = UD64("0.5")
            result = perp.ask_impact(size)
            
            if result is not None:
                worst_price, filled_size, avg_price = result
                
                # Worst price should be >= best ask
                best_ask_price = float(str(asks[0][0]))
                worst_price_float = float(str(worst_price))
                
                assert worst_price_float >= best_ask_price, (
                    f"Worst price {worst_price_float} should be >= best ask {best_ask_price}"
                )
    
    def test_ask_impact_avg_price_reasonable(self, exchange_snapshot):
        """Verify average price is between best and worst."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            asks = l2_book.asks()
            
            if not asks:
                continue
            
            # Use a moderate size
            size = UD64("0.5")
            result = perp.ask_impact(size)
            
            if result is not None:
                worst_price, filled_size, avg_price = result
                
                best_ask_price = float(str(asks[0][0]))
                worst_price_float = float(str(worst_price))
                avg_price_float = float(str(avg_price))
                
                # Average should be between best and worst
                assert best_ask_price <= avg_price_float <= worst_price_float, (
                    f"Avg price {avg_price_float} should be between "
                    f"{best_ask_price} and {worst_price_float}"
                )


# =============================================================================
# Bid Impact Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestBidImpact:
    """Tests for perpetual.bid_impact() method."""
    
    def test_bid_impact_returns_tuple_or_none(self, exchange_snapshot):
        """Verify bid_impact returns tuple or None."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            # Try with a small size
            size = UD64("0.1")
            result = perp.bid_impact(size)
            
            # Either None (empty book) or tuple of 3 elements
            if result is not None:
                assert len(result) == 3, "Impact should return (price, filled, avg_price)"
    
    def test_bid_impact_with_zero_size(self, exchange_snapshot):
        """Verify bid_impact with zero size returns None."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            size = UD64("0")
            result = perp.bid_impact(size)
            
            # Zero size should return None (nothing to fill)
            assert result is None, "Zero size should return None"
    
    def test_bid_impact_price_within_book(self, exchange_snapshot):
        """Verify impact price is within book bounds."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            bids = l2_book.bids()
            
            if not bids:
                continue
            
            # Use a moderate size
            size = UD64("0.5")
            result = perp.bid_impact(size)
            
            if result is not None:
                worst_price, filled_size, avg_price = result
                
                # Worst price should be <= best bid
                best_bid_price = float(str(bids[0][0]))
                worst_price_float = float(str(worst_price))
                
                assert worst_price_float <= best_bid_price, (
                    f"Worst price {worst_price_float} should be <= best bid {best_bid_price}"
                )
    
    def test_bid_impact_avg_price_reasonable(self, exchange_snapshot):
        """Verify average price is between best and worst."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            bids = l2_book.bids()
            
            if not bids:
                continue
            
            # Use a moderate size
            size = UD64("0.5")
            result = perp.bid_impact(size)
            
            if result is not None:
                worst_price, filled_size, avg_price = result
                
                best_bid_price = float(str(bids[0][0]))
                worst_price_float = float(str(worst_price))
                avg_price_float = float(str(avg_price))
                
                # Average should be between worst and best (note: bid is reversed)
                assert worst_price_float <= avg_price_float <= best_bid_price, (
                    f"Avg price {avg_price_float} should be between "
                    f"{worst_price_float} and {best_bid_price}"
                )


# =============================================================================
# Impact Consistency Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestImpactConsistency:
    """Tests for consistency between impact and book data."""
    
    def test_impact_filled_matches_request(self, exchange_snapshot):
        """Verify filled size is <= requested size."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            size = UD64("1.0")
            
            # Test ask impact
            ask_result = perp.ask_impact(size)
            if ask_result is not None:
                _, filled_size, _ = ask_result
                filled_float = float(str(filled_size))
                size_float = float(str(size))
                assert filled_float <= size_float, "Filled should be <= requested"
            
            # Test bid impact
            bid_result = perp.bid_impact(size)
            if bid_result is not None:
                _, filled_size, _ = bid_result
                filled_float = float(str(filled_size))
                size_float = float(str(size))
                assert filled_float <= size_float, "Filled should be <= requested"
    
    def test_large_size_partial_fill(self, exchange_snapshot):
        """Verify very large size may result in partial fill."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            # Request a very large size
            size = UD64("1000000000.0")
            
            ask_result = perp.ask_impact(size)
            if ask_result is not None:
                _, filled_size, _ = ask_result
                filled_float = float(str(filled_size))
                size_float = float(str(size))
                
                # With such a large request, we may not fill everything
                # (unless the book is extremely deep)
                # Just verify the API works correctly
                assert filled_float > 0, "Should fill something"
                assert filled_float <= size_float, "Can't fill more than requested"
    
    def test_small_size_full_fill(self, exchange_snapshot):
        """Verify small size should fully fill if book has liquidity."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            asks = l2_book.asks()
            bids = l2_book.bids()
            
            # Request a tiny size
            size = UD64("0.00001")
            
            # If there are asks with size, a tiny request should fully fill
            if asks:
                best_ask_size = float(str(asks[0][1]))
                if best_ask_size >= float(str(size)):
                    result = perp.ask_impact(size)
                    if result is not None:
                        _, filled_size, _ = result
                        filled_float = float(str(filled_size))
                        size_float = float(str(size))
                        # Should fully fill
                        assert abs(filled_float - size_float) < 0.0001, (
                            f"Small size should fully fill: {filled_float} vs {size_float}"
                        )
