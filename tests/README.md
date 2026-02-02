# Perpl DEX SDK Test Suite

Institution-grade test suite for the Python SDK bindings.

## Test Categories

### Unit Tests (`tests/unit/`)
- **Offline**: No network required
- **Fast**: Run in < 10 seconds
- **Coverage**: Numeric types, enums, builders

```bash
pytest tests/unit -v
```

### Integration Tests (`tests/integration/`)
- **Requires**: Testnet RPC connection
- **Timeout**: 60-120 seconds per test
- **Coverage**: Snapshot, perpetuals, accounts, orderbook, positions

```bash
TESTNET_RPC=https://testnet.monad.xyz pytest tests/integration -v
```

### Validation Tests (`tests/validation/`)
- **Requires**: Testnet RPC + web3.py
- **Purpose**: Cross-reference SDK vs contract
- **Coverage**: Price accuracy, funding rates, risk metrics

```bash
TESTNET_RPC=https://testnet.monad.xyz pytest tests/validation -v
```

### Transaction Tests (`tests/transaction/`)
- **Requires**: Testnet RPC
- **Safe**: No transactions submitted
- **Coverage**: Transaction building, gas estimation, signer interface

```bash
TESTNET_RPC=https://testnet.monad.xyz pytest tests/transaction -v
```

## Running Tests

### Prerequisites

1. Build the SDK:
```bash
cd py
maturin develop --release
```

2. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Quick Start

```bash
# Run all unit tests (fast, offline)
pytest tests/unit -v

# Run with coverage
pytest tests/unit --cov=perpl_sdk --cov-report=html

# Run specific test file
pytest tests/unit/test_numeric.py -v

# Run specific test class
pytest tests/unit/test_numeric.py::TestUD64 -v

# Run specific test
pytest tests/unit/test_numeric.py::TestUD64::test_from_string_integer -v
```

### Environment Variables

| Variable | Description | Required For |
|----------|-------------|--------------|
| `TESTNET_RPC` | Testnet RPC URL | integration, validation, transaction |
| `TEST_ACCOUNT_ADDRESS` | Known account for testing | account validation tests |

### Test Markers

Run tests by category:

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Only fast tests
pytest -m "unit and not slow"
```

### Coverage Report

Generate HTML coverage report:

```bash
pytest --cov=perpl_sdk --cov-report=html --cov-report=term
open htmlcov/index.html
```

### Full Test Suite

Run everything:

```bash
# Set RPC URL
export TESTNET_RPC=https://testnet.monad.xyz

# Run all tests with coverage
pytest --cov=perpl_sdk --cov-report=html -v

# Or with parallel execution (if pytest-xdist installed)
pytest -n auto --cov=perpl_sdk -v
```

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── fixtures/
│   └── expected_values.json
├── unit/
│   ├── test_numeric.py   # UD64, UD128, D256
│   ├── test_types.py     # Enums, StateInstant
│   ├── test_order_request.py
│   └── test_chain.py
├── integration/
│   ├── test_snapshot.py
│   ├── test_perpetuals.py
│   ├── test_accounts.py
│   ├── test_orderbook.py
│   └── test_positions.py
├── validation/
│   ├── test_cross_reference.py
│   ├── test_funding_rates.py
│   └── test_risk_metrics.py
└── transaction/
    ├── test_tx_builder.py
    ├── test_gas_estimation.py
    └── test_signer.py
```

## Writing New Tests

### Example Unit Test

```python
import pytest
from perpl_sdk import UD64

pytestmark = [pytest.mark.unit]

class TestMyFeature:
    def test_basic_operation(self):
        val = UD64.from_str("100.0")
        assert float(str(val)) == 100.0
```

### Example Integration Test

```python
import pytest

pytestmark = [pytest.mark.integration]

class TestMyIntegration:
    @pytest.mark.timeout(60)
    def test_with_snapshot(self, exchange_snapshot):
        # Uses the session-scoped fixture
        assert exchange_snapshot.instant.block_number > 0
```

## Troubleshooting

### SDK not built
```
SKIPPED: SDK not built
```
Run `maturin develop --release` first.

### TESTNET_RPC not set
```
SKIPPED: TESTNET_RPC not set
```
Set the environment variable before running integration tests.

### Test timeout
Increase timeout or check network connectivity:
```bash
pytest tests/integration -v --timeout=300
```
