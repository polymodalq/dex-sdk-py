//! Transaction Building Infrastructure
//!
//! This module provides the transaction building and signing infrastructure
//! for executing orders on the Perpl DEX.
//!
//! ## Architecture
//!
//! ```text
//! OrderRequest --> TransactionBuilder --> UnsignedTransaction
//!                                              |
//!                                         Signer (external)
//!                                              |
//!                                              v
//!                                       SignedTransaction
//!                                              |
//!                                              v
//!                                    TransactionReceipt
//! ```
//!
//! ## External Signer Pattern
//!
//! The SDK builds unsigned transactions. Signing is delegated to external
//! signers (hardware wallets, cloud KMS, etc.) via the `Signer` base class.

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::exceptions::{PyNotImplementedError, PyValueError};
use alloy::primitives::{Address, U256, Bytes, keccak256};
use alloy::rpc::types::TransactionRequest;
use alloy::providers::Provider;
use alloy::rpc::client::RpcClient;

use crate::bindings::chain::Chain;
use crate::bindings::state::Exchange;
use crate::bindings::types::OrderRequest;
use crate::ffi::numeric::PyUD128;
use crate::ffi::error::to_py_err;
use crate::ffi::runtime;

/// Base class for external signers
///
/// Subclass this to implement your own signing logic.
/// The SDK builds unsigned transactions; you provide the signature.
///
/// Example:
///     ```python
///     from perpl_sdk import Signer
///     from eth_account import Account
///     
///     class LocalSigner(Signer):
///         def __init__(self, private_key: str):
///             super().__init__()
///             self._account = Account.from_key(private_key)
///         
///         def sign(self, tx_hash: bytes) -> bytes:
///             sig = self._account.signHash(tx_hash)
///             return sig.signature
///         
///         def address(self) -> str:
///             return self._account.address
///     ```
#[pyclass(name = "Signer", module = "perpl_sdk", subclass)]
pub struct Signer;

#[pymethods]
impl Signer {
    #[new]
    fn new() -> Self {
        Self
    }
    
    /// Sign a transaction hash
    ///
    /// Override this method to implement your signing logic.
    ///
    /// Args:
    ///     tx_hash: 32-byte Keccak256 hash of the unsigned transaction
    ///
    /// Returns:
    ///     65-byte ECDSA signature (r || s || v)
    fn sign(&self, _tx_hash: &Bound<'_, PyBytes>) -> PyResult<Py<PyBytes>> {
        Err(PyNotImplementedError::new_err(
            "Signer.sign() must be overridden in a subclass"
        ))
    }
    
    /// Get the signer's Ethereum address
    ///
    /// Override this method to return your signer's address.
    ///
    /// Returns:
    ///     Checksummed Ethereum address (0x prefixed)
    fn address(&self) -> PyResult<String> {
        Err(PyNotImplementedError::new_err(
            "Signer.address() must be overridden in a subclass"
        ))
    }
    
    fn __repr__(&self) -> String {
        "Signer(base class - override sign() and address())".to_string()
    }
}

/// Builder for creating transactions
///
/// Constructs unsigned transactions that can be signed by any external signer.
///
/// Example:
///     ```python
///     tx_builder = TransactionBuilder(chain, "https://rpc.monad.xyz")
///     
///     # Build an order transaction
///     unsigned_tx = tx_builder.build_order_tx(request, exchange, signer.address())
///     
///     # Sign externally using eth_account, web3.py, hardware wallet, etc.
///     from eth_account import Account
///     signed = Account.sign_transaction(unsigned_tx.to_dict(), private_key)
///     
///     # Submit using web3.py or similar
///     tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
///     ```
#[pyclass(name = "TransactionBuilder", module = "perpl_sdk")]
pub struct TransactionBuilder {
    chain: Chain,
    rpc_url: String,
}

#[pymethods]
impl TransactionBuilder {
    /// Create a new TransactionBuilder
    ///
    /// Args:
    ///     chain: Chain configuration
    ///     rpc_url: RPC endpoint URL
    #[new]
    fn new(chain: Chain, rpc_url: String) -> Self {
        Self { chain, rpc_url }
    }
    
    /// Build an unsigned order transaction
    ///
    /// Creates a transaction dict for submitting an order request to the exchange.
    /// The returned UnsignedTransaction can be converted to a dict for signing
    /// with eth_account, web3.py, or other signing libraries.
    ///
    /// Args:
    ///     request: The order request to submit
    ///     exchange: Exchange state (for converter access)
    ///     from_address: Sender address (hex string)
    ///
    /// Returns:
    ///     UnsignedTransaction ready for signing
    fn build_order_tx(
        &self,
        py: Python<'_>,
        request: &OrderRequest,
        exchange: &Exchange,
        from_address: String,
    ) -> PyResult<UnsignedTransaction> {
        let from: Address = from_address.parse()
            .map_err(|e| to_py_err(format!("Invalid from address: {}", e)))?;
        
        let chain = self.chain.clone();
        let rpc_url = self.rpc_url.clone();
        let request_inner = request.clone();
        let exchange_inner = exchange.inner.clone();
        
        py.allow_threads(|| {
            runtime::block_on(async {
                build_order_tx_async(chain, rpc_url, request_inner, exchange_inner, from).await
            })
        })
    }
    
    /// Get the exchange contract address
    #[getter]
    fn exchange_address(&self) -> String {
        format!("{:?}", self.chain.0.exchange())
    }
    
    /// Get the chain ID
    #[getter]
    fn chain_id(&self) -> u64 {
        self.chain.0.chain_id()
    }
    
    fn __repr__(&self) -> String {
        format!(
            "TransactionBuilder(chain_id={}, rpc_url='{}')",
            self.chain.0.chain_id(),
            self.rpc_url
        )
    }
}

/// Unsigned transaction ready for signing
///
/// Contains all transaction fields except the signature.
/// Convert to a dict using `to_dict()` for use with signing libraries.
#[pyclass(name = "UnsignedTransaction", module = "perpl_sdk")]
#[derive(Clone)]
pub struct UnsignedTransaction {
    /// Destination address (exchange contract)
    pub(crate) to: Address,
    /// Encoded calldata
    pub(crate) data: Vec<u8>,
    /// Transaction value (0 for order transactions)
    pub(crate) value: U256,
    /// Gas limit
    pub(crate) gas_limit: u64,
    /// Account nonce
    pub(crate) nonce: u64,
    /// Chain ID
    pub(crate) chain_id: u64,
    /// Gas price
    pub(crate) gas_price: U256,
}

#[pymethods]
impl UnsignedTransaction {
    /// Get the destination address
    #[getter]
    fn to(&self) -> String {
        format!("{:?}", self.to)
    }
    
    /// Get the calldata as hex string
    #[getter]
    fn data(&self) -> String {
        format!("0x{}", hex::encode(&self.data))
    }
    
    /// Get the calldata as bytes
    fn data_bytes<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new_bound(py, &self.data)
    }
    
    /// Get the transaction value in wei
    #[getter]
    fn value(&self) -> String {
        format!("{}", self.value)
    }
    
    /// Get the gas limit
    #[getter]
    fn gas_limit(&self) -> u64 {
        self.gas_limit
    }
    
    /// Get the nonce
    #[getter]
    fn nonce(&self) -> u64 {
        self.nonce
    }
    
    /// Get the chain ID
    #[getter]
    fn chain_id(&self) -> u64 {
        self.chain_id
    }
    
    /// Get the gas price in wei
    #[getter]
    fn gas_price(&self) -> String {
        format!("{}", self.gas_price)
    }
    
    /// Convert to a dict for use with signing libraries
    ///
    /// Returns a dict compatible with eth_account.sign_transaction():
    /// - 'to': address
    /// - 'data': hex calldata
    /// - 'value': int wei
    /// - 'gas': int gas limit
    /// - 'nonce': int
    /// - 'chainId': int
    /// - 'gasPrice': int (for legacy tx)
    ///
    /// Example:
    ///     ```python
    ///     from eth_account import Account
    ///     
    ///     unsigned_tx = tx_builder.build_order_tx(request, exchange, my_address)
    ///     tx_dict = unsigned_tx.to_dict()
    ///     signed = Account.sign_transaction(tx_dict, private_key)
    ///     ```
    fn to_dict(&self, py: Python<'_>) -> PyResult<PyObject> {
        use pyo3::types::PyDict;
        
        let dict = PyDict::new_bound(py);
        dict.set_item("to", format!("{:?}", self.to))?;
        dict.set_item("data", format!("0x{}", hex::encode(&self.data)))?;
        dict.set_item("value", self.value.to::<u128>())?;
        dict.set_item("gas", self.gas_limit)?;
        dict.set_item("nonce", self.nonce)?;
        dict.set_item("chainId", self.chain_id)?;
        dict.set_item("gasPrice", self.gas_price.to::<u128>())?;
        
        Ok(dict.into())
    }
    
    fn __repr__(&self) -> String {
        format!(
            "UnsignedTransaction(to={:?}, nonce={}, gas_limit={})",
            self.to, self.nonce, self.gas_limit
        )
    }
}

/// Signed transaction (raw bytes)
#[pyclass(name = "SignedTransaction", module = "perpl_sdk")]
#[derive(Clone)]
pub struct SignedTransaction {
    pub(crate) raw_tx: Vec<u8>,
    pub(crate) tx_hash: String,
}

#[pymethods]
impl SignedTransaction {
    /// Create from raw transaction bytes and hash
    ///
    /// Typically you won't create this directly - use eth_account or web3.py
    /// to sign and submit transactions.
    #[new]
    fn new(raw_tx: &Bound<'_, PyBytes>, tx_hash: String) -> Self {
        Self {
            raw_tx: raw_tx.as_bytes().to_vec(),
            tx_hash,
        }
    }
    
    /// Get the raw transaction bytes
    fn raw<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        PyBytes::new_bound(py, &self.raw_tx)
    }
    
    /// Get the raw transaction as hex
    fn raw_hex(&self) -> String {
        format!("0x{}", hex::encode(&self.raw_tx))
    }
    
    /// Get the transaction hash
    #[getter]
    fn tx_hash(&self) -> String {
        self.tx_hash.clone()
    }
    
    fn __repr__(&self) -> String {
        format!("SignedTransaction(hash={})", self.tx_hash)
    }
}

/// Transaction receipt after execution
#[pyclass(name = "TransactionReceipt", module = "perpl_sdk")]
#[derive(Clone)]
pub struct TransactionReceipt {
    /// Transaction hash
    pub(crate) tx_hash: String,
    /// Block number
    pub(crate) block_number: u64,
    /// Gas used
    pub(crate) gas_used: u64,
    /// Whether transaction succeeded
    pub(crate) success: bool,
}

#[pymethods]
impl TransactionReceipt {
    #[new]
    fn new(tx_hash: String, block_number: u64, gas_used: u64, success: bool) -> Self {
        Self { tx_hash, block_number, gas_used, success }
    }
    
    /// Get the transaction hash
    #[getter]
    fn tx_hash(&self) -> String {
        self.tx_hash.clone()
    }
    
    /// Get the block number
    #[getter]
    fn block_number(&self) -> u64 {
        self.block_number
    }
    
    /// Get the gas used
    #[getter]
    fn gas_used(&self) -> u64 {
        self.gas_used
    }
    
    /// Whether the transaction succeeded
    #[getter]
    fn success(&self) -> bool {
        self.success
    }
    
    fn __repr__(&self) -> String {
        format!(
            "TransactionReceipt(hash={}, block={}, success={})",
            self.tx_hash, self.block_number, self.success
        )
    }
}

// =============================================================================
// Internal async implementations
// =============================================================================

async fn build_order_tx_async(
    chain: Chain,
    rpc_url: String,
    request: OrderRequest,
    exchange: dex_sdk::state::Exchange,
    from: Address,
) -> PyResult<UnsignedTransaction> {
    use alloy::providers::ProviderBuilder;
    
    // Create provider
    let url: url::Url = rpc_url.parse()
        .map_err(|e| to_py_err(format!("Invalid RPC URL: {}", e)))?;
    let client = RpcClient::builder().http(url);
    let provider = ProviderBuilder::new().connect_client(client);
    
    // Prepare the order request to get OrderDesc
    let order_desc = request.inner.prepare(&exchange);
    
    // Encode the transaction data
    let exchange_instance = dex_sdk::abi::dex::Exchange::new(
        chain.0.exchange(),
        provider.clone(),
    );
    
    // Use execOpsAndOrders with single order
    // Third argument is `revertOnError` - set to true for simpler error handling
    let call = exchange_instance.execOpsAndOrders(
        vec![],  // No ops
        vec![order_desc],  // Single order
        true,  // revertOnError
    );
    
    let data = call.calldata().to_vec();
    
    // Get nonce
    let nonce = provider.get_transaction_count(from)
        .await
        .map_err(|e| to_py_err(format!("Failed to get nonce: {}", e)))?;
    
    // Build transaction request for gas estimation
    let tx_request = TransactionRequest::default()
        .from(from)
        .to(chain.0.exchange())
        .input(Bytes::from(data.clone()).into());
    
    // Estimate gas
    let gas_estimate = provider.estimate_gas(tx_request)
        .await
        .map_err(|e| to_py_err(format!("Failed to estimate gas: {}", e)))?;
    
    // Add buffer to gas estimate
    let gas_limit = gas_estimate + gas_estimate / 10; // +10% buffer
    
    // Get gas price
    let gas_price = provider.get_gas_price()
        .await
        .map_err(|e| to_py_err(format!("Failed to get gas price: {}", e)))?;
    
    Ok(UnsignedTransaction {
        to: chain.0.exchange(),
        data,
        value: U256::ZERO,
        gas_limit,
        nonce,
        chain_id: chain.0.chain_id(),
        gas_price: U256::from(gas_price),
    })
}
