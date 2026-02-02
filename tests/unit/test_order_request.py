"""
Unit Tests for OrderRequest

Tests for:
- OrderRequest constructor
- Parameter handling
- Request types
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import types, UD64, UD128
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.unit]


def make_order_request(
    request_id=1,
    perp_id=0,
    request_type=None,
    order_id=None,
    price="100.0",
    size="1.0",
    expiry_block=None,
    post_only=False,
    fill_or_kill=False,
    immediate_or_cancel=False,
    max_matches=None,
    leverage="5.0",
    last_exec_block=None,
    amount=None,
):
    """Helper to create OrderRequest with defaults."""
    if request_type is None:
        request_type = types.RequestType.OpenLong
    
    return types.OrderRequest(
        request_id=request_id,
        perp_id=perp_id,
        type=request_type,
        order_id=order_id,
        price=UD64(price),
        size=UD64(size),
        expiry_block=expiry_block,
        post_only=post_only,
        fill_or_kill=fill_or_kill,
        immediate_or_cancel=immediate_or_cancel,
        max_matches=max_matches,
        leverage=UD64(leverage),
        last_exec_block=last_exec_block,
        amount=amount,
    )


# =============================================================================
# OrderRequest Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderRequestBasic:
    """Basic tests for OrderRequest."""
    
    def test_create_open_long(self):
        """Test creating an OpenLong request."""
        request = make_order_request(request_type=types.RequestType.OpenLong)
        assert request is not None
        assert repr(request)  # Should have repr
    
    def test_create_open_short(self):
        """Test creating an OpenShort request."""
        request = make_order_request(request_type=types.RequestType.OpenShort)
        assert request is not None
    
    def test_create_close_long(self):
        """Test creating a CloseLong request."""
        request = make_order_request(request_type=types.RequestType.CloseLong)
        assert request is not None
    
    def test_create_close_short(self):
        """Test creating a CloseShort request."""
        request = make_order_request(request_type=types.RequestType.CloseShort)
        assert request is not None
    
    def test_create_cancel(self):
        """Test creating a Cancel request."""
        request = make_order_request(
            request_type=types.RequestType.Cancel,
            order_id=123,
        )
        assert request is not None


# =============================================================================
# OrderRequest Parameter Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderRequestParameters:
    """Tests for OrderRequest parameter handling."""
    
    def test_with_post_only(self):
        """Test creating request with post_only flag."""
        request = make_order_request(post_only=True)
        assert request is not None
    
    def test_with_fill_or_kill(self):
        """Test creating request with fill_or_kill flag."""
        request = make_order_request(fill_or_kill=True)
        assert request is not None
    
    def test_with_immediate_or_cancel(self):
        """Test creating request with immediate_or_cancel flag."""
        request = make_order_request(immediate_or_cancel=True)
        assert request is not None
    
    def test_with_expiry(self):
        """Test creating request with expiry blocks."""
        request = make_order_request(expiry_block=100)
        assert request is not None
    
    def test_with_max_matches(self):
        """Test creating request with max_matches."""
        request = make_order_request(max_matches=10)
        assert request is not None
    
    def test_request_id_range(self):
        """Test various request IDs."""
        for req_id in [0, 1, 100, 2**32 - 1]:
            request = make_order_request(request_id=req_id)
            assert request is not None
    
    def test_perp_id_range(self):
        """Test various perpetual IDs."""
        for perp_id in [0, 1, 10, 100]:
            request = make_order_request(perp_id=perp_id)
            assert request is not None
    
    def test_price_values(self):
        """Test various price values."""
        prices = ["0.01", "1.0", "100.0", "10000.0", "1000000.0"]
        
        for price in prices:
            request = make_order_request(price=price)
            assert request is not None
    
    def test_size_values(self):
        """Test various size values."""
        sizes = ["0.001", "0.1", "1.0", "10.0", "100.0"]
        
        for size in sizes:
            request = make_order_request(size=size)
            assert request is not None
    
    def test_leverage_values(self):
        """Test various leverage values."""
        leverages = ["1.0", "2.0", "5.0", "10.0", "20.0"]
        
        for lev in leverages:
            request = make_order_request(leverage=lev)
            assert request is not None


# =============================================================================
# OrderRequest Cancel Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderRequestCancel:
    """Tests for cancel order requests."""
    
    def test_cancel_with_order_id(self):
        """Test cancel with valid order ID."""
        request = make_order_request(
            request_type=types.RequestType.Cancel,
            order_id=123,
        )
        assert request is not None
    
    def test_cancel_various_order_ids(self):
        """Test cancel with various order IDs."""
        for order_id in [1, 100, 65535]:
            request = make_order_request(
                request_type=types.RequestType.Cancel,
                order_id=order_id,
            )
            assert request is not None


# =============================================================================
# OrderRequest Amount Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderRequestAmount:
    """Tests for OrderRequest with amount field."""
    
    def test_with_amount(self):
        """Test creating request with amount."""
        request = types.OrderRequest(
            request_id=1,
            perp_id=0,
            type=types.RequestType.OpenLong,
            order_id=None,
            price=UD64("100.0"),
            size=UD64("1.0"),
            expiry_block=None,
            post_only=False,
            fill_or_kill=False,
            immediate_or_cancel=False,
            max_matches=None,
            leverage=UD64("5.0"),
            last_exec_block=None,
            amount=UD128("1000.0"),
        )
        assert request is not None


# =============================================================================
# RequestType.try_side() Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestRequestTypeTrySide:
    """Tests for RequestType.try_side() method."""
    
    def test_open_long_is_bid(self):
        """OpenLong should have Bid side (buying)."""
        side = types.RequestType.OpenLong.try_side()
        assert side == types.OrderSide.Bid
    
    def test_open_short_is_ask(self):
        """OpenShort should have Ask side (selling)."""
        side = types.RequestType.OpenShort.try_side()
        assert side == types.OrderSide.Ask
    
    def test_close_long_is_ask(self):
        """CloseLong should have Ask side (selling to close)."""
        side = types.RequestType.CloseLong.try_side()
        assert side == types.OrderSide.Ask
    
    def test_close_short_is_bid(self):
        """CloseShort should have Bid side (buying to close)."""
        side = types.RequestType.CloseShort.try_side()
        assert side == types.OrderSide.Bid
    
    def test_cancel_has_no_side(self):
        """Cancel should return None (not an order operation)."""
        side = types.RequestType.Cancel.try_side()
        assert side is None
    
    def test_increase_position_collateral_has_no_side(self):
        """IncreasePositionCollateral should return None."""
        side = types.RequestType.IncreasePositionCollateral.try_side()
        assert side is None
    
    def test_change_has_no_side(self):
        """Change should return None (modifying existing order)."""
        side = types.RequestType.Change.try_side()
        assert side is None


# =============================================================================
# OrderRequest Convenience Methods Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderRequestConvenienceMethods:
    """Tests for OrderRequest static convenience methods."""
    
    def test_open_long_convenience(self):
        """Test OrderRequest.open_long() convenience method."""
        request = types.OrderRequest.open_long(
            request_id=1,
            perp_id=16,
            price=UD64("100.0"),
            size=UD64("1.0"),
            leverage=UD64("5.0"),
        )
        assert request is not None
    
    def test_open_long_with_post_only(self):
        """Test OrderRequest.open_long() with post_only."""
        request = types.OrderRequest.open_long(
            request_id=1,
            perp_id=16,
            price=UD64("100.0"),
            size=UD64("1.0"),
            leverage=UD64("5.0"),
            post_only=True,
        )
        assert request is not None
    
    def test_open_long_with_expiry(self):
        """Test OrderRequest.open_long() with expiry."""
        request = types.OrderRequest.open_long(
            request_id=1,
            perp_id=16,
            price=UD64("100.0"),
            size=UD64("1.0"),
            leverage=UD64("5.0"),
            expiry_blocks=100,
        )
        assert request is not None
    
    def test_open_short_convenience(self):
        """Test OrderRequest.open_short() convenience method."""
        request = types.OrderRequest.open_short(
            request_id=1,
            perp_id=16,
            price=UD64("100.0"),
            size=UD64("1.0"),
            leverage=UD64("5.0"),
        )
        assert request is not None
    
    def test_close_long_convenience(self):
        """Test OrderRequest.close_long() convenience method."""
        request = types.OrderRequest.close_long(
            request_id=1,
            perp_id=16,
            price=UD64("100.0"),
            size=UD64("1.0"),
        )
        assert request is not None
    
    def test_close_short_convenience(self):
        """Test OrderRequest.close_short() convenience method."""
        request = types.OrderRequest.close_short(
            request_id=1,
            perp_id=16,
            price=UD64("100.0"),
            size=UD64("1.0"),
        )
        assert request is not None
    
    def test_cancel_convenience(self):
        """Test OrderRequest.cancel() convenience method."""
        request = types.OrderRequest.cancel(
            request_id=1,
            perp_id=16,
            order_id=123,
        )
        assert request is not None
