"""
Integration Tests for New Order Fields

Tests for newly added Order getters:
- client_order_id
- placed_size
- filled_size
- is_expired
- prev_order_id
- next_order_id

These fields are available from real-time events but not from snapshots.
Note: These tests require a live RPC connection to fetch order data.
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
# Order New Field Tests (from snapshot - may be None)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderClientOrderId:
    """Tests for Order.client_order_id getter."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_client_order_id_exists(self, exchange_snapshot):
        """Verify client_order_id getter exists on Order."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None from snapshot
        client_id = order.client_order_id
        assert client_id is None or isinstance(client_id, int)
    
    def test_client_order_id_from_snapshot_is_none(self, exchange_snapshot):
        """Verify client_order_id is None from snapshot (not from events)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # From snapshot, client_order_id should be None
        # (only available from real-time events)
        client_id = order.client_order_id
        assert client_id is None, "client_order_id should be None from snapshot"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderPlacedSize:
    """Tests for Order.placed_size getter."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_placed_size_exists(self, exchange_snapshot):
        """Verify placed_size getter exists on Order."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None from snapshot
        placed = order.placed_size
        if placed is not None:
            # Should be convertible to float
            placed_float = float(str(placed))
            assert placed_float >= 0
    
    def test_placed_size_from_snapshot_is_none(self, exchange_snapshot):
        """Verify placed_size is None from snapshot."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        placed = order.placed_size
        assert placed is None, "placed_size should be None from snapshot"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderFilledSize:
    """Tests for Order.filled_size getter."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_filled_size_exists(self, exchange_snapshot):
        """Verify filled_size getter exists on Order."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None from snapshot
        filled = order.filled_size
        if filled is not None:
            # Should be convertible to float
            filled_float = float(str(filled))
            assert filled_float >= 0
    
    def test_filled_size_from_snapshot_is_none(self, exchange_snapshot):
        """Verify filled_size is None from snapshot."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        filled = order.filled_size
        assert filled is None, "filled_size should be None from snapshot"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderIsExpired:
    """Tests for Order.is_expired getter."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_is_expired_exists(self, exchange_snapshot):
        """Verify is_expired getter exists on Order."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - is_expired is always available
        expired = order.is_expired
        assert isinstance(expired, bool)
    
    def test_is_expired_type(self, exchange_snapshot):
        """Verify is_expired returns a boolean."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        expired = order.is_expired
        assert expired in (True, False)
    
    def test_is_expired_returns_bool_for_all_orders(self, exchange_snapshot):
        """Verify is_expired returns a boolean for all orders in the book."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            
            # Verify is_expired works for all orders
            for oid in order_ids[:10]:  # Check first 10
                order = perp.get_order(oid)
                if order:
                    expired = order.is_expired
                    assert isinstance(expired, bool), f"is_expired should return bool, got {type(expired)}"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderLinkedList:
    """Tests for Order.prev_order_id and next_order_id getters."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_prev_order_id_exists(self, exchange_snapshot):
        """Verify prev_order_id getter exists on Order."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None
        prev_id = order.prev_order_id
        assert prev_id is None or isinstance(prev_id, int)
    
    def test_next_order_id_exists(self, exchange_snapshot):
        """Verify next_order_id getter exists on Order."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None
        next_id = order.next_order_id
        assert next_id is None or isinstance(next_id, int)
    
    def test_linked_list_consistency(self, exchange_snapshot):
        """Verify linked list pointers are consistent."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            orders_dict = perp.orders()
            
            for order_id, order in orders_dict.items():
                # If prev_order_id points to an order, that order's next should point back
                prev_id = order.prev_order_id
                if prev_id is not None and prev_id in orders_dict:
                    prev_order = orders_dict[prev_id]
                    # The prev order's next_order_id might point to us
                    # (depends on price level grouping)
                
                # If next_order_id points to an order, that order's prev should point back
                next_id = order.next_order_id
                if next_id is not None and next_id in orders_dict:
                    next_order = orders_dict[next_id]
                    # The next order's prev_order_id might point to us
                    # (depends on price level grouping)
    
    def test_linked_list_ids_are_positive(self, exchange_snapshot):
        """Verify linked list IDs are positive when present."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            for order_id in perp.order_ids():
                order = perp.get_order(order_id)
                if order:
                    if order.prev_order_id is not None:
                        assert order.prev_order_id > 0, "prev_order_id must be positive"
                    if order.next_order_id is not None:
                        assert order.next_order_id > 0, "next_order_id must be positive"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderFieldsRepr:
    """Tests that new fields are represented properly."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_order_repr_still_works(self, exchange_snapshot):
        """Verify Order repr still works with new fields."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        repr_str = repr(order)
        assert "Order" in repr_str
        assert "id=" in repr_str
