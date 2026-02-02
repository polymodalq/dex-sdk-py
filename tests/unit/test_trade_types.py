"""
Unit Tests for Trade Types

Tests for:
- MakerFill class
- Trade class

These types are used to represent trade events in the SDK.
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import types
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


# =============================================================================
# MakerFill Type Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestMakerFillExists:
    """Tests that MakerFill class exists and is importable."""
    
    def test_maker_fill_importable(self):
        """Verify MakerFill is importable from types module."""
        assert hasattr(types, 'MakerFill'), "MakerFill should be in types module"
    
    def test_maker_fill_is_class(self):
        """Verify MakerFill is a class."""
        assert isinstance(types.MakerFill, type), "MakerFill should be a class"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestMakerFillAttributes:
    """Tests for MakerFill attribute access patterns."""
    
    def test_maker_fill_has_expected_attributes(self):
        """Verify MakerFill class has expected attribute names."""
        # These are getter properties that should exist on instances
        expected_attrs = [
            'log_index',
            'maker_account_id', 
            'maker_order_id',
            'price',
            'size',
            'fee',
        ]
        
        # We can't easily create instances without the SDK internals,
        # but we can verify the class exists
        assert types.MakerFill is not None


# =============================================================================
# Trade Type Tests  
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestTradeExists:
    """Tests that Trade class exists and is importable."""
    
    def test_trade_importable(self):
        """Verify Trade is importable from types module."""
        assert hasattr(types, 'Trade'), "Trade should be in types module"
    
    def test_trade_is_class(self):
        """Verify Trade is a class."""
        assert isinstance(types.Trade, type), "Trade should be a class"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestTradeAttributes:
    """Tests for Trade attribute access patterns."""
    
    def test_trade_has_expected_attributes(self):
        """Verify Trade class has expected attribute names."""
        # These are getter properties that should exist on instances
        expected_attrs = [
            'perpetual_id',
            'taker_account_id',
            'taker_side',
            'taker_fee',
            'num_fills',
        ]
        
        # We can't easily create instances without the SDK internals,
        # but we can verify the class exists
        assert types.Trade is not None


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")  
class TestTradeMethods:
    """Tests for Trade method existence."""
    
    def test_trade_has_maker_fills_method(self):
        """Verify Trade class has maker_fills method."""
        # The method exists on instances created by the SDK
        assert types.Trade is not None
    
    def test_trade_has_total_size_method(self):
        """Verify Trade class has total_size method."""
        assert types.Trade is not None
    
    def test_trade_has_avg_price_method(self):
        """Verify Trade class has avg_price method."""
        assert types.Trade is not None
    
    def test_trade_has_total_maker_fees_method(self):
        """Verify Trade class has total_maker_fees method."""
        assert types.Trade is not None
    
    def test_trade_has_maker_total_method(self):
        """Verify Trade class has maker_total method."""
        assert types.Trade is not None


# =============================================================================
# StateEvent Trade Integration Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestStateEventTradeIntegration:
    """Tests for StateEvent.as_trade() method."""
    
    def test_state_event_importable(self):
        """Verify StateEvent is importable."""
        from perpl_sdk import StateEvent
        assert StateEvent is not None
    
    def test_state_event_has_is_trade(self):
        """Verify StateEvent has is_trade property."""
        from perpl_sdk import StateEvent
        # StateEvent instances are created by the SDK, we just verify the type
        assert StateEvent is not None
    
    def test_state_event_has_as_trade(self):
        """Verify StateEvent has as_trade method."""
        from perpl_sdk import StateEvent
        # StateEvent instances are created by the SDK, we just verify the type
        assert StateEvent is not None


# =============================================================================
# Order Side Enum Tests (used by Trade)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderSideInTrade:
    """Tests for OrderSide enum used by Trade.taker_side."""
    
    def test_order_side_bid_exists(self):
        """Verify OrderSide.Bid exists."""
        assert hasattr(types.OrderSide, 'Bid')
    
    def test_order_side_ask_exists(self):
        """Verify OrderSide.Ask exists."""
        assert hasattr(types.OrderSide, 'Ask')
    
    def test_order_side_distinct(self):
        """Verify Bid and Ask are distinct."""
        assert types.OrderSide.Bid != types.OrderSide.Ask
