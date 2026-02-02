"""
Unit Tests for Module Public API Exports

This module systematically verifies that all classes, functions, and constants
explicitly listed in perpl_sdk/__init__.py are correctly importable and
accessible from the Python module.

This is a critical test for ensuring API stability and compatibility.
"""

import pytest

pytestmark = [pytest.mark.unit]


# =============================================================================
# Module Import Tests
# =============================================================================

class TestModuleImportable:
    """Tests that the module itself is importable."""
    
    def test_module_importable(self):
        """Verify perpl_sdk can be imported."""
        import perpl_sdk
        assert perpl_sdk is not None
    
    def test_module_has_version(self):
        """Verify module has __version__ attribute."""
        import perpl_sdk
        assert hasattr(perpl_sdk, '__version__')
        assert isinstance(perpl_sdk.__version__, str)
    
    def test_module_has_all_attribute(self):
        """Verify module has __all__ attribute."""
        import perpl_sdk
        assert hasattr(perpl_sdk, '__all__')
        assert isinstance(perpl_sdk.__all__, list)


# =============================================================================
# Core Configuration Exports
# =============================================================================

class TestCoreConfigurationExports:
    """Tests for core configuration exports."""
    
    def test_chain_importable(self):
        """Verify Chain is importable."""
        from perpl_sdk import Chain
        assert Chain is not None
    
    def test_chain_is_class(self):
        """Verify Chain is a class."""
        from perpl_sdk import Chain
        assert isinstance(Chain, type)
    
    def test_chain_has_testnet(self):
        """Verify Chain has testnet() classmethod."""
        from perpl_sdk import Chain
        assert hasattr(Chain, 'testnet')
        assert callable(Chain.testnet)
    
    def test_chain_has_custom(self):
        """Verify Chain has custom() classmethod."""
        from perpl_sdk import Chain
        assert hasattr(Chain, 'custom')
        assert callable(Chain.custom)


# =============================================================================
# Numeric Types Exports
# =============================================================================

class TestNumericTypesExports:
    """Tests for numeric type exports."""
    
    def test_ud64_importable(self):
        """Verify UD64 is importable."""
        from perpl_sdk import UD64
        assert UD64 is not None
    
    def test_ud64_is_class(self):
        """Verify UD64 is a class."""
        from perpl_sdk import UD64
        assert isinstance(UD64, type)
    
    def test_ud64_constructible(self):
        """Verify UD64 can be constructed from string."""
        from perpl_sdk import UD64
        val = UD64("100.5")
        assert val is not None
    
    def test_ud128_importable(self):
        """Verify UD128 is importable."""
        from perpl_sdk import UD128
        assert UD128 is not None
    
    def test_ud128_is_class(self):
        """Verify UD128 is a class."""
        from perpl_sdk import UD128
        assert isinstance(UD128, type)
    
    def test_ud128_constructible(self):
        """Verify UD128 can be constructed from string."""
        from perpl_sdk import UD128
        val = UD128("1000000000.123456789")
        assert val is not None
    
    def test_d256_importable(self):
        """Verify D256 is importable."""
        from perpl_sdk import D256
        assert D256 is not None
    
    def test_d256_is_class(self):
        """Verify D256 is a class."""
        from perpl_sdk import D256
        assert isinstance(D256, type)
    
    def test_d256_constructible(self):
        """Verify D256 can be constructed from string."""
        from perpl_sdk import D256
        val = D256("-12345.6789")
        assert val is not None
    
    def test_converter_importable(self):
        """Verify Converter is importable."""
        from perpl_sdk import Converter
        assert Converter is not None
    
    def test_converter_is_class(self):
        """Verify Converter is a class."""
        from perpl_sdk import Converter
        assert isinstance(Converter, type)


# =============================================================================
# Core Types Exports
# =============================================================================

class TestCoreTypesExports:
    """Tests for core type exports."""
    
    def test_state_instant_importable(self):
        """Verify StateInstant is importable."""
        from perpl_sdk import StateInstant
        assert StateInstant is not None
    
    def test_state_instant_is_class(self):
        """Verify StateInstant is a class."""
        from perpl_sdk import StateInstant
        assert isinstance(StateInstant, type)


# =============================================================================
# State Management Exports
# =============================================================================

class TestStateManagementExports:
    """Tests for state management exports."""
    
    def test_exchange_importable(self):
        """Verify Exchange is importable."""
        from perpl_sdk import Exchange
        assert Exchange is not None
    
    def test_exchange_is_class(self):
        """Verify Exchange is a class."""
        from perpl_sdk import Exchange
        assert isinstance(Exchange, type)
    
    def test_exchange_has_revision(self):
        """Verify Exchange has revision() static method."""
        from perpl_sdk import Exchange
        assert hasattr(Exchange, 'revision')
        assert callable(Exchange.revision)
    
    def test_perpetual_importable(self):
        """Verify Perpetual is importable."""
        from perpl_sdk import Perpetual
        assert Perpetual is not None
    
    def test_perpetual_is_class(self):
        """Verify Perpetual is a class."""
        from perpl_sdk import Perpetual
        assert isinstance(Perpetual, type)
    
    def test_account_importable(self):
        """Verify Account is importable."""
        from perpl_sdk import Account
        assert Account is not None
    
    def test_account_is_class(self):
        """Verify Account is a class."""
        from perpl_sdk import Account
        assert isinstance(Account, type)
    
    def test_position_importable(self):
        """Verify Position is importable."""
        from perpl_sdk import Position
        assert Position is not None
    
    def test_position_is_class(self):
        """Verify Position is a class."""
        from perpl_sdk import Position
        assert isinstance(Position, type)
    
    def test_order_importable(self):
        """Verify Order is importable."""
        from perpl_sdk import Order
        assert Order is not None
    
    def test_order_is_class(self):
        """Verify Order is a class."""
        from perpl_sdk import Order
        assert isinstance(Order, type)
    
    def test_l2book_importable(self):
        """Verify L2Book is importable."""
        from perpl_sdk import L2Book
        assert L2Book is not None
    
    def test_l2book_is_class(self):
        """Verify L2Book is a class."""
        from perpl_sdk import L2Book
        assert isinstance(L2Book, type)


# =============================================================================
# Snapshot Building Exports
# =============================================================================

class TestSnapshotBuildingExports:
    """Tests for snapshot building exports."""
    
    def test_snapshot_builder_importable(self):
        """Verify SnapshotBuilder is importable."""
        from perpl_sdk import SnapshotBuilder
        assert SnapshotBuilder is not None
    
    def test_snapshot_builder_is_class(self):
        """Verify SnapshotBuilder is a class."""
        from perpl_sdk import SnapshotBuilder
        assert isinstance(SnapshotBuilder, type)
    
    def test_snapshot_function_importable(self):
        """Verify snapshot function is importable."""
        from perpl_sdk import snapshot
        assert snapshot is not None
    
    def test_snapshot_function_is_callable(self):
        """Verify snapshot is callable."""
        from perpl_sdk import snapshot
        assert callable(snapshot)


# =============================================================================
# Event Streaming Exports
# =============================================================================

class TestEventStreamingExports:
    """Tests for event streaming exports."""
    
    def test_event_stream_builder_importable(self):
        """Verify EventStreamBuilder is importable."""
        from perpl_sdk import EventStreamBuilder
        assert EventStreamBuilder is not None
    
    def test_event_stream_builder_is_class(self):
        """Verify EventStreamBuilder is a class."""
        from perpl_sdk import EventStreamBuilder
        assert isinstance(EventStreamBuilder, type)
    
    def test_event_stream_importable(self):
        """Verify EventStream is importable."""
        from perpl_sdk import EventStream
        assert EventStream is not None
    
    def test_event_stream_is_class(self):
        """Verify EventStream is a class."""
        from perpl_sdk import EventStream
        assert isinstance(EventStream, type)
    
    def test_raw_event_importable(self):
        """Verify RawEvent is importable."""
        from perpl_sdk import RawEvent
        assert RawEvent is not None
    
    def test_raw_event_is_class(self):
        """Verify RawEvent is a class."""
        from perpl_sdk import RawEvent
        assert isinstance(RawEvent, type)
    
    def test_raw_block_events_importable(self):
        """Verify RawBlockEvents is importable."""
        from perpl_sdk import RawBlockEvents
        assert RawBlockEvents is not None
    
    def test_raw_block_events_is_class(self):
        """Verify RawBlockEvents is a class."""
        from perpl_sdk import RawBlockEvents
        assert isinstance(RawBlockEvents, type)
    
    def test_state_event_importable(self):
        """Verify StateEvent is importable."""
        from perpl_sdk import StateEvent
        assert StateEvent is not None
    
    def test_state_event_is_class(self):
        """Verify StateEvent is a class."""
        from perpl_sdk import StateEvent
        assert isinstance(StateEvent, type)
    
    def test_state_block_events_importable(self):
        """Verify StateBlockEvents is importable."""
        from perpl_sdk import StateBlockEvents
        assert StateBlockEvents is not None
    
    def test_state_block_events_is_class(self):
        """Verify StateBlockEvents is a class."""
        from perpl_sdk import StateBlockEvents
        assert isinstance(StateBlockEvents, type)


# =============================================================================
# Transaction Building Exports
# =============================================================================

class TestTransactionBuildingExports:
    """Tests for transaction building exports."""
    
    def test_signer_importable(self):
        """Verify Signer is importable."""
        from perpl_sdk import Signer
        assert Signer is not None
    
    def test_signer_is_class(self):
        """Verify Signer is a class."""
        from perpl_sdk import Signer
        assert isinstance(Signer, type)
    
    def test_transaction_builder_importable(self):
        """Verify TransactionBuilder is importable."""
        from perpl_sdk import TransactionBuilder
        assert TransactionBuilder is not None
    
    def test_transaction_builder_is_class(self):
        """Verify TransactionBuilder is a class."""
        from perpl_sdk import TransactionBuilder
        assert isinstance(TransactionBuilder, type)
    
    def test_unsigned_transaction_importable(self):
        """Verify UnsignedTransaction is importable."""
        from perpl_sdk import UnsignedTransaction
        assert UnsignedTransaction is not None
    
    def test_unsigned_transaction_is_class(self):
        """Verify UnsignedTransaction is a class."""
        from perpl_sdk import UnsignedTransaction
        assert isinstance(UnsignedTransaction, type)
    
    def test_signed_transaction_importable(self):
        """Verify SignedTransaction is importable."""
        from perpl_sdk import SignedTransaction
        assert SignedTransaction is not None
    
    def test_signed_transaction_is_class(self):
        """Verify SignedTransaction is a class."""
        from perpl_sdk import SignedTransaction
        assert isinstance(SignedTransaction, type)
    
    def test_transaction_receipt_importable(self):
        """Verify TransactionReceipt is importable."""
        from perpl_sdk import TransactionReceipt
        assert TransactionReceipt is not None
    
    def test_transaction_receipt_is_class(self):
        """Verify TransactionReceipt is a class."""
        from perpl_sdk import TransactionReceipt
        assert isinstance(TransactionReceipt, type)


# =============================================================================
# Types Submodule Exports
# =============================================================================

class TestTypesSubmoduleExports:
    """Tests for types submodule exports."""
    
    def test_types_submodule_importable(self):
        """Verify types submodule is importable."""
        from perpl_sdk import types
        assert types is not None
    
    def test_order_type_importable(self):
        """Verify OrderType is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'OrderType')
    
    def test_order_type_has_variants(self):
        """Verify OrderType has expected variants."""
        from perpl_sdk import types
        assert hasattr(types.OrderType, 'OpenLong')
        assert hasattr(types.OrderType, 'OpenShort')
        assert hasattr(types.OrderType, 'CloseLong')
        assert hasattr(types.OrderType, 'CloseShort')
    
    def test_order_side_importable(self):
        """Verify OrderSide is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'OrderSide')
    
    def test_order_side_has_variants(self):
        """Verify OrderSide has expected variants."""
        from perpl_sdk import types
        assert hasattr(types.OrderSide, 'Bid')
        assert hasattr(types.OrderSide, 'Ask')
    
    def test_position_type_importable(self):
        """Verify PositionType is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'PositionType')
    
    def test_position_type_has_variants(self):
        """Verify PositionType has expected variants."""
        from perpl_sdk import types
        assert hasattr(types.PositionType, 'Long')
        assert hasattr(types.PositionType, 'Short')
    
    def test_request_type_importable(self):
        """Verify RequestType is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'RequestType')
    
    def test_request_type_has_variants(self):
        """Verify RequestType has expected variants."""
        from perpl_sdk import types
        assert hasattr(types.RequestType, 'OpenLong')
        assert hasattr(types.RequestType, 'OpenShort')
        assert hasattr(types.RequestType, 'CloseLong')
        assert hasattr(types.RequestType, 'CloseShort')
        assert hasattr(types.RequestType, 'Cancel')
    
    def test_order_request_importable(self):
        """Verify OrderRequest is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'OrderRequest')
    
    def test_order_request_is_class(self):
        """Verify OrderRequest is a class."""
        from perpl_sdk import types
        assert isinstance(types.OrderRequest, type)
    
    def test_maker_fill_importable(self):
        """Verify MakerFill is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'MakerFill')
    
    def test_maker_fill_is_class(self):
        """Verify MakerFill is a class."""
        from perpl_sdk import types
        assert isinstance(types.MakerFill, type)
    
    def test_trade_importable(self):
        """Verify Trade is in types module."""
        from perpl_sdk import types
        assert hasattr(types, 'Trade')
    
    def test_trade_is_class(self):
        """Verify Trade is a class."""
        from perpl_sdk import types
        assert isinstance(types.Trade, type)


# =============================================================================
# Error Exports
# =============================================================================

class TestErrorExports:
    """Tests for error exports."""
    
    def test_dex_error_importable(self):
        """Verify DexError is importable."""
        from perpl_sdk import DexError
        assert DexError is not None
    
    def test_dex_error_is_class(self):
        """Verify DexError is a class."""
        from perpl_sdk import DexError
        assert isinstance(DexError, type)
    
    def test_dex_error_is_exception(self):
        """Verify DexError inherits from Exception."""
        from perpl_sdk import DexError
        assert issubclass(DexError, Exception)
    
    def test_dex_error_raisable(self):
        """Verify DexError can be raised."""
        from perpl_sdk import DexError
        with pytest.raises(DexError):
            raise DexError("test error")


# =============================================================================
# Observability Exports
# =============================================================================

class TestObservabilityExports:
    """Tests for observability exports."""
    
    def test_configure_logging_importable(self):
        """Verify configure_logging is importable."""
        from perpl_sdk import configure_logging
        assert configure_logging is not None
    
    def test_configure_logging_is_callable(self):
        """Verify configure_logging is callable."""
        from perpl_sdk import configure_logging
        assert callable(configure_logging)


# =============================================================================
# Constants Exports
# =============================================================================

class TestConstantsExports:
    """Tests for constant exports."""
    
    def test_dex_revision_importable(self):
        """Verify DEX_REVISION is importable."""
        from perpl_sdk import DEX_REVISION
        assert DEX_REVISION is not None
    
    def test_dex_revision_is_string(self):
        """Verify DEX_REVISION is a string."""
        from perpl_sdk import DEX_REVISION
        assert isinstance(DEX_REVISION, str)
    
    def test_dex_revision_format(self):
        """Verify DEX_REVISION is a valid version/revision string."""
        from perpl_sdk import DEX_REVISION
        # Should be a non-empty version string
        assert len(DEX_REVISION) > 0
        # Version strings typically contain alphanumeric chars, dots, hyphens, underscores
        # Examples: 'testnet_rc_v1.1.5-1-g7b1f0a5', 'v0.1.0', 'abc123'
        import re
        assert re.match(r'^[\w.\-]+$', DEX_REVISION), f"Invalid revision format: {DEX_REVISION}"


# =============================================================================
# All Exports Comprehensive Check
# =============================================================================

class TestAllExportsList:
    """Tests that verify __all__ matches actual exports."""
    
    def test_all_items_importable(self):
        """Verify all items in __all__ are importable."""
        import perpl_sdk
        
        for name in perpl_sdk.__all__:
            assert hasattr(perpl_sdk, name), f"{name} in __all__ but not accessible"
    
    def test_all_exports_count(self):
        """Verify expected number of exports."""
        import perpl_sdk
        
        # Should have at least these exports
        expected_minimum = 20
        actual = len(perpl_sdk.__all__)
        
        assert actual >= expected_minimum, (
            f"Expected at least {expected_minimum} exports, got {actual}"
        )
    
    def test_no_private_exports(self):
        """Verify no private names in __all__."""
        import perpl_sdk
        
        for name in perpl_sdk.__all__:
            assert not name.startswith('_'), f"{name} is private but in __all__"


# =============================================================================
# Import Style Tests
# =============================================================================

class TestImportStyles:
    """Tests for different import styles."""
    
    def test_direct_import(self):
        """Test direct import of specific names."""
        from perpl_sdk import Chain, UD64, DexError
        assert Chain is not None
        assert UD64 is not None
        assert DexError is not None
    
    def test_module_import(self):
        """Test module import followed by attribute access."""
        import perpl_sdk
        assert perpl_sdk.Chain is not None
        assert perpl_sdk.UD64 is not None
        assert perpl_sdk.DexError is not None
    
    def test_types_submodule_access(self):
        """Test types submodule access patterns."""
        # Pattern 1: from module import types
        from perpl_sdk import types
        assert types.OrderType.OpenLong is not None
        
        # Pattern 2: import module; module.types
        import perpl_sdk
        assert perpl_sdk.types.OrderType.OpenLong is not None
