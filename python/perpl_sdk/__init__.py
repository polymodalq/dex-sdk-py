"""
Perpl DEX SDK - Python Bindings

Production-grade Python SDK for Perpl perpetual derivatives DEX on Monad.

Example:
    >>> from perpl_sdk import Chain, SnapshotBuilder, UD64
    >>>
    >>> chain = Chain.testnet()
    >>> builder = SnapshotBuilder(chain, "https://testnet-rpc.monad.xyz")
    >>> exchange = builder.build()  # Blocking call
    >>> print(f"Snapshot at block {exchange.instant.block_number}")
    
    For async usage with asyncio:
    
    >>> import asyncio
    >>> from perpl_sdk import Chain, SnapshotBuilder
    >>>
    >>> async def main():
    ...     chain = Chain.testnet()
    ...     builder = SnapshotBuilder(chain, "https://testnet-rpc.monad.xyz")
    ...     exchange = await asyncio.to_thread(builder.build)
    ...     print(f"Snapshot at block {exchange.instant.block_number}")
    >>>
    >>> asyncio.run(main())
"""

# Import native module
from ._native import *  # noqa: F401, F403

__version__ = "0.1.0"
__all__ = [
    # =========================================================================
    # Core Configuration
    # =========================================================================
    "Chain",
    
    # =========================================================================
    # Numeric Types (fastnum wrappers)
    # =========================================================================
    "UD64",      # Unsigned 64-bit decimal
    "UD128",     # Unsigned 128-bit decimal
    "D256",      # Signed 256-bit decimal
    "Converter", # Precision converter
    
    # =========================================================================
    # Core Types
    # =========================================================================
    "StateInstant",  # Block number + timestamp
    
    # =========================================================================
    # State Management
    # =========================================================================
    "Exchange",    # Root state object
    "Perpetual",   # Perpetual contract state
    "Account",     # User account state
    "Position",    # Open position
    "Order",       # Order book entry
    "L2Book",      # Aggregated order book view
    
    # =========================================================================
    # Snapshot Building
    # =========================================================================
    "SnapshotBuilder",  # Build exchange state snapshot
    "snapshot",         # Convenience function
    
    # =========================================================================
    # Block Event Fetching (for incremental state updates)
    # =========================================================================
    "fetch_block_events",       # Fetch events for single block
    "fetch_block_events_range", # Fetch events for block range
    "get_latest_block",         # Get current chain head block number
    
    # =========================================================================
    # Event Streaming (WebSocket)
    # =========================================================================
    "EventStreamBuilder",  # Configure event stream
    "EventStream",         # Async event iterator
    "RawEvent",            # Raw blockchain event
    "RawBlockEvents",      # Block of raw events
    "StateEvent",          # Processed state event
    "StateBlockEvents",    # Block of state events
    
    # =========================================================================
    # Transaction Building
    # =========================================================================
    "Signer",               # Base class for external signers
    "TransactionBuilder",   # Build unsigned transactions
    "UnsignedTransaction",  # Transaction ready for signing
    "SignedTransaction",    # Signed transaction
    "TransactionReceipt",   # Transaction execution result
    
    # =========================================================================
    # Types Submodule (access via types.*)
    # =========================================================================
    # types.OrderType       - Order type enum (OpenLong, OpenShort, CloseLong, CloseShort)
    # types.OrderSide       - Bid/Ask side enum
    # types.PositionType    - Long/Short position enum
    # types.RequestType     - Request type enum (OpenLong, OpenShort, Cancel, etc.)
    # types.OrderRequest    - Order request builder
    # types.MakerFill       - Individual maker fill within a trade
    # types.Trade           - Complete trade event (taker matched against makers)
    
    # =========================================================================
    # Errors
    # =========================================================================
    "DexError",  # SDK exception type
    
    # =========================================================================
    # Observability
    # =========================================================================
    "configure_logging",  # Configure tracing/logging
    
    # =========================================================================
    # Module Info
    # =========================================================================
    "DEX_REVISION",  # Exchange contract revision
]
