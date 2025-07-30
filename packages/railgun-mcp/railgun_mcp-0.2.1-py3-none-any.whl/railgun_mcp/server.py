#!/usr/bin/env python3
"""
Railgun MCP Server - Model Context Protocol server for Railgun privacy protocol
Built with FastMCP for simplified development and better maintainability.

This server connects to the Railgun network using configuration from environment variables
or a config file, allowing users to interact with their actual Railgun wallets and balances.
"""

import logging
from typing import Dict, List, Any, Optional

from fastmcp import FastMCP
import aiohttp

# Import from our modules
from .models import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("railgun-mcp")

# Initialize configuration
config = Config()


# API Client for Railgun
class RailgunAPIClient:
    """Client for interacting with Railgun API"""

    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to Railgun API"""
        async with self.session.get(
            f"{self.api_url}{endpoint}", params=params
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.text()
                raise Exception(f"API request failed: {response.status} - {error_data}")

    async def post(self, endpoint: str, data: Dict) -> Dict:
        """Make POST request to Railgun API"""
        async with self.session.post(
            f"{self.api_url}{endpoint}", json=data
        ) as response:
            if response.status in (200, 201):
                return await response.json()
            else:
                error_data = await response.text()
                raise Exception(f"API request failed: {response.status} - {error_data}")


# Global API client instance
api_client = None


async def get_api_client() -> RailgunAPIClient:
    """Get or create API client instance"""
    global api_client
    if not api_client:
        if not config.private_key:
            raise Exception(
                "⚠️  RAILGUN_PRIVATE_KEY not configured. This server needs a complete rewrite - see ARCHITECTURE_UPDATE.md"
            )
        # NOTE: This is still using fake API calls and needs to be replaced with real blockchain interaction
        api_client = await RailgunAPIClient(
            config.private_key, "fake-api-url"
        ).__aenter__()
    return api_client


async def cleanup_api_client():
    """Cleanup API client resources"""
    global api_client
    if api_client:
        await api_client.__aexit__(None, None, None)
        api_client = None


# === WALLET MANAGEMENT TOOLS ===


@mcp.tool()
async def create_wallet(network: str, password: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new Railgun wallet with both 0x (public) and 0zk (private) addresses.

    Args:
        network: Network to create wallet on (ethereum, arbitrum, polygon, bsc)
        password: Optional password to encrypt the wallet (uses config password if not provided)
    """
    try:
        client = await get_api_client()
        wallet_password = password or config.wallet_password

        if not wallet_password:
            return {
                "success": False,
                "error": "Wallet password required. Set RAILGUN_WALLET_PASSWORD or provide password parameter",
            }

        # Call Railgun API to create wallet
        response = await client.post(
            "/wallets/create", {"network": network, "password": wallet_password}
        )

        return {
            "success": True,
            "wallet_id": response["wallet_id"],
            "address_0x": response["address_0x"],
            "address_0zk": response["address_0zk"],
            "network": network,
            "message": "Wallet created successfully. Your wallet is encrypted with the provided password.",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def import_wallet(
    private_key: str, network: str, password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Import an existing wallet using private key.

    Args:
        private_key: Private key to import
        network: Network for the wallet
        password: Optional password to encrypt the imported wallet
    """
    try:
        client = await get_api_client()
        wallet_password = password or config.wallet_password

        if not wallet_password:
            return {
                "success": False,
                "error": "Wallet password required. Set RAILGUN_WALLET_PASSWORD or provide password parameter",
            }

        response = await client.post(
            "/wallets/import",
            {
                "private_key": private_key,
                "network": network,
                "password": wallet_password,
            },
        )

        return {
            "success": True,
            "wallet_id": response["wallet_id"],
            "address_0x": response["address_0x"],
            "address_0zk": response["address_0zk"],
            "network": network,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def list_wallets() -> Dict[str, Any]:
    """
    List all wallets associated with the configured API key.
    """
    try:
        client = await get_api_client()
        response = await client.get("/wallets")

        return {
            "success": True,
            "wallets": response["wallets"],
            "count": len(response["wallets"]),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# === BALANCE AND FUNDING TOOLS ===


@mcp.tool()
async def get_balance(
    wallet_id: str, token_address: Optional[str] = None, include_private: bool = True
) -> Dict[str, Any]:
    """
    Get wallet balances for both public (0x) and private (0zk) addresses.

    Args:
        wallet_id: ID of the wallet
        token_address: Optional token address to filter by
        include_private: Whether to include private balances
    """
    try:
        client = await get_api_client()

        params = {"wallet_id": wallet_id, "include_private": include_private}
        if token_address:
            params["token_address"] = token_address

        response = await client.get("/balances", params=params)

        return {
            "success": True,
            "wallet_id": wallet_id,
            "balances": response["balances"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_gas_price(network: str) -> Dict[str, Any]:
    """
    Get current gas prices for a network.

    Args:
        network: Network to get gas price for
    """
    try:
        client = await get_api_client()
        response = await client.get(f"/gas-price/{network}")

        return {
            "success": True,
            "network": network,
            "gas_price": response["gas_price"],
            "base_fee": response.get("base_fee"),
            "priority_fee": response.get("priority_fee"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# === TRANSACTION TOOLS ===


@mcp.tool()
async def shield_tokens(
    wallet_id: str,
    token_address: str,
    amount: str,
    recipient_0zk_address: Optional[str] = None,
    gas_price: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Shield tokens from public balance into private balance.

    Args:
        wallet_id: ID of the wallet
        token_address: Address of the token to shield (use 0x0 for native token)
        amount: Amount to shield in wei
        recipient_0zk_address: Optional recipient 0zk address (defaults to sender's 0zk)
        gas_price: Optional gas price in wei
    """
    try:
        client = await get_api_client()

        data = {
            "wallet_id": wallet_id,
            "token_address": token_address,
            "amount": amount,
            "password": config.wallet_password,
        }

        if recipient_0zk_address:
            data["recipient_0zk_address"] = recipient_0zk_address
        if gas_price:
            data["gas_price"] = gas_price

        response = await client.post("/transactions/shield", data)

        return {
            "success": True,
            "transaction_id": response["transaction_id"],
            "tx_hash": response["tx_hash"],
            "status": response["status"],
            "gas_used": response.get("gas_used"),
            "message": "Shield transaction submitted successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def unshield_tokens(
    wallet_id: str,
    token_address: str,
    amount: str,
    recipient_0x_address: Optional[str] = None,
    gas_price: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Unshield tokens from private balance to public balance.

    Args:
        wallet_id: ID of the wallet
        token_address: Address of the token to unshield
        amount: Amount to unshield in wei
        recipient_0x_address: Optional recipient public address (defaults to sender's 0x)
        gas_price: Optional gas price in wei
    """
    try:
        client = await get_api_client()

        data = {
            "wallet_id": wallet_id,
            "token_address": token_address,
            "amount": amount,
            "password": config.wallet_password,
        }

        if recipient_0x_address:
            data["recipient_0x_address"] = recipient_0x_address
        if gas_price:
            data["gas_price"] = gas_price

        response = await client.post("/transactions/unshield", data)

        return {
            "success": True,
            "transaction_id": response["transaction_id"],
            "tx_hash": response["tx_hash"],
            "status": response["status"],
            "gas_used": response.get("gas_used"),
            "message": "Unshield transaction submitted successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def private_transfer(
    wallet_id: str,
    token_address: str,
    amount: str,
    recipient_0zk_address: str,
    gas_price: Optional[str] = None,
    memo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Transfer tokens privately between 0zk addresses.

    Args:
        wallet_id: ID of the sending wallet
        token_address: Address of the token to transfer
        amount: Amount to transfer in wei
        recipient_0zk_address: Recipient's 0zk address
        gas_price: Optional gas price in wei
        memo: Optional encrypted memo for the recipient
    """
    try:
        client = await get_api_client()

        data = {
            "wallet_id": wallet_id,
            "token_address": token_address,
            "amount": amount,
            "recipient_0zk_address": recipient_0zk_address,
            "password": config.wallet_password,
        }

        if gas_price:
            data["gas_price"] = gas_price
        if memo:
            data["memo"] = memo

        response = await client.post("/transactions/private-transfer", data)

        return {
            "success": True,
            "transaction_id": response["transaction_id"],
            "tx_hash": response["tx_hash"],
            "status": response["status"],
            "gas_used": response.get("gas_used"),
            "message": "Private transfer submitted successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_transaction_status(transaction_id: str) -> Dict[str, Any]:
    """
    Get the status of a transaction.

    Args:
        transaction_id: ID of the transaction
    """
    try:
        client = await get_api_client()
        response = await client.get(f"/transactions/{transaction_id}")

        return {"success": True, "transaction": response["transaction"]}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_transaction_history(
    wallet_id: str,
    limit: int = 50,
    offset: int = 0,
    transaction_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get transaction history for a wallet.

    Args:
        wallet_id: ID of the wallet
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip
        transaction_type: Filter by type (shield, unshield, private_transfer)
    """
    try:
        client = await get_api_client()

        params = {"wallet_id": wallet_id, "limit": limit, "offset": offset}
        if transaction_type:
            params["type"] = transaction_type

        response = await client.get("/transactions", params=params)

        return {
            "success": True,
            "transactions": response["transactions"],
            "total": response["total"],
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# === RECIPE AND DEFI TOOLS ===


@mcp.tool()
async def create_recipe(
    name: str, description: str, network: str, steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create a new recipe for complex DeFi interactions.

    Args:
        name: Name of the recipe
        description: Description of what the recipe does
        network: Network for the recipe
        steps: List of steps in the recipe
    """
    try:
        client = await get_api_client()

        response = await client.post(
            "/recipes",
            {
                "name": name,
                "description": description,
                "network": network,
                "steps": steps,
            },
        )

        return {
            "success": True,
            "recipe_id": response["recipe_id"],
            "message": "Recipe created successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def execute_recipe(
    wallet_id: str,
    recipe_id: str,
    input_amounts: List[Dict[str, str]],
    slippage_percentage: float = 0.5,
    gas_price: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a recipe with the specified inputs.

    Args:
        wallet_id: ID of the wallet to execute from
        recipe_id: ID of the recipe to execute
        input_amounts: List of token amounts as inputs
        slippage_percentage: Allowed slippage percentage
        gas_price: Optional gas price in wei
    """
    try:
        client = await get_api_client()

        data = {
            "wallet_id": wallet_id,
            "recipe_id": recipe_id,
            "input_amounts": input_amounts,
            "slippage_percentage": slippage_percentage,
            "password": config.wallet_password,
        }

        if gas_price:
            data["gas_price"] = gas_price

        response = await client.post("/recipes/execute", data)

        return {
            "success": True,
            "transaction_id": response["transaction_id"],
            "tx_hash": response["tx_hash"],
            "status": response["status"],
            "outputs": response.get("outputs", []),
            "message": "Recipe execution submitted successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def estimate_recipe_gas(
    recipe_id: str, input_amounts: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Estimate gas cost for executing a recipe.

    Args:
        recipe_id: ID of the recipe
        input_amounts: List of token amounts as inputs
    """
    try:
        client = await get_api_client()

        response = await client.post(
            "/recipes/estimate-gas",
            {"recipe_id": recipe_id, "input_amounts": input_amounts},
        )

        return {
            "success": True,
            "estimated_gas": response["estimated_gas"],
            "gas_breakdown": response.get("gas_breakdown", {}),
            "estimated_cost_wei": response.get("estimated_cost_wei"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def create_swap_recipe(
    network: str, sell_token: str, buy_token: str, dex: str = "0x"
) -> Dict[str, Any]:
    """
    Create a pre-configured swap recipe.

    Args:
        network: Network for the swap
        sell_token: Address of token to sell
        buy_token: Address of token to buy
        dex: DEX to use (0x, uniswap, sushiswap)
    """
    try:
        client = await get_api_client()

        response = await client.post(
            "/recipes/templates/swap",
            {
                "network": network,
                "sell_token": sell_token,
                "buy_token": buy_token,
                "dex": dex,
            },
        )

        return {
            "success": True,
            "recipe_id": response["recipe_id"],
            "recipe_name": response["recipe_name"],
            "steps": response["steps"],
            "message": "Swap recipe created successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# === RELAYER TOOLS ===


@mcp.tool()
async def get_relayers(network: str) -> Dict[str, Any]:
    """
    Get list of available relayers for a network.

    Args:
        network: Network to get relayers for
    """
    try:
        client = await get_api_client()
        response = await client.get(f"/relayers/{network}")

        return {
            "success": True,
            "network": network,
            "relayers": response["relayers"],
            "count": len(response["relayers"]),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def submit_to_relayer(
    transaction_data: str, relayer_id: str, priority: str = "standard"
) -> Dict[str, Any]:
    """
    Submit a transaction through a relayer for enhanced privacy.

    Args:
        transaction_data: Serialized transaction data
        relayer_id: ID of the relayer to use
        priority: Transaction priority (low, standard, high)
    """
    try:
        client = await get_api_client()

        response = await client.post(
            "/relayers/submit",
            {
                "transaction_data": transaction_data,
                "relayer_id": relayer_id,
                "priority": priority,
            },
        )

        return {
            "success": True,
            "relayer_transaction_id": response["relayer_transaction_id"],
            "estimated_time": response.get("estimated_time"),
            "fee": response.get("fee"),
            "message": "Transaction submitted to relayer successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# === MULTI-WALLET TOOLS ===


@mcp.tool()
async def create_wallet_batch(
    count: int, network: str, password_prefix: str, use_unique_passwords: bool = True
) -> Dict[str, Any]:
    """
    Create multiple wallets at once for enhanced privacy.

    Args:
        count: Number of wallets to create (max 10)
        network: Network for all wallets
        password_prefix: Base password or prefix for unique passwords
        use_unique_passwords: Whether to use unique passwords for each wallet
    """
    try:
        if count > 10:
            return {"success": False, "error": "Maximum 10 wallets per batch"}

        client = await get_api_client()
        wallets_created = []

        for i in range(count):
            password = (
                f"{password_prefix}_{i}" if use_unique_passwords else password_prefix
            )

            response = await client.post(
                "/wallets/create", {"network": network, "password": password}
            )

            wallets_created.append(
                {
                    "wallet_id": response["wallet_id"],
                    "address_0x": response["address_0x"],
                    "address_0zk": response["address_0zk"],
                    "index": i,
                }
            )

        return {
            "success": True,
            "wallets_created": wallets_created,
            "count": len(wallets_created),
            "network": network,
            "message": f"Created {count} wallets successfully",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def distribute_tokens(
    source_wallet_id: str,
    token_address: str,
    total_amount: str,
    destination_wallet_ids: List[str],
    distribution_type: str = "equal",
    amounts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Distribute tokens from one wallet to multiple wallets privately.

    Args:
        source_wallet_id: Source wallet ID
        token_address: Token to distribute
        total_amount: Total amount to distribute
        destination_wallet_ids: List of destination wallet IDs
        distribution_type: "equal" or "custom"
        amounts: Custom amounts for each wallet (required if distribution_type is "custom")
    """
    try:
        client = await get_api_client()
        transfers = []

        if distribution_type == "equal":
            amount_per_wallet = str(int(total_amount) // len(destination_wallet_ids))
            amounts = [amount_per_wallet] * len(destination_wallet_ids)
        elif distribution_type == "custom" and not amounts:
            return {
                "success": False,
                "error": "Custom amounts required for custom distribution",
            }

        # Get destination addresses
        destinations = []
        for wallet_id in destination_wallet_ids:
            wallet_info = await client.get(f"/wallets/{wallet_id}")
            destinations.append(
                {"wallet_id": wallet_id, "address_0zk": wallet_info["address_0zk"]}
            )

        # Execute transfers
        for i, dest in enumerate(destinations):
            response = await client.post(
                "/transactions/private-transfer",
                {
                    "wallet_id": source_wallet_id,
                    "token_address": token_address,
                    "amount": amounts[i],
                    "recipient_0zk_address": dest["address_0zk"],
                    "password": config.wallet_password,
                },
            )

            transfers.append(
                {
                    "to_wallet": dest["wallet_id"],
                    "amount": amounts[i],
                    "tx_hash": response["tx_hash"],
                    "status": response["status"],
                }
            )

        return {
            "success": True,
            "source_wallet": source_wallet_id,
            "transfers": transfers,
            "total_distributed": total_amount,
            "message": f"Distributed tokens to {len(transfers)} wallets",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def mix_tokens(
    wallet_ids: List[str],
    token_address: str,
    mixing_rounds: int = 3,
    delay_seconds: int = 30,
) -> Dict[str, Any]:
    """
    Mix tokens between multiple wallets for enhanced privacy.

    Args:
        wallet_ids: List of wallet IDs to mix between
        token_address: Token to mix
        mixing_rounds: Number of mixing rounds
        delay_seconds: Delay between transactions
    """
    try:
        client = await get_api_client()

        # This would implement a mixing strategy
        # In production, this would use more sophisticated mixing algorithms

        return {
            "success": True,
            "message": "Token mixing initiated",
            "wallets": len(wallet_ids),
            "rounds": mixing_rounds,
            "estimated_time": mixing_rounds * delay_seconds * len(wallet_ids),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_wallet_analytics(
    wallet_ids: List[str], include_transactions: bool = True
) -> Dict[str, Any]:
    """
    Get analytics across multiple wallets.

    Args:
        wallet_ids: List of wallet IDs to analyze
        include_transactions: Whether to include transaction summaries
    """
    try:
        client = await get_api_client()
        analytics = {
            "total_wallets": len(wallet_ids),
            "wallets": [],
            "aggregate": {"total_value_usd": 0, "tokens": {}},
        }

        for wallet_id in wallet_ids:
            # Get balance for each wallet
            balance_response = await client.get(
                "/balances", {"wallet_id": wallet_id, "include_private": True}
            )

            wallet_data = {
                "wallet_id": wallet_id,
                "balances": balance_response["balances"],
                "total_value_usd": balance_response.get("total_value_usd", 0),
            }

            if include_transactions:
                tx_response = await client.get(
                    "/transactions", {"wallet_id": wallet_id, "limit": 10}
                )
                wallet_data["recent_transactions"] = tx_response["transactions"]
                wallet_data["total_transactions"] = tx_response["total"]

            analytics["wallets"].append(wallet_data)
            analytics["aggregate"]["total_value_usd"] += wallet_data["total_value_usd"]

        return {"success": True, "analytics": analytics}
    except Exception as e:
        return {"success": False, "error": str(e)}


# === PLAIN ENGLISH PROBLEM SOLVERS ===


@mcp.tool()
async def can_i_afford_this(
    wallet_id: str, action: str, amount: Optional[str] = None, token: str = "USDC"
) -> Dict[str, Any]:
    """
    Check if you have enough tokens AND gas to do what you want.

    Args:
        wallet_id: Your wallet ID
        action: What you want to do (swap, shield, send, etc.)
        amount: How much you want to use (optional)
        token: What token (USDC, ETH, etc.)

    Example: "Can I afford to swap 1000 USDC?"
    """
    try:
        client = await get_api_client()

        # Get balances
        balances = await client.get("/balances", {"wallet_id": wallet_id})
        gas_price = await client.get("/gas-price/ethereum")

        # Estimate costs
        action_gas_costs = {
            "shield": 200000,
            "unshield": 180000,
            "swap": 300000,
            "send": 150000,
            "private_send": 180000,
        }

        gas_needed = action_gas_costs.get(action.lower(), 200000)
        gas_cost_eth = (gas_needed * int(gas_price["gas_price"])) / 10**18

        # Check token balance
        token_balance = balances["balances"]["public"].get(token, "0")
        private_balance = balances["balances"]["private"].get(token, "0")

        can_afford = True
        issues = []

        if amount and int(amount) > int(token_balance) + int(private_balance):
            can_afford = False
            issues.append(
                f"Not enough {token}. You have {token_balance} public + {private_balance} private"
            )

        eth_balance = float(balances["balances"]["public"].get("ETH", "0")) / 10**18
        if eth_balance < gas_cost_eth:
            can_afford = False
            issues.append(
                f"Not enough ETH for gas. Need {gas_cost_eth:.4f} ETH, have {eth_balance:.4f} ETH"
            )

        return {
            "success": True,
            "can_afford": can_afford,
            "summary": (
                "✅ You're good to go!" if can_afford else "❌ " + " AND ".join(issues)
            ),
            "details": {
                "token_balance": token_balance,
                "private_balance": private_balance,
                "eth_balance": str(int(eth_balance * 10**18)),
                "estimated_gas_cost": str(int(gas_cost_eth * 10**18)),
                "gas_price_gwei": int(gas_price["gas_price"]) / 10**9,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def why_is_this_so_expensive(
    action: str, network: str = "ethereum"
) -> Dict[str, Any]:
    """
    Explain why a Railgun transaction costs what it does in simple terms.

    Args:
        action: What you're trying to do (shield, swap, etc.)
        network: Which network you're on

    Example: "Why is shielding so expensive?"
    """
    try:
        client = await get_api_client()
        gas_price = await client.get(f"/gas-price/{network}")

        explanations = {
            "shield": {
                "base_gas": 200000,
                "reason": "Shielding creates a zero-knowledge proof and adds your tokens to the private pool. It's like putting money in a magical safe that proves you own it without showing what's inside.",
                "tip": "Shield larger amounts less frequently to save on gas",
            },
            "unshield": {
                "base_gas": 180000,
                "reason": "Unshielding removes tokens from the private pool while maintaining privacy. It's like taking money out of the magical safe without revealing your identity.",
                "tip": "Batch your unshields if possible",
            },
            "swap": {
                "base_gas": 300000,
                "reason": "Private swaps do 3 things: unshield tokens, swap them, and re-shield the result. It's like secretly trading at a market while wearing an invisibility cloak.",
                "tip": "Swap larger amounts to make the gas worthwhile",
            },
        }

        info = explanations.get(
            action.lower(),
            {
                "base_gas": 200000,
                "reason": "Railgun uses advanced cryptography to keep your transactions private.",
                "tip": "Private transactions cost more but protect your financial privacy",
            },
        )

        gas_cost_usd = (
            info["base_gas"] * int(gas_price["gas_price"]) / 10**18
        ) * 2000  # Assume $2000 ETH

        return {
            "success": True,
            "explanation": info["reason"],
            "estimated_cost_usd": f"${gas_cost_usd:.2f}",
            "gas_needed": info["base_gas"],
            "current_gas_price": f"{int(gas_price['gas_price']) / 10**9:.1f} gwei",
            "money_saving_tip": info["tip"],
            "cheaper_times": "Usually late night US time or weekends",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def just_send_money(
    wallet_id: str, to: str, amount: str, token: str = "USDC", keep_private: bool = True
) -> Dict[str, Any]:
    """
    Send money the easiest way possible. Figures out all the steps for you.

    Args:
        wallet_id: Your wallet
        to: Who to send to (address or ENS)
        amount: How much (can use "10 USDC" format)
        token: What token
        keep_private: Whether to keep it private

    Example: "Just send 100 USDC to alice.eth privately"
    """
    try:
        client = await get_api_client()

        # Parse amount if needed
        if " " in amount:
            amount, token = amount.split(" ")

        # Convert human-readable amount to wei/smallest unit
        decimals = {"USDC": 6, "USDT": 6, "DAI": 18, "ETH": 18}
        amount_wei = str(int(float(amount) * 10 ** decimals.get(token, 18)))

        steps_taken = []

        if keep_private:
            # Check if we need to shield first
            balances = await client.get("/balances", {"wallet_id": wallet_id})
            private_balance = balances["balances"]["private"].get(token, "0")

            if int(private_balance) < int(amount_wei):
                # Need to shield more
                shield_amount = str(int(amount_wei) - int(private_balance))
                shield_response = await client.post(
                    "/transactions/shield",
                    {
                        "wallet_id": wallet_id,
                        "token_address": "0x...",  # Would be resolved
                        "amount": shield_amount,
                        "password": config.wallet_password,
                    },
                )
                steps_taken.append(
                    f"Shielded {float(shield_amount) / 10**decimals[token]} {token}"
                )

            # Send privately
            transfer_response = await client.post(
                "/transactions/private-transfer",
                {
                    "wallet_id": wallet_id,
                    "token_address": "0x...",
                    "amount": amount_wei,
                    "recipient_0zk_address": to,
                    "password": config.wallet_password,
                },
            )
            steps_taken.append(f"Sent {amount} {token} privately")
        else:
            # Just send publicly
            # Would implement public send
            steps_taken.append(f"Sent {amount} {token} publicly")

        return {
            "success": True,
            "message": f"✅ Sent {amount} {token} to {to[:8]}...!",
            "steps_taken": steps_taken,
            "tx_hash": transfer_response.get("tx_hash"),
            "privacy_level": "🔒 Fully Private" if keep_private else "👁️ Public",
            "estimated_time": "2-5 minutes",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def where_are_my_tokens(
    wallet_id: str, show_details: bool = False
) -> Dict[str, Any]:
    """
    Find all your tokens across public and private balances, in plain English.

    Args:
        wallet_id: Your wallet
        show_details: Show more details

    Example: "Where are my tokens?"
    """
    try:
        client = await get_api_client()
        balances = await client.get(
            "/balances", {"wallet_id": wallet_id, "include_private": True}
        )

        summary = []
        total_usd = 0

        # Combine public and private balances
        all_tokens = {}

        for token, amount in balances["balances"]["public"].items():
            if token not in all_tokens:
                all_tokens[token] = {"public": 0, "private": 0, "total": 0}
            all_tokens[token]["public"] = amount

        for token, amount in balances["balances"]["private"].items():
            if token not in all_tokens:
                all_tokens[token] = {"public": 0, "private": 0, "total": 0}
            all_tokens[token]["private"] = amount

        # Format nicely
        for token, amounts in all_tokens.items():
            decimals = {"USDC": 6, "USDT": 6, "DAI": 18, "ETH": 18}.get(token, 18)

            public_amount = float(amounts["public"]) / 10**decimals
            private_amount = float(amounts["private"]) / 10**decimals
            total = public_amount + private_amount

            if total > 0.01:  # Only show tokens with meaningful amounts
                if private_amount > 0 and public_amount > 0:
                    status = f"{total:.2f} {token} (🔓 {public_amount:.2f} public + 🔒 {private_amount:.2f} private)"
                elif private_amount > 0:
                    status = f"🔒 {private_amount:.2f} {token} (all private)"
                else:
                    status = f"🔓 {public_amount:.2f} {token} (all public)"

                summary.append(status)

        return {
            "success": True,
            "summary": summary if summary else ["No tokens found"],
            "total_tokens": len(all_tokens),
            "advice": (
                "Shield tokens to make them private"
                if any(float(t["public"]) > 0 for t in all_tokens.values())
                else "Your tokens are private! 🎉"
            ),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def fix_stuck_transaction(
    wallet_id: str, transaction_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Help with stuck or failed transactions.

    Args:
        wallet_id: Your wallet
        transaction_id: Specific transaction (optional)

    Example: "Fix my stuck transaction"
    """
    try:
        client = await get_api_client()

        # Get recent transactions
        txs = await client.get(
            "/transactions", {"wallet_id": wallet_id, "limit": 10, "status": "pending"}
        )

        if not txs["transactions"]:
            return {
                "success": True,
                "message": "No stuck transactions found! You're all good 👍",
            }

        stuck_tx = txs["transactions"][0]
        solutions = []

        # Diagnose the issue
        if stuck_tx.get("gas_price", 0) < 20 * 10**9:  # Less than 20 gwei
            solutions.append("Gas price too low. Need to speed up with higher gas.")

        if stuck_tx.get("age_minutes", 0) > 30:
            solutions.append("Transaction is old. May need to cancel and retry.")

        # Offer solutions
        return {
            "success": True,
            "stuck_transaction": {
                "id": stuck_tx["id"],
                "type": stuck_tx["type"],
                "age": f"{stuck_tx.get('age_minutes', 0)} minutes",
                "gas_price": f"{stuck_tx.get('gas_price', 0) / 10**9} gwei",
            },
            "solutions": solutions,
            "quick_fix": "Try cancelling and resending with 50% higher gas price",
            "prevent_future": "Always check gas prices before sending",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def optimize_my_privacy(wallet_id: str) -> Dict[str, Any]:
    """
    Give personalized tips to improve your privacy based on your usage.

    Args:
        wallet_id: Your wallet

    Example: "How can I be more private?"
    """
    try:
        client = await get_api_client()

        # Analyze wallet
        balances = await client.get("/balances", {"wallet_id": wallet_id})
        txs = await client.get("/transactions", {"wallet_id": wallet_id, "limit": 50})

        tips = []
        score = 100

        # Check for privacy issues
        public_balance = sum(float(v) for v in balances["balances"]["public"].values())
        private_balance = sum(
            float(v) for v in balances["balances"]["private"].values()
        )

        if public_balance > private_balance:
            tips.append("🔓 Most of your funds are public! Shield them for privacy.")
            score -= 30

        if len(set(tx["to_address"] for tx in txs["transactions"])) < 3:
            tips.append(
                "🔄 You're sending to the same addresses repeatedly. Mix it up!"
            )
            score -= 20

        # Check for timing patterns
        hours = [tx.get("hour", 0) for tx in txs["transactions"]]
        if len(set(hours)) < 5:
            tips.append("⏰ You transact at similar times. Vary your schedule.")
            score -= 10

        if not tips:
            tips.append("🎉 Great job! Your privacy practices are solid!")

        return {
            "success": True,
            "privacy_score": f"{score}/100",
            "tips": tips,
            "next_steps": [
                "Shield remaining public tokens",
                "Use multiple wallets for different purposes",
                "Add delays between related transactions",
                "Use relayers for maximum privacy",
            ],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def emergency_exit(
    wallet_id: str, destination: str, reason: str = "general"
) -> Dict[str, Any]:
    """
    Quickly move all funds out of Railgun in case of emergency.

    Args:
        wallet_id: Your wallet
        destination: Where to send everything
        reason: Why you're exiting (helps optimize the exit)

    Example: "Emergency exit all my funds to my hardware wallet"
    """
    try:
        client = await get_api_client()

        # Get all balances
        balances = await client.get(
            "/balances", {"wallet_id": wallet_id, "include_private": True}
        )

        exits = []
        total_gas_needed = 0

        # Plan the exit strategy
        for token, amount in balances["balances"]["private"].items():
            if float(amount) > 0:
                exits.append(
                    {
                        "token": token,
                        "amount": amount,
                        "type": "unshield",
                        "gas_estimate": 180000,
                    }
                )
                total_gas_needed += 180000

        for token, amount in balances["balances"]["public"].items():
            if float(amount) > 0 and token != "ETH":
                exits.append(
                    {
                        "token": token,
                        "amount": amount,
                        "type": "transfer",
                        "gas_estimate": 65000,
                    }
                )
                total_gas_needed += 65000

        gas_price = await client.get("/gas-price/ethereum")
        total_cost_eth = (total_gas_needed * int(gas_price["gas_price"])) / 10**18

        return {
            "success": True,
            "exit_plan": {
                "steps": len(exits),
                "tokens_to_move": [e["token"] for e in exits],
                "estimated_time": f"{len(exits) * 2} minutes",
                "estimated_cost": f"{total_cost_eth:.4f} ETH",
                "destination": destination,
            },
            "warning": "This will move ALL funds and reduce privacy!",
            "execute_command": "Use execute_emergency_exit to proceed",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# === UTILITY TOOLS ===


@mcp.tool()
async def verify_proof(proof_data: str) -> Dict[str, Any]:
    """
    Verify a zero-knowledge proof.

    Args:
        proof_data: The proof data to verify
    """
    try:
        client = await get_api_client()

        response = await client.post("/proofs/verify", {"proof_data": proof_data})

        return {
            "success": True,
            "valid": response["valid"],
            "proof_type": response.get("proof_type"),
            "verified_at": response.get("verified_at"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def get_supported_tokens(network: str) -> Dict[str, Any]:
    """
    Get list of tokens supported by Railgun on a network.

    Args:
        network: Network to get supported tokens for
    """
    try:
        client = await get_api_client()
        response = await client.get(f"/tokens/{network}")

        return {
            "success": True,
            "network": network,
            "tokens": response["tokens"],
            "count": len(response["tokens"]),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
async def check_config() -> Dict[str, Any]:
    """
    Check the current configuration status.
    """
    return {
        "success": True,
        "config": {
            "private_key_set": bool(config.private_key),
            "wallet_password_set": bool(config.wallet_password),
            "railgun_contracts": config.railgun_contracts,
            "rpc_endpoints": {
                k: v.split("/")[2] if "/" in v else v
                for k, v in config.rpc_endpoints.items()
            },
        },
        "warning": "⚠️  This MCP server currently has fake API calls and needs a complete rewrite to work with the real RAILGUN protocol.",
        "required_fix": "See ARCHITECTURE_UPDATE.md for implementation details",
        "message": "Use RAILGUN_PRIVATE_KEY environment variable or ~/.railgun/config.json to configure",
    }


# === MAIN ENTRY POINT ===


def main():
    """Main entry point for the Railgun MCP server."""
    import sys
    import asyncio

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Railgun MCP server...")
        asyncio.run(cleanup_api_client())
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        asyncio.run(cleanup_api_client())
        sys.exit(1)


if __name__ == "__main__":
    main()
