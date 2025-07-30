"""Integration tests for core MCP functionality.

These tests verify the core MCP server functionality, tool registration,
and protocol interactions without focusing on specific transport types.
"""

import logging
import subprocess
import sys
from asyncio.exceptions import CancelledError
from unittest.mock import Mock, patch

import httpx
import pytest
from mcp import McpError

from fabric_mcp import __version__
from fabric_mcp.core import FabricMCP
from tests.shared.fabric_api.utils import (
    MockFabricAPIServer,
    fabric_api_server_fixture,
)
from tests.shared.mocking_utils import (
    COMMON_PATTERN_DETAILS,
    COMMON_PATTERN_LIST,
    create_fabric_api_mock,
)

_ = fabric_api_server_fixture  # to get rid of unused variable warning


@pytest.mark.integration
class TestFabricMCPCore:
    """Integration tests for core Fabric MCP Server functionality."""

    @pytest.fixture
    def server(self):
        """Create a FabricMCP server instance for testing."""
        return FabricMCP(log_level="DEBUG")

    @pytest.fixture
    def mock_fabric_api_response(self):
        """Mock responses from the Fabric REST API."""
        return {
            "patterns": ["analyze_claims", "summarize", "create_story"],
            "pattern_details": {
                "name": "analyze_claims",
                "content": "System prompt for analyzing claims...",
                "metadata": {"author": "daniel", "version": "1.0"},
            },
            "pattern_execution": {
                "result": "This claim appears to be factual based on...",
                "model_used": "gpt-4",
                "tokens": 150,
            },
        }

    def test_server_initialization_and_configuration(self, server: FabricMCP):
        """Test server initialization and configuration."""
        assert server.log_level == "DEBUG"
        assert server.mcp.name.startswith("Fabric MCP v")
        assert hasattr(server, "logger")
        assert hasattr(server, "mcp")
        assert server.mcp is not None

    def test_tool_registration_and_discovery(self, server: FabricMCP):
        """Test that MCP tools are properly registered and discoverable."""
        # Check that tools are registered
        tools = getattr(server, "_FabricMCP__tools", [])
        assert len(tools) == 6

        # Verify each tool is callable
        for tool in tools:
            assert callable(tool)

        # Test specific tool functionality with mocking
        list_patterns_tool = tools[0]
        with patch("fabric_mcp.core.FabricApiClient") as mock_api_client_class:
            create_fabric_api_mock(mock_api_client_class).with_successful_response(
                COMMON_PATTERN_LIST
            ).build()

            result: list[str] = list_patterns_tool()
            assert isinstance(result, list)
            assert len(result) == 3

        pattern_details_tool = tools[1]
        # Mock the FabricApiClient for pattern details test
        with patch("fabric_mcp.core.FabricApiClient") as mock_api_client_class:
            create_fabric_api_mock(mock_api_client_class).with_successful_response(
                COMMON_PATTERN_DETAILS
            ).build()

            result = pattern_details_tool("test_pattern")
            assert isinstance(result, dict)
            assert "name" in result

    @pytest.mark.asyncio
    async def test_fabric_list_patterns_with_mocked_api(
        self, server: FabricMCP, mock_fabric_api_response: Mock
    ):
        """Test the fabric_list_patterns tool with mocked API calls."""
        with patch("fabric_mcp.core.FabricApiClient") as mock_api_client_class:
            # Setup mock API client
            mock_api_client = Mock()
            mock_api_client_class.return_value = mock_api_client

            # Setup mock response
            mock_response = Mock()
            mock_response.json.return_value = mock_fabric_api_response["patterns"]
            mock_api_client.get.return_value = mock_response

            # Execute the tool
            tools = getattr(server, "_FabricMCP__tools", [])
            list_patterns_tool = tools[0]
            result: list[str] = list_patterns_tool()

            assert isinstance(result, list)
            assert len(result) > 0
            assert result == mock_fabric_api_response["patterns"]

            # Verify API client was called correctly
            mock_api_client.get.assert_called_once_with("/patterns/names")
            mock_api_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_fabric_pattern_details_with_mocked_api(self, server: FabricMCP):
        """Test the fabric_get_pattern_details tool with mocked API calls."""
        with patch("fabric_mcp.core.FabricApiClient") as mock_api_client_class:
            # Setup mock API client
            mock_api_client = Mock()
            mock_api_client_class.return_value = mock_api_client

            # Setup mock response with actual Fabric API format
            mock_response = Mock()
            mock_response.json.return_value = {
                "Name": "analyze_claims",
                "Description": "Analyze truth claims",
                "Pattern": "# IDENTITY\nYou are an expert fact checker...",
            }
            mock_api_client.get.return_value = mock_response

            # Execute the tool
            tools = getattr(server, "_FabricMCP__tools", [])
            pattern_details_tool = tools[1]
            result = pattern_details_tool("analyze_claims")

            # Verify response structure
            assert isinstance(result, dict)
            assert result["name"] == "analyze_claims"
            assert result["description"] == "Analyze truth claims"
            assert (
                result["system_prompt"]
                == "# IDENTITY\nYou are an expert fact checker..."
            )

            # Verify API client was called correctly
            mock_api_client.get.assert_called_once_with("/patterns/analyze_claims")
            mock_api_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_fabric_run_pattern_with_mocked_api(
        self, server: FabricMCP, mock_fabric_api_response: Mock
    ):
        """Test the fabric_run_pattern tool with mocked API calls."""
        with patch("httpx.Client") as mock_client:
            # Setup mock response
            mock_response = Mock()
            mock_response.json.return_value = mock_fabric_api_response[
                "pattern_execution"
            ]
            mock_response.status_code = 200
            mock_client.return_value.post.return_value = mock_response

            # Execute the tool (currently returns hardcoded values)
            tools = getattr(server, "_FabricMCP__tools", [])
            run_pattern_tool = tools[2]
            result = run_pattern_tool("analyze_claims", "Test input text")

            assert isinstance(result, dict)
            assert "output_format" in result
            assert "output_text" in result

    @pytest.mark.asyncio
    async def test_error_handling_with_fabric_api_down(self, server: FabricMCP):
        """Test error handling when Fabric API is unavailable."""
        with patch("fabric_mcp.core.FabricApiClient") as mock_api_client_class:
            # Simulate connection error
            mock_api_client = Mock()
            mock_api_client_class.return_value = mock_api_client
            mock_api_client.get.side_effect = httpx.ConnectError(
                "Unable to connect to Fabric API"
            )

            # Test that the tool raises appropriate MCP error
            tools = getattr(server, "_FabricMCP__tools", [])
            list_patterns_tool = tools[0]

            with pytest.raises(McpError) as exc_info:
                list_patterns_tool()

            assert "Failed to connect to Fabric API" in str(
                exc_info.value.error.message
            )

    @pytest.mark.asyncio
    async def test_error_handling_with_fabric_api_error(self, server: FabricMCP):
        """Test error handling when Fabric API returns errors."""
        with patch("fabric_mcp.core.FabricApiClient") as mock_api_client_class:
            # Simulate HTTP error
            mock_api_client = Mock()
            mock_api_client_class.return_value = mock_api_client

            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.reason_phrase = "Internal Server Error"

            http_error = httpx.HTTPStatusError(
                "Internal Server Error",
                request=Mock(),
                response=mock_response,
            )
            mock_api_client.get.side_effect = http_error

            # Test that the tool raises appropriate MCP error
            tools = getattr(server, "_FabricMCP__tools", [])
            list_patterns_tool = tools[0]

            with pytest.raises(McpError) as exc_info:
                list_patterns_tool()

            assert "Fabric API error: 500" in str(exc_info.value.error.message)

    def test_server_stdio_integration(self, server: FabricMCP):
        """Test the stdio method integration with mocked MCP run."""
        with patch.object(server.mcp, "run") as mock_run:
            server.stdio()
            mock_run.assert_called_once()

    def test_server_graceful_shutdown_scenarios(
        self, server: FabricMCP, caplog: pytest.LogCaptureFixture
    ):
        """Test graceful shutdown on various interrupt signals."""
        with caplog.at_level(logging.INFO):
            # Test KeyboardInterrupt
            with patch.object(server.mcp, "run", side_effect=KeyboardInterrupt):
                server.stdio()

            # Test CancelledError
            with patch.object(server.mcp, "run", side_effect=CancelledError):
                server.stdio()

        # Should have at least one graceful shutdown message
        assert "Server stopped by user." in caplog.text

    @pytest.mark.asyncio
    async def test_complete_pattern_workflow(
        self, server: FabricMCP, mock_fabric_api_server: MockFabricAPIServer
    ):
        """Test a complete workflow: list patterns -> get details -> run pattern."""

        _ = mock_fabric_api_server  # to get rid of unused variable warning

        tools = getattr(server, "_FabricMCP__tools", [])

        # Step 1: List patterns
        list_patterns_tool = tools[0]
        patterns: list[str] = list_patterns_tool()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

        # Step 2: Get pattern details using a pattern that exists in mock server
        pattern_details_tool = tools[1]
        details = pattern_details_tool("summarize")
        assert isinstance(details, dict)
        assert "name" in details
        assert details["name"] == "summarize"
        assert "description" in details
        assert "system_prompt" in details

        # Step 3: Run pattern
        run_pattern_tool = tools[2]
        result = run_pattern_tool("test_pattern", "Test input")
        assert isinstance(result, dict)
        assert "output_format" in result
        assert "output_text" in result

    def test_server_lifecycle(self, server: FabricMCP):
        """Test complete server lifecycle: init -> configure -> run -> shutdown."""
        # Server is already initialized via fixture
        assert server is not None
        assert hasattr(server, "mcp")

        # Test configuration
        assert server.log_level == "DEBUG"

        # Test run with immediate shutdown
        with patch.object(server.mcp, "run", side_effect=KeyboardInterrupt):
            server.stdio()

        # Server should handle shutdown gracefully
        assert True  # If we get here, shutdown was graceful


@pytest.mark.integration
class TestFabricMCPCli:
    """End-to-end integration tests for the fabric-mcp CLI."""

    def test_version_flag(self):
        """Test that fabric-mcp --version returns the correct version."""
        result = subprocess.run(
            [sys.executable, "-m", "fabric_mcp.cli", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        assert result.returncode == 0
        assert __version__ in result.stdout
        assert f"fabric-mcp, version {__version__}" in result.stdout

    def test_help_flag(self):
        """Test that fabric-mcp --help returns help text."""
        result = subprocess.run(
            [sys.executable, "-m", "fabric_mcp.cli", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )

        assert result.returncode == 0
        assert "A Model Context Protocol server for Fabric AI" in result.stdout
        assert "--version" in result.stdout
        assert "--transport" in result.stdout
        assert "--log-level" in result.stdout

    def test_no_args_shows_missing_transport_error(self):
        """Test that running fabric-mcp with no args errors with missing transport."""
        result = subprocess.run(
            [sys.executable, "-m", "fabric_mcp.cli"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "Missing option '--transport'" in result.stderr

    def test_script_entry_point_version(self):
        """Test the installed script entry point returns correct version."""
        # Test if the fabric-mcp script is available (it should be in dev environment)
        result = subprocess.run(
            ["fabric-mcp", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        # This might fail if not installed in development mode, so we'll check
        if result.returncode == 0:
            assert __version__ in result.stdout
            assert f"fabric-mcp, version {__version__}" in result.stdout
        else:
            # If the script isn't available, we can skip this test
            pytest.skip("fabric-mcp script not available (not installed in dev mode)")

    def test_script_entry_point_help(self):
        """Test the installed script entry point returns help."""
        result = subprocess.run(
            ["fabric-mcp", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )

        # This might fail if not installed in development mode
        if result.returncode == 0:
            assert "A Model Context Protocol server for Fabric AI" in result.stdout
            assert "--version" in result.stdout
            assert "--transport" in result.stdout
        else:
            # If the script isn't available, we can skip this test
            pytest.skip("fabric-mcp script not available (not installed in dev mode)")
