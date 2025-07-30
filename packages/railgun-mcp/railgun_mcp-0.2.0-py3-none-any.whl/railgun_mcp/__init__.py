"""
Railgun MCP Server - Model Context Protocol server for Railgun privacy protocol.

This package provides a comprehensive MCP server for interacting with the Railgun
privacy protocol, enabling private DeFi transactions across multiple networks.
"""

__version__ = "0.2.0"
__author__ = "Sam Savage"
__license__ = "MIT"

from .models import Config, Token, TokenAmount, Step, Recipe

# Conditionally import server module (requires fastmcp)
try:
    from .server import main

    __all__ = [
        "main",
        "Config",
        "Token",
        "TokenAmount",
        "Step",
        "Recipe",
    ]
except ImportError:
    # fastmcp not available, only expose models
    __all__ = [
        "Config",
        "Token",
        "TokenAmount",
        "Step",
        "Recipe",
    ]
