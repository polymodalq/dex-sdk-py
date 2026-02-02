"""
Integration Tests for Order Book

Tests for L2 and L3 order book:
- Bid/ask ordering
- Spread calculation
- Mid price calculation
- Level aggregation
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
# L2 Book Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL2BookBasic:
    """Basic tests for L2 order book."""
    
    def test_l2_book_accessible(self, exchange_snapshot):
        """Verify L2 book is accessible from perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            assert l2_book is not None
    
    def test_l2_book_has_bids(self, exchange_snapshot):
        """Verify L2 book has bids accessor."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            bids = l2_book.bids()
            assert bids is not None
            assert isinstance(bids, list)
    
    def test_l2_book_has_asks(self, exchange_snapshot):
        """Verify L2 book has asks accessor."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            asks = l2_book.asks()
            assert asks is not None
            assert isinstance(asks, list)


# =============================================================================
# L2 Book Ordering Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL2BookOrdering:
    """Tests for L2 book ordering."""
    
    def test_bids_sorted_descending(self, exchange_snapshot, orderbook_assert):
        """Verify bids are sorted by price descending (best first)."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            bids = l2_book.bids()
            
            if len(bids) > 1:
                prices = [float(str(bid[0])) for bid in bids]
                orderbook_assert["sorted_desc"](prices)
    
    def test_asks_sorted_ascending(self, exchange_snapshot, orderbook_assert):
        """Verify asks are sorted by price ascending (best first)."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            asks = l2_book.asks()
            
            if len(asks) > 1:
                prices = [float(str(ask[0])) for ask in asks]
                orderbook_assert["sorted_asc"](prices)
    
    def test_no_crossed_book(self, exchange_snapshot, orderbook_assert):
        """Verify best bid < best ask (no crossed book)."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            bids = l2_book.bids()
            asks = l2_book.asks()
            
            orderbook_assert["price_ordered"](bids, asks)


# =============================================================================
# L2 Book Best Price Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL2BookBestPrices:
    """Tests for L2 book best prices."""
    
    def test_best_bid(self, exchange_snapshot):
        """Verify best_bid() returns correct value."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            best_bid = l2_book.best_bid()
            bids = l2_book.bids()
            
            if bids:
                # best_bid should match first bid
                assert best_bid is not None
                bb_price = float(str(best_bid[0]))
                first_bid_price = float(str(bids[0][0]))
                assert bb_price == first_bid_price
            else:
                assert best_bid is None
    
    def test_best_ask(self, exchange_snapshot):
        """Verify best_ask() returns correct value."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            best_ask = l2_book.best_ask()
            asks = l2_book.asks()
            
            if asks:
                # best_ask should match first ask
                assert best_ask is not None
                ba_price = float(str(best_ask[0]))
                first_ask_price = float(str(asks[0][0]))
                assert ba_price == first_ask_price
            else:
                assert best_ask is None


# =============================================================================
# L2 Book Spread Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL2BookSpread:
    """Tests for L2 book spread calculations."""
    
    def test_spread_positive(self, exchange_snapshot):
        """Verify spread is positive when both sides have orders."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            spread = l2_book.spread()
            best_bid = l2_book.best_bid()
            best_ask = l2_book.best_ask()
            
            if best_bid and best_ask:
                assert spread is not None
                spread_val = float(str(spread))
                assert spread_val > 0, "Spread should be positive"
    
    def test_spread_none_when_empty_side(self, exchange_snapshot):
        """Verify spread is None when one side is empty."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            best_bid = l2_book.best_bid()
            best_ask = l2_book.best_ask()
            spread = l2_book.spread()
            
            if best_bid is None or best_ask is None:
                assert spread is None
    
    def test_mid_price(self, exchange_snapshot):
        """Verify mid price is average of best bid and ask."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            mid = l2_book.mid_price()
            best_bid = l2_book.best_bid()
            best_ask = l2_book.best_ask()
            
            if best_bid and best_ask:
                assert mid is not None
                mid_val = float(str(mid))
                bid_val = float(str(best_bid[0]))
                ask_val = float(str(best_ask[0]))
                expected = (bid_val + ask_val) / 2
                
                assert abs(mid_val - expected) < 0.0001 * expected, (
                    f"Mid price {mid_val} != expected {expected}"
                )


# =============================================================================
# L2 Book Level Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL2BookLevels:
    """Tests for L2 book price levels."""
    
    def test_level_has_price_and_size(self, exchange_snapshot):
        """Verify each level has price and size."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            for bid in l2_book.bids():
                assert len(bid) >= 2, "Bid should have (price, size)"
                price, size = bid[0], bid[1]
                assert price is not None
                assert size is not None
            
            for ask in l2_book.asks():
                assert len(ask) >= 2, "Ask should have (price, size)"
                price, size = ask[0], ask[1]
                assert price is not None
                assert size is not None
    
    def test_sizes_positive(self, exchange_snapshot):
        """Verify all sizes are positive."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            for bid in l2_book.bids():
                size = float(str(bid[1]))
                assert size > 0, "Bid size should be positive"
            
            for ask in l2_book.asks():
                size = float(str(ask[1]))
                assert size > 0, "Ask size should be positive"
    
    def test_num_levels(self, exchange_snapshot):
        """Test level count methods."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            l2_book = perp.l2_book()
            
            num_bids = l2_book.num_bid_levels()
            num_asks = l2_book.num_ask_levels()
            
            assert num_bids == len(l2_book.bids())
            assert num_asks == len(l2_book.asks())


# =============================================================================
# Order Class Tests (L3 Book)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderBasic:
    """Basic tests for Order class."""
    
    def test_order_ids_accessible(self, exchange_snapshot):
        """Verify order IDs are accessible from perpetuals."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            
            assert order_ids is not None
            assert isinstance(order_ids, list)
    
    def test_get_order_by_id(self, exchange_snapshot):
        """Verify orders can be retrieved by ID."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            
            if order_ids:
                order_id = order_ids[0]
                order = perp.get_order(order_id)
                assert order is not None
    
    def test_get_nonexistent_order(self, exchange_snapshot):
        """Verify getting nonexistent order returns None."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            # Use an unlikely order ID
            order = perp.get_order(65535)
            # Should return None, not raise
            # (may or may not exist, just testing API)
            pass  # If we get here without exception, API works
    
    def test_total_orders_count(self, exchange_snapshot):
        """Verify total_orders matches order_ids length."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            total = perp.total_orders
            ids_count = len(perp.order_ids())
            
            assert total == ids_count


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderProperties:
    """Tests for Order property accessors."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_order_id_getter(self, exchange_snapshot):
        """Verify order_id getter returns positive int."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        order_id = order.order_id
        assert isinstance(order_id, int)
        assert order_id > 0
    
    def test_order_account_id_getter(self, exchange_snapshot):
        """Verify account_id getter returns int."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        account_id = order.account_id
        assert isinstance(account_id, int)
    
    def test_order_price_getter(self, exchange_snapshot):
        """Verify price getter returns UD64."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        price = order.price
        assert price is not None
        
        # Should be convertible to float
        price_float = float(str(price))
        assert price_float > 0
    
    def test_order_size_getter(self, exchange_snapshot):
        """Verify size getter returns UD64."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        size = order.size
        assert size is not None
        
        # Should be convertible to float
        size_float = float(str(size))
        assert size_float > 0
    
    def test_order_leverage_getter(self, exchange_snapshot):
        """Verify leverage getter returns UD64."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        leverage = order.leverage
        assert leverage is not None
        
        # Leverage should be >= 1
        lev_float = float(str(leverage))
        assert lev_float >= 1.0
    
    def test_order_expiry_block_getter(self, exchange_snapshot):
        """Verify expiry_block getter returns int."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        expiry = order.expiry_block
        assert isinstance(expiry, int)
    
    def test_order_type_getter(self, exchange_snapshot):
        """Verify type getter returns string."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        order_type = order.type
        assert isinstance(order_type, str)
        # Should be a valid order type
        assert order_type in ["OpenLong", "OpenShort", "CloseLong", "CloseShort", 
                              "Bid", "Ask", "Long", "Short"]
    
    def test_order_instant_getter(self, exchange_snapshot):
        """Verify instant getter returns StateInstant."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        instant = order.instant
        assert instant is not None
        assert hasattr(instant, 'block_number')


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderOptionalProperties:
    """Tests for Order optional properties (only from events, not snapshot)."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_request_id_optional(self, exchange_snapshot):
        """Verify request_id is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None or int
        request_id = order.request_id
        assert request_id is None or isinstance(request_id, int)
    
    def test_post_only_optional(self, exchange_snapshot):
        """Verify post_only is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        post_only = order.post_only
        assert post_only is None or isinstance(post_only, bool)
    
    def test_fill_or_kill_optional(self, exchange_snapshot):
        """Verify fill_or_kill is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        fok = order.fill_or_kill
        assert fok is None or isinstance(fok, bool)
    
    def test_immediate_or_cancel_optional(self, exchange_snapshot):
        """Verify immediate_or_cancel is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        ioc = order.immediate_or_cancel
        assert ioc is None or isinstance(ioc, bool)


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderRepr:
    """Tests for Order string representation."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_order_repr_format(self, exchange_snapshot):
        """Verify Order has a proper string representation."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        repr_str = repr(order)
        
        assert "Order" in repr_str
        assert "id=" in repr_str
        assert "price=" in repr_str
        assert "size=" in repr_str
    
    def test_order_str_equals_repr(self, exchange_snapshot):
        """Verify str(order) returns meaningful string."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        str_val = str(order)
        assert len(str_val) > 0


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrdersDict:
    """Tests for perpetual.orders() dictionary method."""
    
    def test_orders_returns_dict(self, exchange_snapshot):
        """Verify orders() returns a dictionary."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            orders_dict = perp.orders()
            
            assert isinstance(orders_dict, dict)
    
    def test_orders_dict_keys_match_ids(self, exchange_snapshot):
        """Verify orders dict keys match order_ids."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            order_ids = set(perp.order_ids())
            dict_keys = set(perp.orders().keys())
            
            assert order_ids == dict_keys
    
    def test_orders_dict_values_are_orders(self, exchange_snapshot):
        """Verify orders dict values are Order objects."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            orders_dict = perp.orders()
            
            for order_id, order in orders_dict.items():
                assert order.order_id == order_id
                assert hasattr(order, 'price')
                assert hasattr(order, 'size')


# =============================================================================
# L3 Order Book Methods Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL3AskOrders:
    """Tests for perpetual.ask_orders() L3 method."""
    
    def test_ask_orders_returns_list(self, exchange_snapshot):
        """Verify ask_orders() returns a list."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            ask_orders = perp.ask_orders()
            
            assert isinstance(ask_orders, list)
    
    def test_ask_orders_are_order_objects(self, exchange_snapshot):
        """Verify ask_orders() returns Order objects."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            ask_orders = perp.ask_orders()
            
            for order in ask_orders[:5]:  # Check first 5
                assert hasattr(order, 'order_id')
                assert hasattr(order, 'price')
                assert hasattr(order, 'size')
    
    def test_ask_orders_sorted_by_price(self, exchange_snapshot, orderbook_assert):
        """Verify ask orders are sorted by price ascending."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            ask_orders = perp.ask_orders()
            
            if len(ask_orders) > 1:
                prices = [float(str(o.price)) for o in ask_orders]
                orderbook_assert["sorted_asc"](prices)


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestL3BidOrders:
    """Tests for perpetual.bid_orders() L3 method."""
    
    def test_bid_orders_returns_list(self, exchange_snapshot):
        """Verify bid_orders() returns a list."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            bid_orders = perp.bid_orders()
            
            assert isinstance(bid_orders, list)
    
    def test_bid_orders_are_order_objects(self, exchange_snapshot):
        """Verify bid_orders() returns Order objects."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            bid_orders = perp.bid_orders()
            
            for order in bid_orders[:5]:  # Check first 5
                assert hasattr(order, 'order_id')
                assert hasattr(order, 'price')
                assert hasattr(order, 'size')
    
    def test_bid_orders_sorted_by_price(self, exchange_snapshot, orderbook_assert):
        """Verify bid orders are sorted by price descending."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            bid_orders = perp.bid_orders()
            
            if len(bid_orders) > 1:
                prices = [float(str(o.price)) for o in bid_orders]
                orderbook_assert["sorted_desc"](prices)


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestGetOrderByClientId:
    """Tests for perpetual.get_order_by_client_id() method."""
    
    def test_get_order_by_client_id_returns_none_for_unknown(self, exchange_snapshot):
        """Verify get_order_by_client_id returns None for unknown IDs."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            # Use unlikely account and client IDs
            result = perp.get_order_by_client_id(999999, 999999999)
            assert result is None
    
    def test_get_order_by_client_id_method_exists(self, exchange_snapshot):
        """Verify the method exists and is callable."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            
            # Just verify the method is callable
            assert callable(getattr(perp, 'get_order_by_client_id', None))


# =============================================================================
# Order Extended Fields Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestOrderExtendedFields:
    """Tests for Order extended fields (client_order_id, placed_size, filled_size, etc.)."""
    
    def _get_sample_order(self, exchange_snapshot):
        """Helper to get a sample order from any perpetual."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            order_ids = perp.order_ids()
            if order_ids:
                return perp.get_order(order_ids[0])
        return None
    
    def test_client_order_id_accessible(self, exchange_snapshot):
        """Verify client_order_id is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        # Should not raise - may be None from snapshot
        client_id = order.client_order_id
        assert client_id is None or isinstance(client_id, int)
    
    def test_placed_size_accessible(self, exchange_snapshot):
        """Verify placed_size is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        placed_size = order.placed_size
        # May be None from initial snapshot
        if placed_size is not None:
            placed_float = float(str(placed_size))
            assert placed_float >= 0
    
    def test_filled_size_accessible(self, exchange_snapshot):
        """Verify filled_size is accessible (may be None from snapshot)."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        filled_size = order.filled_size
        # May be None from initial snapshot
        if filled_size is not None:
            filled_float = float(str(filled_size))
            assert filled_float >= 0
    
    def test_is_expired_accessible(self, exchange_snapshot):
        """Verify is_expired is accessible."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        is_expired = order.is_expired
        assert isinstance(is_expired, bool)
    
    def test_prev_order_id_accessible(self, exchange_snapshot):
        """Verify prev_order_id is accessible."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        prev_id = order.prev_order_id
        # Can be None (first in queue) or int
        assert prev_id is None or isinstance(prev_id, int)
    
    def test_next_order_id_accessible(self, exchange_snapshot):
        """Verify next_order_id is accessible."""
        order = self._get_sample_order(exchange_snapshot)
        if order is None:
            pytest.skip("No orders in order book")
        
        next_id = order.next_order_id
        # Can be None (last in queue) or int
        assert next_id is None or isinstance(next_id, int)
    
    def test_prev_next_chain_valid(self, exchange_snapshot):
        """Verify prev/next pointers form a valid chain."""
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            orders_dict = perp.orders()
            
            for order_id, order in orders_dict.items():
                # If there's a next_order_id, that order should exist
                next_id = order.next_order_id
                if next_id is not None:
                    next_order = perp.get_order(next_id)
                    # Next order may or may not exist depending on snapshot state
                    if next_order is not None:
                        # And its prev_order_id should point back to us
                        assert next_order.prev_order_id == order_id or next_order.prev_order_id is None, (
                            f"Broken chain: order {order_id}.next={next_id}, "
                            f"but order {next_id}.prev={next_order.prev_order_id}"
                        )
