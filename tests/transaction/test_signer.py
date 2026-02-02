"""
Transaction Building Tests - Signer Interface

Tests for the Signer interface:
- Base class behavior
- Custom signer implementation
- Signature validation
"""

import pytest

# Try to import SDK
try:
    from perpl_sdk import (
        Signer,
        SignedTransaction,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False

# Try to import eth_account for real signing tests
try:
    from eth_account import Account
    from eth_account.messages import encode_defunct
    ETH_ACCOUNT_AVAILABLE = True
except ImportError:
    ETH_ACCOUNT_AVAILABLE = False

pytestmark = [pytest.mark.transaction]


# =============================================================================
# Base Signer Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestBaseSigner:
    """Tests for base Signer class."""
    
    def test_signer_exists(self):
        """Verify Signer class exists and is importable."""
        assert Signer is not None
    
    def test_base_signer_not_implemented(self):
        """Verify base Signer raises NotImplementedError."""
        signer = Signer()
        
        with pytest.raises((NotImplementedError, TypeError, AttributeError)):
            signer.sign(b"test message")
    
    def test_base_address_not_implemented(self):
        """Verify base address() raises NotImplementedError."""
        signer = Signer()
        
        with pytest.raises((NotImplementedError, TypeError, AttributeError)):
            signer.address()


# =============================================================================
# Custom Signer Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestCustomSigner:
    """Tests for custom signer implementations."""
    
    def test_custom_signer_subclass(self):
        """Test that custom signer can be created by subclassing.
        
        Note: Due to PyO3 limitations, subclasses must use a factory pattern
        or set attributes after construction. The base Signer.__new__() 
        doesn't accept arguments.
        """
        
        class MockSigner(Signer):
            """Mock signer for testing."""
            
            def __init__(self):
                super().__init__()
                self._address = None
            
            def set_address(self, address: str):
                """Set address after construction (PyO3 workaround)."""
                self._address = address
                return self
            
            def address(self) -> str:
                return self._address
            
            def sign(self, message: bytes) -> bytes:
                # Return dummy signature (65 bytes)
                return b"\x00" * 65
        
        # Create signer and configure via method chaining
        signer = MockSigner().set_address("0x1234567890123456789012345678901234567890")
        
        assert signer.address() == "0x1234567890123456789012345678901234567890"
        assert len(signer.sign(b"test")) == 65
    
    @pytest.mark.skipif(not ETH_ACCOUNT_AVAILABLE, reason="eth_account not installed")
    def test_eth_account_signer(self):
        """Test real signing with eth_account.
        
        Note: Due to PyO3 limitations, we use a factory pattern.
        """
        
        class EthAccountSigner(Signer):
            """Real signer using eth_account."""
            
            def __init__(self):
                super().__init__()
                self._account = None
            
            def with_key(self, private_key: str):
                """Set private key after construction."""
                self._account = Account.from_key(private_key)
                return self
            
            def address(self) -> str:
                return self._account.address
            
            def sign(self, message: bytes) -> bytes:
                # Sign a message
                signed = self._account.sign_message(encode_defunct(message))
                return signed.signature
        
        # Use a random test key (DO NOT use real keys!)
        test_key = "0x" + "11" * 32  # Dummy private key
        
        # Use factory pattern for PyO3 compatibility
        signer = EthAccountSigner().with_key(test_key)
        
        # Should have valid address
        addr = signer.address()
        assert addr.startswith("0x")
        assert len(addr) == 42
        
        # Should produce valid signature
        sig = signer.sign(b"test message")
        assert len(sig) == 65


# =============================================================================
# Signature Validation Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestSignatureValidation:
    """Tests for signature format validation."""
    
    def test_signature_length(self):
        """Verify signatures are 65 bytes (r + s + v)."""
        
        class MockSigner(Signer):
            def address(self) -> str:
                return "0x0000000000000000000000000000000000000000"
            
            def sign(self, message: bytes) -> bytes:
                return b"\x00" * 65
        
        signer = MockSigner()
        sig = signer.sign(b"test")
        
        assert len(sig) == 65, "Signature should be 65 bytes"
    
    def test_invalid_signature_length_short(self):
        """Test handling of short signatures."""
        
        class ShortSigner(Signer):
            def address(self) -> str:
                return "0x0000000000000000000000000000000000000000"
            
            def sign(self, message: bytes) -> bytes:
                return b"\x00" * 32  # Too short
        
        signer = ShortSigner()
        sig = signer.sign(b"test")
        
        # Should be 32 bytes (which is invalid for tx signing)
        assert len(sig) == 32
        assert len(sig) != 65, "This is an invalid signature length"
    
    def test_address_format(self):
        """Verify address format (0x + 40 hex chars)."""
        
        class MockSigner(Signer):
            def address(self) -> str:
                return "0xABCdef1234567890ABCdef1234567890ABCdef12"
            
            def sign(self, message: bytes) -> bytes:
                return b"\x00" * 65
        
        signer = MockSigner()
        addr = signer.address()
        
        assert addr.startswith("0x")
        assert len(addr) == 42
        # Should be valid hex
        int(addr, 16)


# =============================================================================
# SignedTransaction Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestSignedTransaction:
    """Tests for SignedTransaction structure."""
    
    def test_signed_transaction_exists(self):
        """Verify SignedTransaction class exists."""
        assert SignedTransaction is not None
    
    def test_signed_transaction_creation(self):
        """Verify SignedTransaction can be created with raw bytes and hash."""
        import struct
        
        # Create dummy raw transaction bytes
        raw_tx = b"\x00" * 100
        tx_hash = "0x" + "ab" * 32
        
        signed = SignedTransaction(raw_tx, tx_hash)
        assert signed is not None
    
    def test_signed_transaction_tx_hash_getter(self):
        """Verify SignedTransaction.tx_hash returns the hash."""
        raw_tx = b"\x00" * 100
        tx_hash = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        
        signed = SignedTransaction(raw_tx, tx_hash)
        assert signed.tx_hash == tx_hash
    
    def test_signed_transaction_raw_method(self):
        """Verify SignedTransaction.raw() returns bytes."""
        raw_tx = b"\x12\x34\x56\x78" * 25
        tx_hash = "0x" + "ab" * 32
        
        signed = SignedTransaction(raw_tx, tx_hash)
        raw_bytes = signed.raw()
        
        assert raw_bytes == raw_tx
    
    def test_signed_transaction_raw_hex_method(self):
        """Verify SignedTransaction.raw_hex() returns hex string."""
        raw_tx = b"\x12\x34\x56\x78"
        tx_hash = "0x" + "ab" * 32
        
        signed = SignedTransaction(raw_tx, tx_hash)
        raw_hex = signed.raw_hex()
        
        assert raw_hex == "0x12345678"
        assert raw_hex.startswith("0x")
    
    def test_signed_transaction_repr(self):
        """Verify SignedTransaction has a repr."""
        raw_tx = b"\x00" * 100
        tx_hash = "0xabcd1234"
        
        signed = SignedTransaction(raw_tx, tx_hash)
        repr_str = repr(signed)
        
        assert "SignedTransaction" in repr_str
        assert "hash" in repr_str.lower()


# =============================================================================
# TransactionReceipt Tests
# =============================================================================

@pytest.mark.skipif(not SDK_AVAILABLE, reason="SDK not built")
class TestTransactionReceipt:
    """Tests for TransactionReceipt structure."""
    
    def test_transaction_receipt_exists(self):
        """Verify TransactionReceipt class exists."""
        from perpl_sdk import TransactionReceipt
        assert TransactionReceipt is not None
    
    def test_transaction_receipt_creation(self):
        """Verify TransactionReceipt can be created."""
        from perpl_sdk import TransactionReceipt
        
        tx_hash = "0x" + "ab" * 32
        block_number = 12345678
        gas_used = 150000
        success = True
        
        receipt = TransactionReceipt(tx_hash, block_number, gas_used, success)
        assert receipt is not None
    
    def test_transaction_receipt_tx_hash_getter(self):
        """Verify TransactionReceipt.tx_hash getter."""
        from perpl_sdk import TransactionReceipt
        
        tx_hash = "0xdeadbeef1234567890deadbeef1234567890deadbeef1234567890deadbeef12"
        receipt = TransactionReceipt(tx_hash, 100, 21000, True)
        
        assert receipt.tx_hash == tx_hash
    
    def test_transaction_receipt_block_number_getter(self):
        """Verify TransactionReceipt.block_number getter."""
        from perpl_sdk import TransactionReceipt
        
        block_number = 98765432
        receipt = TransactionReceipt("0x" + "00" * 32, block_number, 21000, True)
        
        assert receipt.block_number == block_number
    
    def test_transaction_receipt_gas_used_getter(self):
        """Verify TransactionReceipt.gas_used getter."""
        from perpl_sdk import TransactionReceipt
        
        gas_used = 250000
        receipt = TransactionReceipt("0x" + "00" * 32, 100, gas_used, True)
        
        assert receipt.gas_used == gas_used
    
    def test_transaction_receipt_success_getter(self):
        """Verify TransactionReceipt.success getter."""
        from perpl_sdk import TransactionReceipt
        
        # Test with success=True
        receipt_success = TransactionReceipt("0x" + "00" * 32, 100, 21000, True)
        assert receipt_success.success == True
        
        # Test with success=False
        receipt_failed = TransactionReceipt("0x" + "00" * 32, 100, 21000, False)
        assert receipt_failed.success == False
    
    def test_transaction_receipt_repr(self):
        """Verify TransactionReceipt has a repr."""
        from perpl_sdk import TransactionReceipt
        
        receipt = TransactionReceipt("0xabcd", 12345, 50000, True)
        repr_str = repr(receipt)
        
        assert "TransactionReceipt" in repr_str
        assert "12345" in repr_str  # block number
        assert "True" in repr_str or "success" in repr_str.lower()
