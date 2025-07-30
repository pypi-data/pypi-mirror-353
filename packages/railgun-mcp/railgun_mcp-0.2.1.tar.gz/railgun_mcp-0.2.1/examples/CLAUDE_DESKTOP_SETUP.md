# 🚀 Claude Desktop Setup for RAILGUN MCP

## **Installation Steps**

### **1. Install the Package**
```bash
pip install railgun-mcp
```

### **2. Get Your Keys**
You'll need:
- **Private Key**: Your Ethereum wallet private key (starts with `0x`)
- **RPC URLs**: From providers like Alchemy or Infura
  - Get free API key at: https://www.alchemy.com/
  - Or use public endpoints (may be slower)

### **3. Configure Claude Desktop**

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

**Copy this template** and replace the placeholder values:

```json
{
  "mcpServers": {
    "railgun-mcp": {
      "command": "python",
      "args": ["-m", "railgun_mcp"],
      "env": {
        "RAILGUN_PRIVATE_KEY": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "RAILGUN_WALLET_PASSWORD": "your-secure-wallet-password",
        "ETHEREUM_RPC_URL": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY",
        "POLYGON_RPC_URL": "https://polygon-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY",
        "ARBITRUM_RPC_URL": "https://arb-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY",
        "BSC_RPC_URL": "https://bsc-dataseed.binance.org/"
      }
    }
  }
}
```

### **4. Replace Placeholder Values** ⚠️

**IMPORTANT**: Replace these values with your actual credentials:

- `RAILGUN_PRIVATE_KEY`: Your wallet's private key
- `RAILGUN_WALLET_PASSWORD`: A secure password for wallet encryption
- `YOUR_ALCHEMY_API_KEY`: Your Alchemy API key (or use other RPC providers)

### **5. Restart Claude Desktop**

Completely quit and restart Claude Desktop for changes to take effect.

### **6. Test the Connection**

Ask Claude:
> *"What RAILGUN tools do you have available?"*

> *"Run check_config to show my RAILGUN configuration"*

## **Security Notes** 🔒

- **Private keys are stored in plain text** in the Claude config
- **Only you have access** to Claude's config directory
- **Consider using a dedicated test wallet** instead of your main wallet
- **Keep your config file secure** and never share it

## **Available Tools** 🛠️

Once configured, you'll have access to:

- **Wallet Management**: Create wallets, check balances
- **Privacy Operations**: Shield/unshield tokens, private transfers
- **Multi-Wallet Tools**: Batch operations, token distribution
- **AI-Powered Tools**: Affordability checker, cost explainer
- **Privacy Analytics**: Transaction mixing, privacy optimization

## **Troubleshooting** 🔧

### **Server Won't Start**
- Check that `railgun-mcp` is installed: `pip show railgun-mcp`
- Verify Python is accessible: `python -m railgun_mcp --help`

### **No Tools Available**
- Restart Claude Desktop completely
- Check config file syntax with a JSON validator
- Verify file location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### **Configuration Issues**
- Run `python -c "from railgun_mcp.models import Config; print(Config())"`
- Check environment variables are set correctly

## **Need Help?** 💬

- **GitHub**: https://github.com/samthedataman/mcp_rail_gun
- **PyPI**: https://pypi.org/project/railgun-mcp/
- **Issues**: https://github.com/samthedataman/mcp_rail_gun/issues 