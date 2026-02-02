//! Chain Configuration
//!
//! Chain-specific configuration and deployment information.

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use dex_sdk::Chain as SdkChain;
use crate::ffi::helpers::{parse_address, format_address};

/// Chain configuration for the exchange
///
/// Contains network-specific deployment information including chain ID,
/// contract addresses, and available perpetual markets.
///
/// Example:
///     ```python
///     # Use the testnet configuration
///     chain = Chain.testnet()
///     print(f"Chain ID: {chain.chain_id}")
///     print(f"Exchange: {chain.exchange}")
///     print(f"Perpetuals: {chain.perpetuals}")
///     
///     # Or create a custom configuration
///     chain = Chain.custom(
///         chain_id=10143,
///         collateral_token="0x...",
///         deployed_at_block=62953,
///         exchange="0x...",
///         perpetuals=[16, 32, 48, 64, 256]
///     )
///     ```
#[pyclass(name = "Chain", module = "perpl_sdk")]
#[derive(Clone)]
pub struct Chain(pub SdkChain);

#[pymethods]
impl Chain {
    /// Get the Monad testnet configuration
    ///
    /// Returns a Chain configured for the Monad testnet with pre-set
    /// contract addresses and available perpetual markets.
    ///
    /// Returns:
    ///     Chain: Testnet configuration
    #[staticmethod]
    fn testnet() -> Self {
        Self(SdkChain::testnet())
    }
    
    /// Create a custom chain configuration
    ///
    /// Use this to connect to a custom deployment or different network.
    ///
    /// Args:
    ///     chain_id: Network chain ID
    ///     collateral_token: Collateral token contract address (hex string)
    ///     deployed_at_block: Block number the exchange was deployed at
    ///     exchange: Exchange contract address (hex string)
    ///     perpetuals: List of available perpetual market IDs
    ///
    /// Returns:
    ///     Chain: Custom configuration
    ///
    /// Raises:
    ///     ValueError: If addresses are invalid
    #[staticmethod]
    fn custom(
        chain_id: u64,
        collateral_token: &str,
        deployed_at_block: u64,
        exchange: &str,
        perpetuals: Vec<u32>,
    ) -> PyResult<Self> {
        let collateral_token = parse_address(collateral_token)?;
        let exchange = parse_address(exchange)?;
        
        Ok(Self(SdkChain::custom(
            chain_id,
            collateral_token,
            deployed_at_block,
            exchange,
            perpetuals,
        )))
    }
    
    /// Network chain ID (e.g., 10143 for Monad testnet)
    #[getter]
    fn chain_id(&self) -> u64 {
        self.0.chain_id()
    }
    
    /// Collateral token contract address (hex string)
    #[getter]
    fn collateral_token(&self) -> String {
        format_address(&self.0.collateral_token())
    }
    
    /// Block number the exchange contract was deployed at
    #[getter]
    fn deployed_at_block(&self) -> u64 {
        self.0.deployed_at_block()
    }
    
    /// Exchange contract address (hex string)
    #[getter]
    fn exchange(&self) -> String {
        format_address(&self.0.exchange())
    }
    
    /// List of available perpetual market IDs
    #[getter]
    fn perpetuals(&self) -> Vec<u32> {
        self.0.perpetuals().to_vec()
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Chain(chain_id={}, exchange={}, perpetuals={:?})",
            self.0.chain_id(),
            format_address(&self.0.exchange()),
            self.0.perpetuals()
        )
    }
}

impl From<SdkChain> for Chain {
    fn from(value: SdkChain) -> Self {
        Self(value)
    }
}

impl From<Chain> for SdkChain {
    fn from(value: Chain) -> Self {
        value.0
    }
}

