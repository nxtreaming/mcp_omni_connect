from os import getenv
from typing import Any, Dict, Optional

from omnicoreagent.core.tools.local_tools_registry import Tool
from omnicoreagent.core.utils import log_debug, log_error

try:
    from eth_account.account import LocalAccount
    from eth_account.datastructures import SignedTransaction
    from hexbytes import HexBytes
    from web3 import Web3
    from web3.main import Web3 as Web3Type
    from web3.providers.rpc import HTTPProvider
    from web3.types import TxParams, TxReceipt
except ImportError:
    LocalAccount = None
    SignedTransaction = None
    HexBytes = None
    Web3 = None
    Web3Type = None
    HTTPProvider = None
    TxParams = None
    TxReceipt = None



class EvmTools:
    def __init__(
        self,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
    ):
        if Web3 is None:
            raise ImportError(
                "Could not import `web3` python package. "
                "Please install it using `pip install web3`."
            )
        self.private_key = private_key or getenv("EVM_PRIVATE_KEY")
        self.rpc_url = rpc_url or getenv("EVM_RPC_URL")

        if not self.private_key:
            raise ValueError("Private Key is required")
        if not self.rpc_url:
            raise ValueError("RPC Url is needed to interact with EVM blockchain")

        if not self.private_key.startswith("0x"):
            self.private_key = f"0x{self.private_key}"

        self.web3_client: "Web3Type" = Web3(HTTPProvider(self.rpc_url))
        self.account: "LocalAccount" = self.web3_client.eth.account.from_key(self.private_key)
        log_debug(f"Your wallet address is: {self.account.address}")

    def get_tool(self) -> Tool:
        return Tool(
            name="evm_send_transaction",
            description="Send an ETH transaction to a given address.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_address": {"type": "string", "description": "Recipient address"},
                    "amount_in_wei": {"type": "integer", "description": "Amount of ETH in wei"},
                },
                "required": ["to_address", "amount_in_wei"],
            },
            function=self._send_transaction,
        )

    def _get_max_priority_fee_per_gas(self) -> int:
        return self.web3_client.to_wei(1, "gwei")

    def _get_max_fee_per_gas(self, max_priority_fee_per_gas: int) -> int:
        latest_block = self.web3_client.eth.get_block("latest")
        base_fee_per_gas = latest_block.get("baseFeePerGas")
        if base_fee_per_gas is None:
            raise ValueError("Base fee per gas not found in the latest block.")
        return (2 * base_fee_per_gas) + max_priority_fee_per_gas

    async def _send_transaction(self, to_address: str, amount_in_wei: int) -> Dict[str, Any]:
        try:
            max_priority_fee_per_gas = self._get_max_priority_fee_per_gas()
            max_fee_per_gas = self._get_max_fee_per_gas(max_priority_fee_per_gas)

            transaction_params: "TxParams" = {
                "from": self.account.address,
                "to": to_address,
                "value": amount_in_wei,  # type: ignore
                "nonce": self.web3_client.eth.get_transaction_count(self.account.address),
                "gas": 21000,
                "maxFeePerGas": max_fee_per_gas,  # type: ignore
                "maxPriorityFeePerGas": max_priority_fee_per_gas,  # type: ignore
                "chainId": self.web3_client.eth.chain_id,
                "type": 2,
            }

            signed_transaction: "SignedTransaction" = self.web3_client.eth.account.sign_transaction(
                transaction_params, self.private_key
            )
            transaction_hash: "HexBytes" = self.web3_client.eth.send_raw_transaction(signed_transaction.raw_transaction)
            log_debug(f"Transaction hash: 0x{transaction_hash.hex()}")

            transaction_receipt: "TxReceipt" = self.web3_client.eth.wait_for_transaction_receipt(transaction_hash)
            if transaction_receipt.get("status") == 1:
                tx_hash = f"0x{transaction_hash.hex()}"
                return {"status": "success", "data": {"tx_hash": tx_hash}, "message": "Transaction successful"}
            else:
                return {"status": "error", "data": None, "message": "Transaction failed"}
        except Exception as e:
            log_error(f"Error sending transaction: {e}")
            return {"status": "error", "data": None, "message": str(e)}
