# perpl_sdk

Python SDK for Perpl perpetual derivatives DEX on Monad.

> **Note**: This package provides Python bindings for the core Rust SDK at [PerplFoundation/dex-sdk](https://github.com/PerplFoundation/dex-sdk).

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Reference](#reference)
  - [Chain Configuration](#chain-configuration)
  - [Snapshot Building](#snapshot-building)
  - [Exchange State](#exchange-state)
  - [Perpetual Markets](#perpetual-markets)
  - [Order Books](#order-books)
  - [Accounts & Positions](#accounts--positions)
  - [Orders](#orders)
  - [Numeric Types](#numeric-types)
  - [Transaction Building](#transaction-building)
  - [Event Streaming](#event-streaming)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [License](#license)

---

## Overview

`perpl_sdk` provides Python bindings for the Perpl perpetual futures DEX SDK. The core functionality is implemented in Rust for performance and exposed to Python via [PyO3](https://pyo3.rs).

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Python Application                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            perpl_sdk (Python Package)                       │
│  ┌───────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐    │
│  │   state   │ │  types   │ │ numeric │ │ tx_builder   │    │
│  └───────────┘ └──────────┘ └─────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              _native.abi3.so (PyO3 Extension)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 dex-sdk (Core Rust SDK)                     │
│  ┌───────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐    │
│  │   state   │ │  types   │ │   num   │ │   stream     │    │
│  └───────────┘ └──────────┘ └─────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **State Snapshots**: Fetch consistent exchange state from blockchain RPC
- **Order Books**: L2/L3 order book with best bid/ask, spread, mid-price
- **Accounts & Positions**: Balance, PnL, liquidation prices, risk metrics
- **Transaction Building**: Create unsigned transactions for external signing
- **Event Streaming**: Real-time state updates via WebSocket
- **Fixed-Point Arithmetic**: Precise numeric types (UD64, UD128, D256)

---

## Installation

### Prerequisites

- Python 3.9+
- Rust toolchain >= 1.85.0
- [maturin](https://github.com/PyO3/maturin) for building

### Core Rust SDK Dependency

This package depends on the core Rust SDK ([PerplFoundation/dex-sdk](https://github.com/PerplFoundation/dex-sdk)). The `Cargo.toml` references it via a relative path:

```toml
dex-sdk = { package = "perpl-sdk", path = "/sdk/crates/sdk" }
```

Ensure the core SDK is available at `/sdk/` relative to this directory, or update the path in `Cargo.toml` to point to your local clone.

### Development Install

```bash
# Clone Python SDK
git clone https://github.com/polymodalq/dex-sdk-py.git
cd dex-sdk-py

# Clone Rusk SDK (or update relative path if already cloned)
git clone https://github.com/PerplFoundation/dex-sdk.git ./sdk

# Build and install Python bindings
python -m venv .venv
source .venv/bin/activate
pip install maturin
maturin develop --release
```

### Build Wheel

```bash
maturin build --release
pip install target/wheels/perpl_sdk-*.whl
```

---

## Quick Start

### Fetch Exchange State

```python
from perpl_sdk import Chain, SnapshotBuilder, UD64

# Connect to testnet
chain = Chain.testnet()
builder = SnapshotBuilder(chain, "https://testnet-rpc.monad.xyz")
exchange = builder.build()

print(f"Snapshot at block {exchange.instant.block_number}")
print(f"Perpetuals: {exchange.perpetual_ids()}")

# Get perpetual state
for perp_id in exchange.perpetual_ids():
    perp = exchange.get_perpetual(perp_id)
    book = perp.l2_book()
    print(f"{perp.symbol}: mark={perp.mark_price}, spread={book.spread()}")
```

### View Account State

```python
from perpl_sdk import Chain, SnapshotBuilder

chain = Chain.testnet()
builder = SnapshotBuilder(chain, "https://testnet-rpc.monad.xyz")
builder = builder.with_accounts(["0xYourAccountAddress"])
exchange = builder.build()

# Get account state (accounts use integer IDs)
for account_id in exchange.account_ids():
    account = exchange.get_account(account_id)
    print(f"Address: {account.address}")
    print(f"Balance: {account.balance}")
    print(f"Unrealized PnL: {account.unrealized_pnl}")

    # View positions (by perpetual ID)
    for perp_id in account.position_perpetual_ids():
        position = account.get_position(perp_id)
        print(f" Position: {position.size} @ {position.entry_price}")
        print(f" Liquidation price: {position.liquidation_price}")
```

### Build Transactions

```python
from perpl_sdk import (
    Chain, TxBuilder, OrderRequest, RequestType, 
    OrderSide, UD64, UD128
)

chain = Chain.testnet()
tx_builder = TxBuilder(chain)

# Build an open long order
request = OrderRequest(
    request_id=1,
    perp_id=0,
    type=RequestType.OpenLong,
    order_id=None,
    price=UD64("100.5"),
    size=UD64("1.0"),
    expiry_block=None,
    post_only=False,
    fill_or_kill=False,
    immediate_or_cancel=False,
    max_matches=None,
    leverage=UD64("5.0"),
    last_exec_block=None,
    amount=UD128("20.0"),
)

unsigned_tx = tx_builder.build_order_request(request)
# Sign with your preferred wallet/signer
```

---

## Reference

### Chain Configuration

The `Chain` class configures network endpoints and contract addresses.

```python
from perpl_sdk import Chain

# Use testnet configuration
chain = Chain.testnet()

# Custom chain configuration
chain = Chain.custom(
    chain_id=41454,
    collateral_token="0x...",
    deployed_at_block=1000000,
    exchange="0x...",
    perpetuals=[0, 1, 2]  # List of perpetual IDs
)

# Access chain properties
print(chain.chain_id)
print(chain.collateral_token)
print(chain.exchange)
```

### Snapshot Building

`SnapshotBuilder` fetches exchange state from the blockchain.

```python
from perpl_sdk import Chain, SnapshotBuilder

chain = Chain.testnet()
builder = SnapshotBuilder(chain, "https://testnet-rpc.monad.xyz")

# Optional: Add specific accounts to fetch
builder = builder.with_accounts(["0xAccount1", "0xAccount2"])

# Build the snapshot
exchange = builder.build()
```

### Exchange State

The `Exchange` class represents the complete state of the DEX.

```python
# Get block information
instant = exchange.instant
print(f"Block: {instant.block_number}")
print(f"Timestamp: {instant.block_timestamp}")

# List all perpetual markets
perp_ids = exchange.perpetual_ids()

# Get specific perpetual
perp = exchange.get_perpetual(0)

# Get account state (if fetched)
account = exchange.get_account("0xAccountAddress")

# Get position state
position = exchange.get_position((0, "0xAccountAddress"))
```

### Perpetual Markets

The `Perpetual` class represents a perpetual futures market.

```python
perp = exchange.get_perpetual(0)

# Market metadata
print(perp.symbol)           # e.g., "ETH"
print(perp.name)             # Full name
print(perp.id)               # Perpetual ID

# Price data
print(perp.oracle_price)     # External oracle price
print(perp.mark_price)       # Mark price for margin
print(perp.last_price)       # Last traded price

# Market statistics
print(perp.open_interest)
print(perp.funding_rate)

# Fees
print(perp.maker_fee)
print(perp.taker_fee)

# Order book
book = perp.l2_book()
```

### Order Books

The `L2Book` class provides order book functionality.

```python
book = perp.l2_book()

# Best prices (returns tuple of (price, size) or None)
best_bid = book.best_bid()   # e.g., (UD64('100.5'), UD64('10.0'))
best_ask = book.best_ask()   # e.g., (UD64('100.6'), UD64('5.0'))

# Derived metrics
spread = book.spread()       # Returns Optional[UD64]
mid_price = book.mid_price() # Returns Optional[UD64]

# Order book depth
bids = book.bids()  # List of (price, size) tuples
asks = book.asks()  # List of (price, size) tuples

# Level counts
print(book.num_bid_levels())
print(book.num_ask_levels())
```

### Accounts & Positions

```python
# Account IDs are integers, get them from exchange
account_ids = exchange.account_ids()

for account_id in account_ids:
    account = exchange.get_account(account_id)
    
    print(f"Address: {account.address}")
    print(f"Balance: {account.balance}")
    print(f"Unrealized PnL: {account.unrealized_pnl}")
    print(f"Available: {account.available_balance}")
    
    # List positions by perpetual ID
    perp_ids = account.position_perpetual_ids()
    for perp_id in perp_ids:
        position = account.get_position(perp_id)
        print(f"  Size: {position.size}")
        print(f"  Entry: {position.entry_price}")
        print(f"  Liq price: {position.liquidation_price}")
        print(f"  PnL: {position.pnl}")
```

### Orders

```python
# Orders are accessed via perpetual
perp = exchange.get_perpetual(0)

# Get all order IDs for this perpetual
order_ids = perp.order_ids()

for order_id in order_ids:
    order = perp.get_order(order_id)
    print(f"Order {order.order_id}: {order.type} {order.size} @ {order.price}")
    print(f"  Account: {order.account_id}")
    print(f"  Filled: {order.filled_size}")
    print(f"  Post-only: {order.post_only}")
```

### Numeric Types

The SDK provides three fixed-point numeric types for precision:

```python
from perpl_sdk import UD64, UD128, D256

# UD64 - Unsigned 64-bit fixed-point (9 decimals)
# Used for: prices, sizes, rates
price = UD64("100.123456789")
size = UD64("1.5")

# UD128 - Unsigned 128-bit fixed-point (18 decimals)
# Used for: large amounts, collateral
amount = UD128("1000000.123456789012345678")

# D256 - Signed 256-bit fixed-point (18 decimals)
# Used for: PnL calculations, signed values
pnl = D256("-500.123456789012345678")
```

#### Arithmetic Operations

```python
# Basic arithmetic
a = UD64("10.0")
b = UD64("3.0")

sum_ab = a + b        # 13.0
diff_ab = a - b       # 7.0
prod_ab = a * b       # 30.0
quot_ab = a / b       # 3.333333333

# Comparisons
a > b                 # True
a >= b                # True
a == UD64("10.0")     # True

# Conversion
float_val = float(a)  # 10.0
str_val = str(a)      # "10.000000000"

# Check for zero
is_zero = a.is_zero()  # False
```

### Transaction Building

Build unsigned transactions for signing with your preferred wallet.

```python
from perpl_sdk import (
    Chain, TxBuilder, OrderRequest, RequestType, UD64, UD128
)

chain = Chain.testnet()
tx_builder = TxBuilder(chain)

# Open Long Order
request = OrderRequest(
    request_id=1,
    perp_id=0,
    type=RequestType.OpenLong,
    order_id=None,
    price=UD64("100.5"),
    size=UD64("1.0"),
    expiry_block=None,
    post_only=False,
    fill_or_kill=False,
    immediate_or_cancel=False,
    max_matches=None,
    leverage=UD64("5.0"),
    last_exec_block=None,
    amount=UD128("20.0"),
)

unsigned_tx = tx_builder.build_order_request(request)

# Request Types:
# - RequestType.OpenLong   - Open a long position
# - RequestType.OpenShort  - Open a short position  
# - RequestType.CloseLong  - Close a long position
# - RequestType.CloseShort - Close a short position
# - RequestType.Cancel     - Cancel an order
# - RequestType.IncreasePositionCollateral - Add margin
# - RequestType.Change     - Modify existing order

# Get order side from request type
side = RequestType.OpenLong.try_side()  # Returns OrderSide.Bid
side = RequestType.Cancel.try_side()    # Returns None
```

### Event Streaming

Stream real-time state updates via WebSocket.

```python
from perpl_sdk import Chain, EventStream

chain = Chain.testnet()

# Create event stream (requires WebSocket endpoint)
stream = EventStream(chain, "wss://testnet-ws.monad.xyz")

# Process events
for event in stream.events():
    if event.is_trade():
        trade = event.as_trade()
        print(f"Trade: {trade.size} @ {trade.price}")
    elif event.is_order_update():
        order = event.as_order_update()
        print(f"Order update: {order.order_id}")
```

---

## Error Handling

The SDK raises Python exceptions for error conditions:

```python
from perpl_sdk import Chain, SnapshotBuilder

try:
    chain = Chain.testnet()
    builder = SnapshotBuilder(chain, "https://invalid-rpc.example.com")
    exchange = builder.build()
except RuntimeError as e:
    print(f"SDK error: {e}")

# Common errors:
# - RuntimeError: Network/RPC errors
# - ValueError: Invalid numeric strings
# - TypeError: Type conversion errors

---

## Testing

### Setup

```bash
cd py
source .venv/bin/activate
pip install -r requirements-test.txt
```

### Environment Variables

```bash
export TESTNET_RPC="https://testnet-rpc.monad.xyz"
export TESTNET_WS="https://testnet-websocket.com"
export TEST_ACCOUNT_ADDRESS="0xYourRegisteredAccount"
```

### Run Tests

```bash
# Run all tests
pytest -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests (requires RPC)
pytest tests/integration/ -v

# Run specific test file
pytest tests/unit/test_numeric.py -v

# Run with coverage
pytest --cov=perpl_sdk --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (no network)
│   ├── test_numeric.py      # Numeric types
│   ├── test_order_request.py # Order building
│   ├── test_trade_types.py  # Trade types
│   └── test_module_exports.py # Package surface
└── integration/             # Integration tests
    ├── test_snapshot.py     # Snapshot fetching
    ├── test_events.py       # Event parsing
    └── test_apply_events.py # State updates
```

---

## License

MIT - See [LICENSE](https://github.com/PerplFoundation/dex-sdk/blob/main/LICENSE) in the core Rust SDK.