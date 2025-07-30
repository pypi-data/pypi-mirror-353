#!/usr/bin/env python3
"""
Tests for Railgun MCP configuration module.
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from railgun_mcp.models import Config


def test_config_defaults():
    """Test configuration defaults."""
    with patch.dict(os.environ, {}, clear=True):
        config = Config()

        assert config.api_key is None
        assert config.wallet_password is None
        assert config.railgun_api_url == "https://api.railgun.org/v1"
        assert "ethereum" in config.rpc_endpoints
        assert "arbitrum" in config.rpc_endpoints
        assert "polygon" in config.rpc_endpoints
        assert "bsc" in config.rpc_endpoints


def test_config_from_env():
    """Test configuration from environment variables."""
    env_vars = {
        "RAILGUN_API_KEY": "test-api-key",
        "RAILGUN_WALLET_PASSWORD": "test-password",
        "RAILGUN_API_URL": "https://test-api.railgun.org/v1",
        "ETHEREUM_RPC_URL": "https://test-eth-rpc.com",
    }

    with patch.dict(os.environ, env_vars, clear=True):
        config = Config()

        assert config.api_key == "test-api-key"
        assert config.wallet_password == "test-password"
        assert config.railgun_api_url == "https://test-api.railgun.org/v1"
        assert config.rpc_endpoints["ethereum"] == "https://test-eth-rpc.com"


def test_config_from_file():
    """Test configuration from JSON file."""
    config_data = {
        "api_key": "file-api-key",
        "wallet_password": "file-password",
        "railgun_api_url": "https://file-api.railgun.org/v1",
        "rpc_endpoints": {"ethereum": "https://file-eth-rpc.com"},
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / ".railgun"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        with patch("pathlib.Path.home", return_value=Path(temp_dir)):
            with patch.dict(os.environ, {}, clear=True):
                config = Config()

                assert config.api_key == "file-api-key"
                assert config.wallet_password == "file-password"
                assert config.railgun_api_url == "https://file-api.railgun.org/v1"
                assert config.rpc_endpoints["ethereum"] == "https://file-eth-rpc.com"


def test_env_overrides_file():
    """Test that environment variables override file configuration."""
    config_data = {
        "api_key": "file-api-key",
        "wallet_password": "file-password",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / ".railgun"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        env_vars = {
            "RAILGUN_API_KEY": "env-api-key",
        }

        with patch("pathlib.Path.home", return_value=Path(temp_dir)):
            with patch.dict(os.environ, env_vars, clear=True):
                config = Config()

                # Environment should override file
                assert config.api_key == "env-api-key"
                # File value should be used when env var not set
                assert config.wallet_password == "file-password"


if __name__ == "__main__":
    pytest.main([__file__])
