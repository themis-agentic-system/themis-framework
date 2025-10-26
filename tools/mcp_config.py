"""MCP (Model Context Protocol) configuration management for Themis.

This module handles loading and managing MCP server configurations,
allowing Themis agents to connect to external tools and data sources.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("themis.mcp_config")


class MCPConfig:
    """Manager for MCP server configurations."""

    def __init__(self, config_path: str | Path | None = None):
        """Initialize MCP configuration manager.

        Args:
            config_path: Path to .mcp.json file. If None, looks for .mcp.json
                in current directory, parent directories, or home directory.
        """
        self.config_path = self._find_config_file(config_path)
        self.servers: dict[str, dict[str, Any]] = {}
        self._load_config()

    def _find_config_file(self, config_path: str | Path | None) -> Path | None:
        """Find MCP configuration file in standard locations."""
        if config_path:
            path = Path(config_path)
            if path.exists():
                return path
            logger.warning(f"Specified MCP config not found: {config_path}")
            return None

        # Check current directory
        cwd_config = Path.cwd() / ".mcp.json"
        if cwd_config.exists():
            return cwd_config

        # Check parent directories
        current = Path.cwd()
        for parent in current.parents:
            parent_config = parent / ".mcp.json"
            if parent_config.exists():
                return parent_config

        # Check home directory
        home_config = Path.home() / ".mcp.json"
        if home_config.exists():
            return home_config

        logger.info("No .mcp.json configuration file found")
        return None

    def _load_config(self) -> None:
        """Load MCP server configurations from file."""
        if not self.config_path:
            logger.info("No MCP configuration file, MCP integration disabled")
            return

        try:
            with open(self.config_path) as f:
                config = json.load(f)

            servers = config.get("servers", {})
            for name, server_config in servers.items():
                # Expand environment variables in configuration
                expanded_config = self._expand_env_vars(server_config)

                # Only load enabled servers with valid URLs
                if expanded_config.get("enabled") and expanded_config.get("url"):
                    self.servers[name] = expanded_config
                    logger.info(
                        f"Loaded MCP server: {name} ({expanded_config.get('description', 'No description')})"
                    )

            if self.servers:
                logger.info(f"Loaded {len(self.servers)} enabled MCP server(s)")
            else:
                logger.info("No enabled MCP servers found in configuration")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MCP config file: {e}")
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")

    def _expand_env_vars(self, config: dict[str, Any]) -> dict[str, Any]:
        """Expand environment variables in server configuration.

        Supports ${VAR_NAME} syntax in string values.
        """
        expanded = {}
        for key, value in config.items():
            if isinstance(value, str):
                # Replace ${VAR_NAME} with environment variable value
                import re

                def replace_env(match: re.Match) -> str:
                    var_name = match.group(1)
                    return os.getenv(var_name, f"${{{var_name}}}")

                expanded[key] = re.sub(r"\$\{([^}]+)\}", replace_env, value)
            else:
                expanded[key] = value
        return expanded

    def get_enabled_servers(self) -> list[dict[str, str]]:
        """Get list of enabled MCP servers for API requests.

        Returns:
            List of dicts with 'url' and optional 'api_key' for each enabled server.
        """
        mcp_servers = []
        for name, config in self.servers.items():
            server = {"url": config["url"]}
            if config.get("api_key"):
                server["api_key"] = config["api_key"]
            mcp_servers.append(server)
        return mcp_servers

    def get_server(self, name: str) -> dict[str, Any] | None:
        """Get configuration for a specific MCP server.

        Args:
            name: Server name as defined in .mcp.json

        Returns:
            Server configuration dict or None if not found/disabled.
        """
        return self.servers.get(name)

    def is_enabled(self, name: str) -> bool:
        """Check if an MCP server is enabled.

        Args:
            name: Server name

        Returns:
            True if server is enabled and configured, False otherwise.
        """
        return name in self.servers

    def list_servers(self) -> list[str]:
        """List all enabled MCP server names.

        Returns:
            List of server names.
        """
        return list(self.servers.keys())


# Global singleton for easy access
_mcp_config: MCPConfig | None = None


def get_mcp_config() -> MCPConfig:
    """Get or create the global MCP configuration instance."""
    global _mcp_config
    if _mcp_config is None:
        _mcp_config = MCPConfig()
    return _mcp_config


def set_mcp_config(config: MCPConfig) -> None:
    """Set the global MCP configuration instance (useful for testing)."""
    global _mcp_config
    _mcp_config = config
