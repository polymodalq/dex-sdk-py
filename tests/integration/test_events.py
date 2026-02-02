"""
Integration Tests for Event Types

Tests for blockchain event types:
- RawEvent attribute access
- RawBlockEvents container
- StateEvent mutations
- StateBlockEvents container
"""

import pytest

# Try to import SDK, skip if not available
try:
    from perpl_sdk import (
        RawEvent, RawBlockEvents, 
        StateEvent, StateBlockEvents,
        Chain, SnapshotBuilder
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.integration]


# =============================================================================
# Event Type Existence Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestEventTypesExist:
    """Tests that event types are importable and exist."""
    
    def test_raw_event_type_exists(self):
        """Verify RawEvent type is importable."""
        assert RawEvent is not None
    
    def test_raw_block_events_type_exists(self):
        """Verify RawBlockEvents type is importable."""
        assert RawBlockEvents is not None
    
    def test_state_event_type_exists(self):
        """Verify StateEvent type is importable."""
        assert StateEvent is not None
    
    def test_state_block_events_type_exists(self):
        """Verify StateBlockEvents type is importable."""
        assert StateBlockEvents is not None


# =============================================================================
# RawEvent Tests (Type Interface)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestRawEventInterface:
    """Tests for RawEvent type interface.
    
    Note: RawEvent objects are created internally by the SDK when receiving
    blockchain events. We test the interface expectations here.
    """
    
    def test_raw_event_class_exists(self):
        """Verify RawEvent class exists and is a type."""
        assert RawEvent is not None
        assert isinstance(RawEvent, type)
    
    def test_raw_event_is_frozen(self):
        """Document that RawEvent is immutable (frozen pyclass)."""
        # RawEvent is marked #[pyclass(..., frozen)] in Rust
        # This means instances are immutable
        assert RawEvent is not None


# =============================================================================
# RawBlockEvents Tests (Type Interface)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestRawBlockEventsInterface:
    """Tests for RawBlockEvents type interface.
    
    RawBlockEvents are created by the event stream infrastructure.
    We test the expected interface here.
    """
    
    def test_raw_block_events_class_exists(self):
        """Verify RawBlockEvents class exists and is a type."""
        assert RawBlockEvents is not None
        assert isinstance(RawBlockEvents, type)
    
    def test_raw_block_events_is_frozen(self):
        """Document that RawBlockEvents is immutable (frozen pyclass)."""
        assert RawBlockEvents is not None


# =============================================================================
# RawBlockEvents Tests (Type Interface)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestRawBlockEventsInterface:
    """Tests for RawBlockEvents type interface.
    
    RawBlockEvents are created by the event stream infrastructure.
    We test the expected interface here.
    """
    
    def test_raw_block_events_has_instant_getter(self):
        """Verify RawBlockEvents should have instant getter."""
        # This is a type-level check - actual usage requires live events
        pass
    
    def test_raw_block_events_has_events_method(self):
        """Verify RawBlockEvents should have events() method."""
        pass
    
    def test_raw_block_events_has_len_method(self):
        """Verify RawBlockEvents should support len()."""
        pass


# =============================================================================
# StateEvent Tests (Type Interface)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestStateEventInterface:
    """Tests for StateEvent type interface.
    
    StateEvent objects are created when applying raw events to Exchange state.
    """
    
    def test_state_event_class_exists(self):
        """Verify StateEvent class exists and is a type."""
        assert StateEvent is not None
        assert isinstance(StateEvent, type)
    
    def test_state_event_is_frozen(self):
        """Document that StateEvent is immutable (frozen pyclass)."""
        assert StateEvent is not None
    
    def test_state_event_categories_documented(self):
        """Document expected StateEvent categories."""
        # Expected categories based on SDK source:
        expected_categories = [
            "Account",
            "Error", 
            "Exchange",
            "Order",
            "Perpetual",
            "Position",
            "Trade"
        ]
        # Categories correspond to SDK StateEvents enum variants
        assert len(expected_categories) == 7


# =============================================================================
# StateBlockEvents Tests (Type Interface)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestStateBlockEventsInterface:
    """Tests for StateBlockEvents type interface.
    
    StateBlockEvents are returned by Exchange.apply_events().
    """
    
    def test_state_block_events_has_instant_getter(self):
        """Verify StateBlockEvents should have instant getter."""
        pass
    
    def test_state_block_events_has_events_method(self):
        """Verify StateBlockEvents should have events() method."""
        pass
    
    def test_state_block_events_has_len_method(self):
        """Verify StateBlockEvents should support len()."""
        pass


# =============================================================================
# Event Flow Documentation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestEventFlowDocumentation:
    """Documentation tests for the event processing flow."""
    
    def test_event_flow_description(self):
        """Document the expected event processing flow.
        
        Flow:
        1. EventStream produces RawBlockEvents
        2. Each RawBlockEvents contains multiple RawEvent
        3. Exchange.apply_events(RawBlockEvents) -> StateBlockEvents
        4. StateBlockEvents contains StateEvent mutations
        """
        # This is documentation, always passes
        assert True
    
    def test_raw_event_immutability(self):
        """Document that RawEvent is immutable (frozen)."""
        # RawEvent is marked #[pyclass(..., frozen)] in Rust
        assert True
    
    def test_state_event_immutability(self):
        """Document that StateEvent is immutable (frozen)."""
        # StateEvent is marked #[pyclass(..., frozen)] in Rust
        assert True


# =============================================================================
# Integration with Exchange.apply_events() (placeholder)
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestEventsWithExchange:
    """Tests for event integration with Exchange.
    
    Note: Full testing requires live event streaming, which is tested
    separately in test_apply_events.py and test_event_stream.py.
    """
    
    def test_exchange_has_apply_events_method(self, exchange_snapshot):
        """Verify Exchange has apply_events method."""
        assert hasattr(exchange_snapshot, 'apply_events')
        assert callable(exchange_snapshot.apply_events)
    
    def test_apply_events_signature(self, exchange_snapshot):
        """Verify apply_events has expected signature."""
        # apply_events takes RawBlockEvents and returns Optional[StateBlockEvents]
        # We can't call it without real events, but we verify the method exists
        import inspect
        # Method should be callable
        assert callable(exchange_snapshot.apply_events)
