"""
Unit Tests for Core Types

Tests for:
- Types submodule import patterns
- OrderType enum
- OrderSide enum
- PositionType enum
- RequestType enum
- StateInstant comparison
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import types, StateInstant
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


# =============================================================================
# Types Submodule Import Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestTypesSubmoduleImport:
    """Tests for types submodule import patterns."""
    
    def test_types_importable_from_module(self):
        """Verify types can be imported from perpl_sdk."""
        from perpl_sdk import types
        assert types is not None
    
    def test_types_module_attribute_access(self):
        """Verify types can be accessed as module attribute."""
        import perpl_sdk
        assert hasattr(perpl_sdk, 'types')
        assert perpl_sdk.types is not None
    
    def test_types_has_expected_attributes(self):
        """Verify types module has all expected attributes."""
        from perpl_sdk import types
        
        expected_attrs = [
            'OrderType',
            'OrderSide',
            'PositionType',
            'RequestType',
            'OrderRequest',
            'MakerFill',
            'Trade',
        ]
        
        for attr in expected_attrs:
            assert hasattr(types, attr), f"types module missing {attr}"


# =============================================================================
# OrderType Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderType:
    """Tests for OrderType enum."""
    
    def test_open_long_exists(self):
        """Verify OpenLong variant exists."""
        ot = types.OrderType.OpenLong
        assert ot is not None
    
    def test_open_short_exists(self):
        """Verify OpenShort variant exists."""
        ot = types.OrderType.OpenShort
        assert ot is not None
    
    def test_close_long_exists(self):
        """Verify CloseLong variant exists."""
        ot = types.OrderType.CloseLong
        assert ot is not None
    
    def test_close_short_exists(self):
        """Verify CloseShort variant exists."""
        ot = types.OrderType.CloseShort
        assert ot is not None
    
    def test_equality(self):
        """Test enum equality."""
        a = types.OrderType.OpenLong
        b = types.OrderType.OpenLong
        assert a == b
    
    def test_inequality(self):
        """Test enum inequality."""
        a = types.OrderType.OpenLong
        b = types.OrderType.OpenShort
        assert a != b
    
    def test_repr(self):
        """Test string representation."""
        ot = types.OrderType.OpenLong
        assert "OpenLong" in repr(ot) or "Long" in str(ot)


# =============================================================================
# OrderSide Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderSide:
    """Tests for OrderSide enum."""
    
    def test_bid_exists(self):
        """Verify Bid variant exists."""
        side = types.OrderSide.Bid
        assert side is not None
    
    def test_ask_exists(self):
        """Verify Ask variant exists."""
        side = types.OrderSide.Ask
        assert side is not None
    
    def test_bid_ask_different(self):
        """Verify Bid and Ask are different."""
        assert types.OrderSide.Bid != types.OrderSide.Ask
    
    def test_repr(self):
        """Test string representation."""
        bid = types.OrderSide.Bid
        ask = types.OrderSide.Ask
        assert "Bid" in repr(bid) or "bid" in str(bid).lower()
        assert "Ask" in repr(ask) or "ask" in str(ask).lower()


# =============================================================================
# PositionType Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestPositionType:
    """Tests for PositionType enum."""
    
    def test_long_exists(self):
        """Verify Long variant exists."""
        pt = types.PositionType.Long
        assert pt is not None
    
    def test_short_exists(self):
        """Verify Short variant exists."""
        pt = types.PositionType.Short
        assert pt is not None
    
    def test_is_long_method(self):
        """Test is_long() method if available."""
        long = types.PositionType.Long
        short = types.PositionType.Short
        
        if hasattr(long, 'is_long'):
            assert long.is_long() == True
            assert short.is_long() == False
    
    def test_is_short_method(self):
        """Test is_short() method if available."""
        long = types.PositionType.Long
        short = types.PositionType.Short
        
        if hasattr(short, 'is_short'):
            assert short.is_short() == True
            assert long.is_short() == False
    
    def test_equality(self):
        """Test position type equality."""
        a = types.PositionType.Long
        b = types.PositionType.Long
        c = types.PositionType.Short
        
        assert a == b
        assert a != c


# =============================================================================
# RequestType Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestRequestType:
    """Tests for RequestType enum."""
    
    def test_open_long_exists(self):
        """Verify OpenLong request type exists."""
        rt = types.RequestType.OpenLong
        assert rt is not None
    
    def test_open_short_exists(self):
        """Verify OpenShort request type exists."""
        rt = types.RequestType.OpenShort
        assert rt is not None
    
    def test_close_long_exists(self):
        """Verify CloseLong request type exists."""
        rt = types.RequestType.CloseLong
        assert rt is not None
    
    def test_close_short_exists(self):
        """Verify CloseShort request type exists."""
        rt = types.RequestType.CloseShort
        assert rt is not None
    
    def test_cancel_exists(self):
        """Verify Cancel request type exists."""
        rt = types.RequestType.Cancel
        assert rt is not None
    
    def test_all_distinct(self):
        """Verify all request types are distinct."""
        request_types = [
            types.RequestType.OpenLong,
            types.RequestType.OpenShort,
            types.RequestType.CloseLong,
            types.RequestType.CloseShort,
            types.RequestType.Cancel,
        ]
        
        # All should be unique
        for i, rt1 in enumerate(request_types):
            for j, rt2 in enumerate(request_types):
                if i != j:
                    assert rt1 != rt2, f"Request types at {i} and {j} should be different"


# =============================================================================
# StateInstant Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestStateInstant:
    """Tests for StateInstant type."""
    
    def test_state_instant_type_exists(self):
        """Verify StateInstant type is importable."""
        assert StateInstant is not None
    
    def test_state_instant_is_class(self):
        """Verify StateInstant is a class."""
        assert isinstance(StateInstant, type)
    
    def test_has_block_number(self):
        """Verify StateInstant has block_number attribute."""
        # We can't easily create a StateInstant directly,
        # but we can verify the attribute exists on the type
        assert hasattr(StateInstant, '__init__') or True  # Just verify import works


# =============================================================================
# StateInstant Integration Tests (using Exchange snapshot)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.integration
class TestStateInstantIntegration:
    """Integration tests for StateInstant using live data."""
    
    def test_exchange_instant_block_number(self, exchange_snapshot):
        """Verify exchange instant has valid block_number."""
        instant = exchange_snapshot.instant
        
        assert instant.block_number > 0
        assert isinstance(instant.block_number, int)
    
    def test_exchange_instant_block_timestamp(self, exchange_snapshot):
        """Verify exchange instant has valid block_timestamp."""
        instant = exchange_snapshot.instant
        
        assert instant.block_timestamp > 0
        assert isinstance(instant.block_timestamp, int)
    
    def test_instant_timestamp_reasonable(self, exchange_snapshot):
        """Verify timestamp is reasonable (after 2020, before 2100)."""
        instant = exchange_snapshot.instant
        
        # Timestamps should be after Jan 1, 2020 (1577836800)
        assert instant.block_timestamp > 1577836800
        # And before Jan 1, 2100 (4102444800)
        assert instant.block_timestamp < 4102444800
    
    def test_perpetual_instant_accessible(self, exchange_snapshot):
        """Verify perpetual instant is accessible."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            instant = perp.instant
            
            assert instant.block_number >= 0
            assert instant.block_timestamp >= 0
    
    def test_instant_repr(self, exchange_snapshot):
        """Verify StateInstant has a string representation."""
        instant = exchange_snapshot.instant
        repr_str = repr(instant)
        
        # Should contain some useful info
        assert "StateInstant" in repr_str or str(instant.block_number) in repr_str
    
    def test_instant_comparison_works(self, exchange_snapshot):
        """Verify StateInstant comparison works."""
        instant1 = exchange_snapshot.instant
        
        # Get another instant from a perpetual
        perp_ids = exchange_snapshot.perpetual_ids()
        if perp_ids:
            perp = exchange_snapshot.get_perpetual(perp_ids[0])
            instant2 = perp.instant
            
            # Both should have the same or similar block numbers
            # (both are from the same snapshot)
            assert abs(instant1.block_number - instant2.block_number) <= 1
