"""
Integration Tests for Account State

Tests for account data:
- Account attributes
- Balance data
- Position access
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
# Account Basic Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountBasic:
    """Basic tests for account state."""
    
    def test_account_ids_accessible(self, exchange_snapshot):
        """Verify account IDs are accessible."""
        account_ids = exchange_snapshot.account_ids()
        assert account_ids is not None
        assert isinstance(account_ids, (list, tuple))
    
    def test_get_account_returns_valid(self, exchange_snapshot):
        """Verify get_account returns valid accounts."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                assert account.id == account_id
    
    def test_account_has_address(self, exchange_snapshot):
        """Verify accounts have addresses."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                addr = account.address
                assert addr is not None
                assert isinstance(addr, str)
                assert addr.startswith("0x")


# =============================================================================
# Account Balance Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountBalance:
    """Tests for account balance data."""
    
    def test_balance_accessible(self, exchange_snapshot):
        """Verify balance is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                balance = account.balance
                assert balance is not None
    
    def test_balance_non_negative(self, exchange_snapshot):
        """Verify balance is non-negative."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                balance = float(str(account.balance))
                assert balance >= 0, "Balance cannot be negative"
    
    def test_locked_balance_accessible(self, exchange_snapshot):
        """Verify locked balance is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                locked = account.locked_balance
                assert locked is not None
    
    def test_locked_balance_non_negative(self, exchange_snapshot):
        """Verify locked balance is non-negative."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                locked = float(str(account.locked_balance))
                assert locked >= 0, "Locked balance cannot be negative"
    
    def test_locked_not_greater_than_balance(self, exchange_snapshot):
        """Verify locked balance <= total balance."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                balance = float(str(account.balance))
                locked = float(str(account.locked_balance))
                
                # Locked should typically not exceed balance
                # (but may be close due to pending orders)
                assert locked <= balance + 1e-6, (
                    f"Locked {locked} > balance {balance}"
                )


# =============================================================================
# Account Position Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountPositions:
    """Tests for account position access."""
    
    def test_position_perpetual_ids_accessible(self, exchange_snapshot):
        """Verify position perpetual IDs are accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                perp_ids = account.position_perpetual_ids()
                assert perp_ids is not None
                assert isinstance(perp_ids, (list, tuple))
    
    def test_get_position_returns_valid(self, exchange_snapshot):
        """Verify get_position returns valid positions."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                for perp_id in account.position_perpetual_ids():
                    position = account.get_position(perp_id)
                    if position is not None:
                        assert position.perpetual_id == perp_id
                        assert position.account_id == account_id
    
    def test_positions_dict_accessible(self, exchange_snapshot):
        """Verify positions dict is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                positions = account.positions()
                assert positions is not None
                # Should be dict-like
                assert hasattr(positions, 'keys') or isinstance(positions, dict)


# =============================================================================
# Account Frozen Status Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountFrozen:
    """Tests for account frozen status."""
    
    def test_frozen_status_accessible(self, exchange_snapshot):
        """Verify frozen status is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                frozen = account.frozen
                assert frozen is not None
                assert isinstance(frozen, bool)


# =============================================================================
# Account Available Balance Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountAvailableBalance:
    """Tests for account available_balance property."""
    
    def test_available_balance_accessible(self, exchange_snapshot):
        """Verify available_balance is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                available = account.available_balance
                assert available is not None
    
    def test_available_balance_non_negative(self, exchange_snapshot):
        """Verify available balance is non-negative."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                available = float(str(account.available_balance))
                assert available >= 0, "Available balance cannot be negative"
    
    def test_available_plus_locked_equals_balance(self, exchange_snapshot):
        """Verify available_balance + locked_balance == balance."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                balance = float(str(account.balance))
                locked = float(str(account.locked_balance))
                available = float(str(account.available_balance))
                
                # available = balance - locked
                expected = balance - locked
                assert abs(available - expected) < 1e-10, (
                    f"available {available} != balance {balance} - locked {locked}"
                )
    
    def test_available_not_greater_than_balance(self, exchange_snapshot):
        """Verify available balance <= total balance."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                balance = float(str(account.balance))
                available = float(str(account.available_balance))
                
                assert available <= balance + 1e-10, (
                    f"Available {available} > balance {balance}"
                )


# =============================================================================
# Account Unrealized PnL Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountUnrealizedPnL:
    """Tests for account unrealized_pnl property."""
    
    def test_unrealized_pnl_accessible(self, exchange_snapshot):
        """Verify unrealized_pnl is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                pnl = account.unrealized_pnl
                assert pnl is not None
    
    def test_unrealized_pnl_can_be_negative(self, exchange_snapshot):
        """Verify unrealized PnL can be negative (D256 signed type)."""
        # This test just ensures the value is accessible and is a number
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                pnl = account.unrealized_pnl
                # Should be convertible to float
                pnl_float = float(str(pnl))
                # Can be positive, negative, or zero
                assert isinstance(pnl_float, float)
    
    def test_unrealized_pnl_sums_positions(self, exchange_snapshot):
        """Verify account unrealized_pnl is sum of position PnLs."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is None:
                continue
            
            # Calculate sum of position PnLs
            position_pnl_sum = 0.0
            for perp_id in account.position_perpetual_ids():
                position = account.get_position(perp_id)
                if position is not None:
                    position_pnl_sum += float(str(position.pnl))
            
            # Compare with account unrealized_pnl
            account_pnl = float(str(account.unrealized_pnl))
            
            # Allow small tolerance for floating point precision
            assert abs(account_pnl - position_pnl_sum) < 1e-6 * (abs(position_pnl_sum) + 1), (
                f"Account PnL {account_pnl} != sum of position PnLs {position_pnl_sum}"
            )


# =============================================================================
# Account Instant Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestAccountInstant:
    """Tests for account instant property."""
    
    def test_instant_accessible(self, exchange_snapshot):
        """Verify account instant is accessible."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                instant = account.instant
                assert instant is not None
    
    def test_instant_has_block_number(self, exchange_snapshot):
        """Verify instant has block_number."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                instant = account.instant
                assert hasattr(instant, 'block_number')
                assert instant.block_number >= 0
    
    def test_instant_has_block_timestamp(self, exchange_snapshot):
        """Verify instant has block_timestamp."""
        for account_id in exchange_snapshot.account_ids():
            account = exchange_snapshot.get_account(account_id)
            if account is not None:
                instant = account.instant
                assert hasattr(instant, 'block_timestamp')
                assert instant.block_timestamp >= 0
