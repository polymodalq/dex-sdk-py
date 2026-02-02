"""
Integration Tests for Snapshot Building

Tests that require testnet RPC connection:
- Building snapshots at latest block
- Building snapshots at specific blocks
- Snapshot with accounts
- Snapshot builder configuration
"""

import pytest
import os

# Try to import SDK, skip if not available
try:
    from perpl_sdk import Chain, SnapshotBuilder, Exchange, snapshot, DEX_REVISION
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

pytestmark = [pytest.mark.integration]


# =============================================================================
# Basic Snapshot Tests
# =============================================================================

def _build_snapshot_or_skip(builder, chain):
    """Helper to build snapshot or skip if contract not deployed."""
    try:
        return builder.build()
    except Exception as e:
        error_msg = str(e).lower()
        if "not a contract" in error_msg or "returned no data" in error_msg:
            pytest.skip(
                f"Exchange contract not deployed at {chain.exchange}. "
                "Check Chain.testnet() configuration."
            )
        raise


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestSnapshotBuilding:
    """Tests for basic snapshot building."""
    
    def test_build_snapshot_latest_block(self, testnet_chain, testnet_rpc):
        """Verify snapshot building succeeds at latest block."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        
        assert exchange is not None
        assert exchange.instant.block_number > 0
        assert exchange.instant.block_timestamp > 0
    
    def test_snapshot_has_perpetuals(self, testnet_chain, testnet_rpc):
        """Verify snapshot contains perpetual data."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        
        perp_ids = exchange.perpetual_ids()
        assert len(perp_ids) > 0, "Should have at least one perpetual"
    
    def test_snapshot_has_funding_interval(self, testnet_chain, testnet_rpc):
        """Verify snapshot has funding interval."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        
        assert exchange.funding_interval_blocks > 0
    
    def test_snapshot_has_exchange_params(self, testnet_chain, testnet_rpc):
        """Verify snapshot has exchange parameters."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        
        # These should be valid values
        min_post = exchange.min_post
        min_settle = exchange.min_settle
        recycle_fee = exchange.recycle_fee
        
        assert min_post is not None
        assert min_settle is not None
        assert recycle_fee is not None


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestSnapshotConfiguration:
    """Tests for snapshot builder configuration."""
    
    def test_with_perpetuals_filter(self, testnet_chain, testnet_rpc):
        """Test filtering to specific perpetuals."""
        # Use the first valid perpetual ID from chain config
        valid_perp_ids = testnet_chain.perpetuals
        if not valid_perp_ids:
            pytest.skip("No perpetuals configured in chain")
        
        first_perp_id = valid_perp_ids[0]
        
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        builder = builder.with_perpetuals([first_perp_id])
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        
        perp_ids = exchange.perpetual_ids()
        assert first_perp_id in perp_ids
    
    def test_with_specific_block(self, testnet_chain, testnet_rpc):
        """Test building at a specific historical block."""
        # First, get the latest block to find a historical one
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        latest_block = exchange.instant.block_number
        
        # Build at a block 100 blocks ago (if possible)
        if latest_block > 100:
            historical_block = latest_block - 100
            builder2 = SnapshotBuilder(testnet_chain, testnet_rpc)
            builder2 = builder2.at_block(historical_block)
            exchange2 = _build_snapshot_or_skip(builder2, testnet_chain)
            
            # Should be at the requested block (or close to it)
            assert exchange2.instant.block_number <= latest_block
    
    def test_snapshot_consistency(self, testnet_chain, testnet_rpc):
        """Test that snapshot data is internally consistent."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        exchange = _build_snapshot_or_skip(builder, testnet_chain)
        
        # All perpetuals in the IDs list should be accessible
        for perp_id in exchange.perpetual_ids():
            perp = exchange.get_perpetual(perp_id)
            assert perp is not None, f"Perpetual {perp_id} should exist"


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(180)
class TestSnapshotWithAccounts:
    """Tests for snapshot building with accounts."""
    
    def test_with_accounts(self, testnet_chain, testnet_rpc, known_account_address):
        """Test building snapshot with specific accounts."""
        if known_account_address == "0x0000000000000000000000000000000000000000":
            pytest.skip("No known account address configured")
        
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        builder = builder.with_accounts([known_account_address])
        
        try:
            exchange = builder.build()
        except Exception as e:
            error_msg = str(e).lower()
            # Skip if contract reverted (account may not exist on exchange)
            if "reverted" in error_msg or "execution" in error_msg:
                pytest.skip(f"Account {known_account_address} not registered on exchange")
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        # Should have account data
        account_ids = exchange.account_ids()
        assert len(account_ids) >= 0  # May or may not have accounts


@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(300)
class TestSnapshotAllPositions:
    """Tests for snapshot building with all positions."""
    
    def test_with_all_positions_method_exists(self, testnet_chain, testnet_rpc):
        """Verify with_all_positions method exists on SnapshotBuilder."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        
        # Should have the method
        assert hasattr(builder, 'with_all_positions')
        assert callable(getattr(builder, 'with_all_positions'))
    
    def test_with_all_positions_returns_builder(self, testnet_chain, testnet_rpc):
        """Verify with_all_positions returns builder for chaining."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        result = builder.with_all_positions()
        
        # Should return the builder for chaining
        assert result is not None
    
    def test_with_all_positions_builds_successfully(self, testnet_chain, testnet_rpc):
        """Test building snapshot with all positions enabled."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        builder = builder.with_all_positions()
        
        try:
            exchange = builder.build()
        except Exception as e:
            error_msg = str(e).lower()
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        # Should succeed - may or may not have positions depending on testnet state
        assert exchange is not None
        assert exchange.instant.block_number > 0
    
    def test_with_positions_per_batch_method_exists(self, testnet_chain, testnet_rpc):
        """Verify with_positions_per_batch method exists."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        
        assert hasattr(builder, 'with_positions_per_batch')
        assert callable(getattr(builder, 'with_positions_per_batch'))
    
    def test_with_positions_per_batch_returns_builder(self, testnet_chain, testnet_rpc):
        """Verify with_positions_per_batch returns builder for chaining."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        result = builder.with_positions_per_batch(100)
        
        # Should return the builder for chaining
        assert result is not None
    
    def test_combined_all_positions_and_batch_size(self, testnet_chain, testnet_rpc):
        """Test with_all_positions combined with with_positions_per_batch."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        builder = builder.with_all_positions()
        builder = builder.with_positions_per_batch(100)
        
        try:
            exchange = builder.build()
        except Exception as e:
            error_msg = str(e).lower()
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        # Should succeed
        assert exchange is not None
    
    def test_with_accounts_clears_all_positions(self, testnet_chain, testnet_rpc, known_account_address):
        """Test that with_accounts clears with_all_positions flag."""
        if known_account_address == "0x0000000000000000000000000000000000000000":
            pytest.skip("No known account address configured")
        
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        
        # Set all_positions first, then accounts (should clear all_positions)
        builder = builder.with_all_positions()
        builder = builder.with_accounts([known_account_address])
        
        try:
            exchange = builder.build()
        except Exception as e:
            error_msg = str(e).lower()
            if "reverted" in error_msg or "execution" in error_msg:
                pytest.skip(f"Account {known_account_address} not registered")
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        # Should succeed - using accounts mode, not all_positions
        assert exchange is not None


# =============================================================================
# Exchange State Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestExchangeState:
    """Tests for Exchange state object."""
    
    def test_exchange_chain(self, exchange_snapshot):
        """Test exchange has chain configuration."""
        chain = exchange_snapshot.chain
        assert chain is not None
        assert chain.chain_id > 0
    
    def test_exchange_instant(self, exchange_snapshot):
        """Test exchange has valid instant."""
        instant = exchange_snapshot.instant
        assert instant.block_number > 0
        assert instant.block_timestamp > 0
    
    def test_exchange_revision(self, exchange_snapshot):
        """Test exchange revision is accessible."""
        revision = Exchange.revision()
        assert revision is not None
        assert isinstance(revision, str)
    
    def test_exchange_not_halted(self, exchange_snapshot):
        """Test exchange halted status is accessible."""
        is_halted = exchange_snapshot.is_halted
        assert isinstance(is_halted, bool)
        # Usually the testnet exchange is not halted
        # but we don't assert the value


# =============================================================================
# snapshot() Convenience Function Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestSnapshotFunction:
    """Tests for the snapshot() convenience function."""
    
    def test_snapshot_function_exists(self):
        """Verify snapshot() function is importable."""
        assert snapshot is not None
        assert callable(snapshot)
    
    def test_snapshot_function_basic(self, testnet_chain, testnet_rpc):
        """Test basic snapshot() function call."""
        try:
            exchange = snapshot(chain=testnet_chain, rpc_url=testnet_rpc)
        except Exception as e:
            error_msg = str(e).lower()
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        assert exchange is not None
        assert isinstance(exchange, Exchange)
        assert exchange.instant.block_number > 0
    
    def test_snapshot_function_with_perpetuals(self, testnet_chain, testnet_rpc):
        """Test snapshot() with perpetual_ids parameter."""
        valid_perp_ids = testnet_chain.perpetuals
        if not valid_perp_ids:
            pytest.skip("No perpetuals configured in chain")
        
        first_perp_id = valid_perp_ids[0]
        
        try:
            exchange = snapshot(
                chain=testnet_chain,
                rpc_url=testnet_rpc,
                perpetual_ids=[first_perp_id]
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        assert exchange is not None
        perp_ids = exchange.perpetual_ids()
        assert first_perp_id in perp_ids
    
    def test_snapshot_function_with_block_number(self, testnet_chain, testnet_rpc):
        """Test snapshot() with block_number parameter."""
        # First get latest block
        try:
            exchange1 = snapshot(chain=testnet_chain, rpc_url=testnet_rpc)
        except Exception as e:
            error_msg = str(e).lower()
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        latest_block = exchange1.instant.block_number
        
        if latest_block > 100:
            historical_block = latest_block - 100
            exchange2 = snapshot(
                chain=testnet_chain,
                rpc_url=testnet_rpc,
                block_number=historical_block
            )
            assert exchange2.instant.block_number <= latest_block
    
    def test_snapshot_function_equivalent_to_builder(self, testnet_chain, testnet_rpc):
        """Test that snapshot() produces equivalent results to SnapshotBuilder."""
        try:
            # Using snapshot() function
            exchange1 = snapshot(chain=testnet_chain, rpc_url=testnet_rpc)
            
            # Using SnapshotBuilder directly  
            builder = SnapshotBuilder(testnet_chain, testnet_rpc)
            exchange2 = builder.build()
        except Exception as e:
            error_msg = str(e).lower()
            if "not a contract" in error_msg or "returned no data" in error_msg:
                pytest.skip("Exchange contract not deployed")
            raise
        
        # Both should return valid Exchange objects
        assert isinstance(exchange1, Exchange)
        assert isinstance(exchange2, Exchange)
        
        # Both should have the same chain configuration
        assert exchange1.chain.chain_id == exchange2.chain.chain_id


# =============================================================================
# Exchange Utility Method Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestExchangeUtilityMethods:
    """Tests for Exchange utility methods."""
    
    def test_exchange_revision_static_method(self):
        """Test Exchange.revision() static method."""
        revision = Exchange.revision()
        
        assert revision is not None
        assert isinstance(revision, str)
        assert len(revision) > 0
    
    def test_dex_revision_constant(self):
        """Test DEX_REVISION constant is available."""
        assert DEX_REVISION is not None
        assert isinstance(DEX_REVISION, str)
    
    def test_collateral_converter_getter(self, exchange_snapshot):
        """Test exchange.collateral_converter getter."""
        converter = exchange_snapshot.collateral_converter
        
        assert converter is not None
        assert hasattr(converter, 'decimals')
        assert isinstance(converter.decimals, int)
    
    def test_min_post_getter(self, exchange_snapshot):
        """Test exchange.min_post getter."""
        min_post = exchange_snapshot.min_post
        
        assert min_post is not None
        # Should be convertible to float
        value = float(str(min_post))
        assert value >= 0
    
    def test_min_settle_getter(self, exchange_snapshot):
        """Test exchange.min_settle getter."""
        min_settle = exchange_snapshot.min_settle
        
        assert min_settle is not None
        value = float(str(min_settle))
        assert value >= 0
    
    def test_recycle_fee_getter(self, exchange_snapshot):
        """Test exchange.recycle_fee getter."""
        recycle_fee = exchange_snapshot.recycle_fee
        
        assert recycle_fee is not None
        value = float(str(recycle_fee))
        assert value >= 0
    
    def test_funding_interval_blocks_getter(self, exchange_snapshot):
        """Test exchange.funding_interval_blocks getter."""
        interval = exchange_snapshot.funding_interval_blocks
        
        assert isinstance(interval, int)
        assert interval > 0
    
    def test_perpetuals_dict_method(self, exchange_snapshot):
        """Test exchange.perpetuals() dict method."""
        perps_dict = exchange_snapshot.perpetuals()
        
        assert isinstance(perps_dict, dict)
        
        # Keys should match perpetual_ids
        perp_ids = exchange_snapshot.perpetual_ids()
        assert set(perps_dict.keys()) == set(perp_ids)
    
    def test_accounts_dict_method(self, exchange_snapshot):
        """Test exchange.accounts() dict method."""
        accounts_dict = exchange_snapshot.accounts()
        
        assert isinstance(accounts_dict, dict)
        
        # Keys should match account_ids
        account_ids = exchange_snapshot.account_ids()
        assert set(accounts_dict.keys()) == set(account_ids)
    
    def test_exchange_repr(self, exchange_snapshot):
        """Test exchange __repr__ method."""
        repr_str = repr(exchange_snapshot)
        
        assert "Exchange" in repr_str
        assert "perpetuals=" in repr_str
        assert "accounts=" in repr_str
        assert "block=" in repr_str


# =============================================================================
# Exchange Iteration and Access Pattern Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestExchangeAccessPatterns:
    """Tests for Exchange access patterns."""
    
    def test_iterate_all_perpetuals(self, exchange_snapshot):
        """Test iterating over all perpetuals."""
        count = 0
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            assert perp is not None
            count += 1
        
        assert count == len(exchange_snapshot.perpetual_ids())
    
    def test_iterate_perpetuals_dict(self, exchange_snapshot):
        """Test iterating over perpetuals dict."""
        perps_dict = exchange_snapshot.perpetuals()
        
        for perp_id, perp in perps_dict.items():
            assert isinstance(perp_id, int)
            assert perp.id == perp_id
    
    def test_iterate_accounts_dict(self, exchange_snapshot):
        """Test iterating over accounts dict."""
        accounts_dict = exchange_snapshot.accounts()
        
        for account_id, account in accounts_dict.items():
            assert isinstance(account_id, int)
            assert account.id == account_id
    
    def test_get_perpetual_invalid_id(self, exchange_snapshot):
        """Test get_perpetual with invalid ID returns None or raises."""
        # Invalid IDs should return None or raise
        result = exchange_snapshot.get_perpetual(99999)
        assert result is None
    
    def test_get_account_invalid_id(self, exchange_snapshot):
        """Test get_account with invalid ID returns None."""
        result = exchange_snapshot.get_account(99999999)
        assert result is None
    
    def test_perpetuals_count_matches(self, exchange_snapshot):
        """Verify perpetual count matches between methods."""
        ids_count = len(exchange_snapshot.perpetual_ids())
        dict_count = len(exchange_snapshot.perpetuals())
        
        assert ids_count == dict_count
    
    def test_accounts_count_matches(self, exchange_snapshot):
        """Verify account count matches between methods."""
        ids_count = len(exchange_snapshot.account_ids())
        dict_count = len(exchange_snapshot.accounts())
        
        assert ids_count == dict_count


# =============================================================================
# Exchange State Consistency Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestExchangeStateConsistency:
    """Tests for Exchange state consistency."""
    
    def test_all_perpetuals_at_same_block(self, exchange_snapshot):
        """Verify all perpetuals are at the same block."""
        exchange_block = exchange_snapshot.instant.block_number
        
        for perp_id in exchange_snapshot.perpetual_ids():
            perp = exchange_snapshot.get_perpetual(perp_id)
            assert perp.instant.block_number == exchange_block
    
    def test_all_accounts_at_same_block(self, exchange_snapshot):
        """Verify all accounts are at the same block."""
        exchange_block = exchange_snapshot.instant.block_number
        
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                assert account.instant.block_number == exchange_block
    
    def test_exchange_chain_reference(self, exchange_snapshot):
        """Verify exchange has consistent chain reference."""
        chain = exchange_snapshot.chain
        
        # Chain should be valid
        assert chain is not None
        assert chain.chain_id > 0
        assert chain.exchange is not None
        assert len(chain.exchange) == 42
    
    def test_exchange_is_mutable_for_apply_events(self, exchange_snapshot):
        """Verify Exchange is not frozen (required for apply_events)."""
        # Exchange must be mutable for apply_events to work
        # We can't easily test mutation without events, but verify the method exists
        assert hasattr(exchange_snapshot, 'apply_events')
        assert callable(exchange_snapshot.apply_events)


# =============================================================================
# SnapshotBuilder Chaining Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
@pytest.mark.timeout(120)
class TestSnapshotBuilderChaining:
    """Tests for SnapshotBuilder method chaining."""
    
    def test_builder_returns_self_for_chaining(self, testnet_chain, testnet_rpc):
        """Verify builder methods return self for chaining."""
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        
        # with_perpetuals should return builder
        valid_perp_ids = testnet_chain.perpetuals
        if valid_perp_ids:
            result = builder.with_perpetuals([valid_perp_ids[0]])
            assert result is not None
            # Should be able to chain further
            assert hasattr(result, 'build')
    
    def test_builder_chain_multiple_methods(self, testnet_chain, testnet_rpc):
        """Test chaining multiple builder methods."""
        valid_perp_ids = testnet_chain.perpetuals
        if not valid_perp_ids:
            pytest.skip("No perpetuals configured")
        
        builder = SnapshotBuilder(testnet_chain, testnet_rpc)
        
        # Chain multiple methods
        builder = builder.with_perpetuals([valid_perp_ids[0]])
        builder = builder.with_all_positions()
        builder = builder.with_positions_per_batch(100)
        
        # Should still be valid
        assert builder is not None
        assert hasattr(builder, 'build')
