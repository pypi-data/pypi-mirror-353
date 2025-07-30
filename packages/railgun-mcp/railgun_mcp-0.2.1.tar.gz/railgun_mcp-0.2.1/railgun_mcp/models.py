#!/usr/bin/env python3
"""
Models and data structures for Railgun MCP Server
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# Enums for Railgun types
class TokenType(Enum):
    ERC20 = "ERC20"
    ERC721 = "ERC721"
    NATIVE = "NATIVE"


class StepType(Enum):
    APPROVE = "approve"
    SWAP = "swap"
    TRANSFER = "transfer"
    SHIELD = "shield"
    UNSHIELD = "unshield"
    ADD_LIQUIDITY = "add_liquidity"
    REMOVE_LIQUIDITY = "remove_liquidity"
    STAKE = "stake"
    UNSTAKE = "unstake"


class Network(Enum):
    ETHEREUM = "ethereum"
    ARBITRUM = "arbitrum"
    POLYGON = "polygon"
    BSC = "bsc"


class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Data classes
@dataclass
class Token:
    address: str
    symbol: str
    decimals: int
    type: TokenType
    chain_id: int


@dataclass
class TokenAmount:
    token: Token
    amount: str  # Wei amount as string


@dataclass
class Step:
    id: str
    type: StepType
    description: str
    inputs: List[TokenAmount]
    outputs: List[TokenAmount]
    contract_address: Optional[str] = None
    function_name: Optional[str] = None
    function_args: Optional[Dict[str, Any]] = None


@dataclass
class Recipe:
    id: str
    name: str
    description: str
    steps: List[Step]
    network: Network
    created_at: str


# Configuration
class Config:
    """Configuration management for Railgun MCP - Direct blockchain interaction"""

    def __init__(self):
        # Private key for wallet operations (required)
        self.private_key = os.getenv("RAILGUN_PRIVATE_KEY")

        # Wallet password for local encryption (optional)
        self.wallet_password = os.getenv("RAILGUN_WALLET_PASSWORD")

        # RPC endpoints for direct blockchain connection
        self.rpc_endpoints = {
            "ethereum": os.getenv(
                "ETHEREUM_RPC_URL", "https://eth-mainnet.g.alchemy.com/v2/your-api-key"
            ),
            "arbitrum": os.getenv(
                "ARBITRUM_RPC_URL", "https://arb-mainnet.g.alchemy.com/v2/your-api-key"
            ),
            "polygon": os.getenv(
                "POLYGON_RPC_URL",
                "https://polygon-mainnet.g.alchemy.com/v2/your-api-key",
            ),
            "bsc": os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org/"),
        }

        # RAILGUN smart contract addresses (mainnet)
        self.railgun_contracts = {
            "ethereum": {
                "proxy": "0xFA7093CDD9EE6932B4eb2c9e1cde7CE00B1FA4b9",
                "poseidon": "0x3e3a3D69dc66bA10737F531ed088954a9EC89d97",
                "verifier": "0x87C7fd0635Fb4E2FE5A3b40d5a57E96cE01a0B7a",
            },
            "polygon": {
                "proxy": "0x19b620929f97b7b990801496c3b361ca5def8c71",
                "poseidon": "0x3e3a3D69dc66bA10737F531ed088954a9EC89d97",
                "verifier": "0x87C7fd0635Fb4E2FE5A3b40d5a57E96cE01a0B7a",
            },
            "bsc": {
                "proxy": "0x590162bf4b50f6576a459b75309ee21d92178a10",
                "poseidon": "0x3e3a3D69dc66bA10737F531ed088954a9EC89d97",
                "verifier": "0x87C7fd0635Fb4E2FE5A3b40d5a57E96cE01a0B7a",
            },
        }

        # Network chain IDs
        self.chain_ids = {"ethereum": 1, "polygon": 137, "bsc": 56, "arbitrum": 42161}

        # Try to load from config file if env vars not set
        config_path = Path.home() / ".railgun" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    self.private_key = self.private_key or config_data.get(
                        "private_key"
                    )
                    self.wallet_password = self.wallet_password or config_data.get(
                        "wallet_password"
                    )
                    self.rpc_endpoints.update(config_data.get("rpc_endpoints", {}))

                    # Allow override of contract addresses if needed
                    if "railgun_contracts" in config_data:
                        for network, contracts in config_data[
                            "railgun_contracts"
                        ].items():
                            if network in self.railgun_contracts:
                                self.railgun_contracts[network].update(contracts)
                            else:
                                self.railgun_contracts[network] = contracts

            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

    def get_rpc_url(self, network: str) -> str:
        """Get RPC URL for a network"""
        return self.rpc_endpoints.get(network)

    def get_chain_id(self, network: str) -> int:
        """Get chain ID for a network"""
        return self.chain_ids.get(network, 1)

    def get_railgun_proxy(self, network: str) -> str:
        """Get RAILGUN proxy contract address for a network"""
        return self.railgun_contracts.get(network, {}).get("proxy")
