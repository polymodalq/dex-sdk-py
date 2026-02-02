//! Snapshot Builder
//!
//! Builder pattern for creating exchange state snapshots.
//!
//! ## Design Note
//!
//! This implementation uses a blocking interface with an internal Tokio runtime
//! to avoid the pyo3-asyncio 0.21 dependency issue. Python users can still use
//! this in async contexts via `asyncio.to_thread()` if needed.

use pyo3::prelude::*;
use dex_sdk::state::SnapshotBuilder as SdkSnapshotBuilder;
use alloy::providers::ProviderBuilder;
use alloy::rpc::client::RpcClient;
use alloy::eips::BlockId;
use crate::bindings::{chain::Chain, state::Exchange};
use crate::ffi::error::to_py_err;

/// Builder for creating exchange state snapshots
///
/// This builder allows you to configure which perpetuals and accounts to track,
/// and at which block to capture the snapshot.
///
/// Example:
///     ```python
///     from perpl_sdk import Chain, SnapshotBuilder
///     
///     chain = Chain.testnet()
///     builder = SnapshotBuilder(chain, "https://testnet.monad.xyz")
///     builder = builder.with_perpetuals([0, 1, 2])
///     builder = builder.with_accounts(["0x..."])
///     
///     exchange = builder.build()
///     print(f"Snapshot at block {exchange.instant().block_number()}")
///     ```
#[pyclass(name = "SnapshotBuilder", module = "perpl_sdk")]
pub struct SnapshotBuilder {
    chain: Chain,
    rpc_url: String,
    block_id: Option<u64>,
    perpetuals: Option<Vec<u32>>,
    accounts: Option<Vec<String>>,
    orders_per_batch: Option<usize>,
    all_positions: bool,
    positions_per_batch: Option<usize>,
}

#[pymethods]
impl SnapshotBuilder {
    /// Create a new SnapshotBuilder
    ///
    /// Args:
    ///     chain: Chain configuration
    ///     rpc_url: RPC endpoint URL
    ///
    /// Returns:
    ///     SnapshotBuilder instance
    #[new]
    fn new(chain: Chain, rpc_url: String) -> Self {
        Self {
            chain,
            rpc_url,
            block_id: None,
            perpetuals: None,
            accounts: None,
            orders_per_batch: None,
            all_positions: false,
            positions_per_batch: None,
        }
    }
    
    /// Set the block number to fetch state at (default: latest)
    ///
    /// Args:
    ///     block_number: Block number
    ///
    /// Returns:
    ///     Self for chaining
    fn at_block(mut slf: PyRefMut<'_, Self>, block_number: u64) -> PyRefMut<'_, Self> {
        slf.block_id = Some(block_number);
        slf
    }
    
    /// Set the perpetuals to track
    ///
    /// Args:
    ///     perpetual_ids: List of perpetual IDs
    ///
    /// Returns:
    ///     Self for chaining
    fn with_perpetuals(mut slf: PyRefMut<'_, Self>, perpetual_ids: Vec<u32>) -> PyRefMut<'_, Self> {
        slf.perpetuals = Some(perpetual_ids);
        slf
    }
    
    /// Set the accounts to track
    ///
    /// Mutually exclusive with with_all_positions.
    ///
    /// Args:
    ///     addresses: List of account addresses (hex strings)
    ///
    /// Returns:
    ///     Self for chaining
    fn with_accounts(mut slf: PyRefMut<'_, Self>, addresses: Vec<String>) -> PyResult<PyRefMut<'_, Self>> {
        slf.accounts = Some(addresses);
        slf.all_positions = false;
        Ok(slf)
    }
    
    /// Set the batch size for fetching orders
    ///
    /// Args:
    ///     batch_size: Number of orders to fetch per call
    ///
    /// Returns:
    ///     Self for chaining
    fn with_orders_per_batch(mut slf: PyRefMut<'_, Self>, batch_size: usize) -> PyRefMut<'_, Self> {
        slf.orders_per_batch = Some(batch_size);
        slf
    }
    
    /// Fetch all positions across all accounts (without full account state)
    ///
    /// This is useful for scanning all active positions without needing
    /// specific account addresses. Mutually exclusive with with_accounts.
    ///
    /// Returns:
    ///     Self for chaining
    fn with_all_positions(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.all_positions = true;
        slf.accounts = None;
        slf
    }
    
    /// Set the batch size for fetching positions
    ///
    /// Args:
    ///     batch_size: Number of positions to fetch per call (default: 3000)
    ///
    /// Returns:
    ///     Self for chaining
    fn with_positions_per_batch(mut slf: PyRefMut<'_, Self>, batch_size: usize) -> PyRefMut<'_, Self> {
        slf.positions_per_batch = Some(batch_size);
        slf
    }
    
    /// Build the exchange snapshot
    ///
    /// This method blocks until the snapshot is fetched. It uses the shared
    /// Tokio runtime for efficient async execution.
    ///
    /// For async Python contexts, use `asyncio.to_thread(builder.build)`.
    ///
    /// Returns:
    ///     Exchange snapshot
    ///
    /// Raises:
    ///     DexError: If snapshot building fails
    fn build(&self, py: Python) -> PyResult<Exchange> {
        py.allow_threads(|| {
            // Use shared runtime for async operations
            crate::ffi::runtime::block_on(self.build_async())
        })
    }
    
    fn __repr__(&self) -> String {
        format!(
            "SnapshotBuilder(rpc_url='{}', perpetuals={:?}, accounts={:?})",
            self.rpc_url,
            self.perpetuals.as_ref().map(|p| p.len()),
            self.accounts.as_ref().map(|a| a.len())
        )
    }
}

impl SnapshotBuilder {
    /// Internal async implementation
    async fn build_async(&self) -> PyResult<Exchange> {
        // Create RPC client and provider
        let url: url::Url = self.rpc_url.parse()
            .map_err(|e| to_py_err(format!("Invalid RPC URL: {}", e)))?;
        let client = RpcClient::builder().http(url);
        let provider = ProviderBuilder::new().connect_client(client);
        
        // Create builder
        let mut builder = SdkSnapshotBuilder::new(&self.chain.0, provider);
        
        // Apply configurations
        if let Some(block) = self.block_id {
            builder = builder.at_block(BlockId::number(block));
        }
        
        if let Some(ref perpetuals) = self.perpetuals {
            builder = builder.with_perpetuals(perpetuals.clone());
        }
        
        if let Some(ref accounts) = self.accounts {
            let addresses: Result<Vec<_>, _> = accounts
                .iter()
                .map(|addr| addr.parse())
                .collect();
            let addresses = addresses
                .map_err(|e| to_py_err(format!("Invalid address: {}", e)))?;
            builder = builder.with_accounts(addresses);
        }
        
        if let Some(batch_size) = self.orders_per_batch {
            builder = builder.with_orders_per_batch(batch_size);
        }
        
        if self.all_positions {
            builder = builder.with_all_positions();
        }
        
        if let Some(batch_size) = self.positions_per_batch {
            builder = builder.with_positions_per_batch(batch_size);
        }
        
        // Build snapshot
        let exchange = builder.build().await
            .map_err(|e| to_py_err(format!("Snapshot build failed: {}", e)))?;
        
        Ok(Exchange { inner: exchange })
    }
}

/// Helper function to create a SnapshotBuilder from Python
///
/// Args:
///     chain: Chain configuration
///     rpc_url: RPC endpoint URL
///     perpetual_ids: Optional list of perpetual IDs to track
///     account_addresses: Optional list of account addresses to track
///     block_number: Optional block number to fetch at
///
/// Returns:
///     Exchange snapshot
///
/// Example:
///     ```python
///     from perpl_sdk import snapshot
///     
///     exchange = snapshot(
///         chain=Chain.testnet(),
///         rpc_url="https://testnet.monad.xyz",
///         perpetual_ids=[0, 1, 2],
///         account_addresses=["0x..."],
///         block_number=12345
///     )
///     ```
#[pyfunction]
#[pyo3(signature = (chain, rpc_url, perpetual_ids=None, account_addresses=None, block_number=None))]
pub fn snapshot(
    py: Python,
    chain: Chain,
    rpc_url: String,
    perpetual_ids: Option<Vec<u32>>,
    account_addresses: Option<Vec<String>>,
    block_number: Option<u64>,
) -> PyResult<Exchange> {
    let mut builder = SnapshotBuilder::new(chain, rpc_url);
    
    if let Some(perps) = perpetual_ids {
        builder.perpetuals = Some(perps);
    }
    
    if let Some(accounts) = account_addresses {
        builder.accounts = Some(accounts);
    }
    
    if let Some(block) = block_number {
        builder.block_id = Some(block);
    }
    
    builder.build(py)
}
