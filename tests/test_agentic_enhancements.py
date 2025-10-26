"""Tests for agentic enhancements (2025 features).

Tests cover:
- Extended thinking mode
- Prompt caching
- Code execution tool
- Files API
- MCP configuration

Note: Some features are in beta/upcoming. Tests mock API calls to avoid
dependency on API availability.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.llm_client import LLMClient
from tools.mcp_config import MCPConfig


class TestExtendedThinking:
    """Test extended thinking mode functionality."""

    def test_extended_thinking_enabled_by_default(self):
        """Verify extended thinking is enabled by default."""
        client = LLMClient(api_key="test-key")
        assert client.use_extended_thinking is True

    def test_extended_thinking_can_be_disabled(self):
        """Verify extended thinking can be disabled."""
        client = LLMClient(api_key="test-key", use_extended_thinking=False)
        assert client.use_extended_thinking is False

    @pytest.mark.asyncio
    @patch("tools.llm_client.Anthropic")
    async def test_extended_thinking_adds_headers(self, mock_anthropic):
        """Verify extended thinking adds correct API headers."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key", use_extended_thinking=True)
        await client._call_anthropic_api("system", [{"role": "user", "content": "test"}], 1000)

        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["extended_thinking"] is True
        assert "anthropic-beta" in call_args.kwargs.get("extra_headers", {})

    @pytest.mark.asyncio
    @patch("tools.llm_client.Anthropic")
    async def test_thinking_blocks_logged(self, mock_anthropic):
        """Verify thinking blocks are logged but not returned."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(type="thinking", thinking="internal reasoning here"),
            MagicMock(type="text", text="final response"),
        ]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key", use_extended_thinking=True)
        result = await client._call_anthropic_api("system", [{"role": "user", "content": "test"}], 1000)

        assert "final response" in result
        assert "internal reasoning" not in result


class TestPromptCaching:
    """Test 1-hour prompt caching functionality."""

    def test_prompt_caching_enabled_by_default(self):
        """Verify prompt caching is enabled by default."""
        client = LLMClient(api_key="test-key")
        assert client.use_prompt_caching is True

    def test_prompt_caching_can_be_disabled(self):
        """Verify prompt caching can be disabled."""
        client = LLMClient(api_key="test-key", use_prompt_caching=False)
        assert client.use_prompt_caching is False

    @pytest.mark.asyncio
    @patch("tools.llm_client.Anthropic")
    async def test_cache_control_headers_added(self, mock_anthropic):
        """Verify cache control headers are added when caching enabled."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key", use_prompt_caching=True)
        await client._call_anthropic_api("system prompt", [{"role": "user", "content": "test"}], 1000)

        call_args = mock_client.messages.create.call_args
        assert "extra_headers" in call_args.kwargs
        assert "anthropic-cache-control" in call_args.kwargs["extra_headers"]
        assert call_args.kwargs["extra_headers"]["anthropic-cache-control"] == "ephemeral+extended"

    @pytest.mark.asyncio
    @patch("tools.llm_client.Anthropic")
    async def test_system_prompt_has_cache_control(self, mock_anthropic):
        """Verify system prompt includes cache_control when caching enabled."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key", use_prompt_caching=True)
        await client._call_anthropic_api("system prompt", [{"role": "user", "content": "test"}], 1000)

        call_args = mock_client.messages.create.call_args
        system = call_args.kwargs["system"]
        assert isinstance(system, list)
        assert system[0]["type"] == "text"
        assert system[0]["text"] == "system prompt"
        assert "cache_control" in system[0]
        assert system[0]["cache_control"]["type"] == "ephemeral"


class TestCodeExecution:
    """Test code execution tool functionality."""

    def test_code_execution_disabled_by_default(self):
        """Verify code execution is disabled by default."""
        client = LLMClient(api_key="test-key")
        assert client.enable_code_execution is False

    def test_code_execution_can_be_enabled(self):
        """Verify code execution can be enabled."""
        client = LLMClient(api_key="test-key", enable_code_execution=True)
        assert client.enable_code_execution is True

    @pytest.mark.asyncio
    @patch("tools.llm_client.Anthropic")
    async def test_code_execution_tool_registered(self, mock_anthropic):
        """Verify code execution tool is registered when enabled."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key", enable_code_execution=True)
        await client._call_anthropic_api("system", [{"role": "user", "content": "test"}], 1000)

        call_args = mock_client.messages.create.call_args
        tools = call_args.kwargs.get("tools", [])
        assert len(tools) == 1
        assert tools[0]["type"] == "code_execution_2025_04_01"
        assert tools[0]["name"] == "python"


class TestFilesAPI:
    """Test Files API functionality."""

    @patch("tools.llm_client.Anthropic")
    def test_upload_file_success(self, mock_anthropic):
        """Test successful file upload."""
        mock_client = MagicMock()
        mock_file = MagicMock()
        mock_file.id = "file_abc123"
        mock_client.files.create.return_value = mock_file
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key")

        # Create temporary test file
        test_file = Path("/tmp/test_doc.txt")
        test_file.write_text("test content")

        try:
            file_id = client.upload_file(str(test_file))
            assert file_id == "file_abc123"
            assert mock_client.files.create.called
        finally:
            test_file.unlink(missing_ok=True)

    def test_upload_file_without_api_key_raises(self):
        """Test file upload fails in stub mode."""
        client = LLMClient(api_key=None)  # Stub mode

        with pytest.raises(ValueError, match="File upload requires ANTHROPIC_API_KEY"):
            client.upload_file("/tmp/test.txt")

    @patch("tools.llm_client.Anthropic")
    def test_list_files(self, mock_anthropic):
        """Test listing uploaded files."""
        mock_client = MagicMock()
        mock_file1 = MagicMock(id="file_1", filename="doc1.pdf", created_at="2025-01-01")
        mock_file2 = MagicMock(id="file_2", filename="doc2.pdf", created_at="2025-01-02")
        mock_response = MagicMock(data=[mock_file1, mock_file2])
        mock_client.files.list.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key")
        files = client.list_files()

        assert len(files) == 2
        assert files[0]["id"] == "file_1"
        assert files[0]["filename"] == "doc1.pdf"
        assert files[1]["id"] == "file_2"

    @patch("tools.llm_client.Anthropic")
    def test_delete_file(self, mock_anthropic):
        """Test deleting a file."""
        mock_client = MagicMock()
        mock_client.files.delete = MagicMock()
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key")
        client.delete_file("file_abc123")

        mock_client.files.delete.assert_called_once_with("file_abc123")

    @pytest.mark.asyncio
    @patch("tools.llm_client.Anthropic")
    async def test_generate_with_file_ids(self, mock_anthropic):
        """Test generating text with file references."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="analysis complete")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = LLMClient(api_key="test-key")
        result = await client.generate_text(
            system_prompt="system",
            user_prompt="analyze",
            file_ids=["file_abc123", "file_def456"],
        )

        assert "analysis complete" in result
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        content = messages[0]["content"]

        # Should have 2 file references + 1 text
        assert len(content) == 3
        assert content[0]["type"] == "file"
        assert content[0]["file"]["file_id"] == "file_abc123"
        assert content[1]["type"] == "file"
        assert content[1]["file"]["file_id"] == "file_def456"
        assert content[2]["type"] == "text"


class TestMCPConfig:
    """Test MCP configuration management."""

    def test_mcp_config_loads_from_file(self, tmp_path):
        """Test loading MCP configuration from file."""
        config_file = tmp_path / ".mcp.json"
        config_data = {
            "servers": {
                "test-server": {
                    "url": "https://example.com/mcp",
                    "api_key": "test-key",
                    "enabled": True,
                    "description": "Test server",
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = MCPConfig(config_path=str(config_file))

        assert "test-server" in config.servers
        assert config.servers["test-server"]["url"] == "https://example.com/mcp"
        assert config.is_enabled("test-server")

    def test_mcp_config_expands_env_vars(self, tmp_path):
        """Test environment variable expansion in MCP config."""
        config_file = tmp_path / ".mcp.json"
        config_data = {
            "servers": {
                "test-server": {
                    "url": "${TEST_MCP_URL}",
                    "api_key": "${TEST_MCP_KEY}",
                    "enabled": True,
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        os.environ["TEST_MCP_URL"] = "https://expanded.com/mcp"
        os.environ["TEST_MCP_KEY"] = "expanded-key"

        try:
            config = MCPConfig(config_path=str(config_file))

            assert config.servers["test-server"]["url"] == "https://expanded.com/mcp"
            assert config.servers["test-server"]["api_key"] == "expanded-key"
        finally:
            os.environ.pop("TEST_MCP_URL", None)
            os.environ.pop("TEST_MCP_KEY", None)

    def test_mcp_config_ignores_disabled_servers(self, tmp_path):
        """Test that disabled servers are not loaded."""
        config_file = tmp_path / ".mcp.json"
        config_data = {
            "servers": {
                "enabled-server": {"url": "https://enabled.com", "enabled": True},
                "disabled-server": {"url": "https://disabled.com", "enabled": False},
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = MCPConfig(config_path=str(config_file))

        assert "enabled-server" in config.servers
        assert "disabled-server" not in config.servers

    def test_mcp_config_get_enabled_servers(self, tmp_path):
        """Test getting list of enabled MCP servers for API."""
        config_file = tmp_path / ".mcp.json"
        config_data = {
            "servers": {
                "server1": {"url": "https://s1.com", "api_key": "key1", "enabled": True},
                "server2": {"url": "https://s2.com", "enabled": True},
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = MCPConfig(config_path=str(config_file))
        servers = config.get_enabled_servers()

        assert len(servers) == 2
        assert servers[0]["url"] == "https://s1.com"
        assert servers[0]["api_key"] == "key1"
        assert servers[1]["url"] == "https://s2.com"
        assert "api_key" not in servers[1]


class TestLDAEnhancedTools:
    """Test LDA agent enhancements with code execution."""

    @pytest.mark.asyncio
    @patch("tools.llm_client.get_llm_client")
    async def test_damages_calculator(self, mock_get_client):
        """Test damages calculator tool."""
        from agents.lda import _damages_calculator

        # Mock LLM client response
        mock_client = MagicMock()
        mock_client.generate_structured.return_value = {
            "economic_total": 165000.0,
            "non_economic_estimate": 50000.0,
            "punitive_total": 0.0,
            "grand_total": 215000.0,
            "confidence_level": "high",
            "settlement_range": {"min": 129000.0, "max": 172000.0},
            "breakdown": {"medical": 45000, "lost_wages": 120000},
        }
        mock_get_client.return_value = mock_client

        damages_data = {
            "economic_losses": {"medical": 45000, "lost_wages": 120000},
            "non_economic_factors": {"pain_suffering_severity": "moderate"},
            "punitive_factors": {},
        }

        result = await _damages_calculator(damages_data)

        assert "economic_total" in result
        assert "settlement_range" in result
        assert result["economic_total"] >= 0

    @pytest.mark.asyncio
    @patch("tools.llm_client.get_llm_client")
    async def test_timeline_analyzer(self, mock_get_client):
        """Test timeline analyzer tool."""
        from agents.lda import _timeline_analyzer

        # Mock LLM client response
        mock_client = MagicMock()
        mock_client.generate_structured.return_value = {
            "duration_days": 31,
            "total_events": 3,
            "gaps": [{"start_date": "2024-01-15", "end_date": "2024-02-01", "days": 17}],
            "clusters": [],
            "critical_periods": ["2024-01-01 - Incident date"],
            "average_gap_days": 15.5,
            "recommendations": ["Obtain additional medical records for treatment gaps"],
        }
        mock_get_client.return_value = mock_client

        timeline_data = {
            "timeline": [
                {"date": "2024-01-01", "description": "Incident occurred"},
                {"date": "2024-01-15", "description": "First medical visit"},
                {"date": "2024-02-01", "description": "Follow-up treatment"},
            ]
        }

        result = await _timeline_analyzer(timeline_data)

        assert "duration_days" in result
        assert "total_events" in result
        assert result["total_events"] == 3
        assert result["duration_days"] >= 0

    @pytest.mark.asyncio
    async def test_lda_agent_with_code_execution_enabled(self):
        """Test LDA agent with code execution enabled."""
        from agents.lda import LDAAgent

        agent = LDAAgent(enable_code_execution=True)

        assert agent.enable_code_execution is True
        assert "damages_calculator" in agent.tools
        assert "timeline_analyzer" in agent.tools


@pytest.mark.asyncio
async def test_generate_with_mcp_stub_mode():
    """Test MCP generation falls back in stub mode."""
    client = LLMClient(api_key=None)  # Stub mode
    mcp_servers = [{"url": "https://example.com/mcp"}]

    # Should fallback to regular generation
    result = await client.generate_with_mcp(
        system_prompt="system",
        user_prompt="test",
        mcp_servers=mcp_servers,
    )

    assert isinstance(result, str)


def test_llm_client_initialization_with_all_features():
    """Test LLM client can be initialized with all features."""
    client = LLMClient(
        api_key="test-key",
        model="claude-sonnet-4-5",
        use_extended_thinking=True,
        use_prompt_caching=True,
        enable_code_execution=True,
    )

    assert client.model == "claude-sonnet-4-5"
    assert client.use_extended_thinking is True
    assert client.use_prompt_caching is True
    assert client.enable_code_execution is True
    assert client._stub_mode is False


def test_llm_client_stub_mode_detected():
    """Test LLM client detects stub mode when no API key."""
    client = LLMClient(api_key=None)

    assert client._stub_mode is True
    assert client.client is None
