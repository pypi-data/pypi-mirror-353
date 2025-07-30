"""Core MCP server implementation using the Model Context Protocol."""

import logging
from asyncio.exceptions import CancelledError
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

import httpx
from anyio import WouldBlock
from fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData

from . import __version__
from .api_client import FabricApiClient

DEFAULT_MCP_HTTP_PATH = "/message"
DEFAULT_MCP_SSE_PATH = "/sse"


@dataclass
class PatternExecutionConfig:  # pylint: disable=too-many-instance-attributes
    """Configuration for pattern execution parameters."""

    model_name: str | None = None
    strategy_name: str | None = None
    variables: dict[str, str] | None = None
    attachments: list[str] | None = None
    temperature: float | None = None
    top_p: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None


class FabricMCP(FastMCP[None]):
    """Base class for the Model Context Protocol server."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the MCP server with a model."""
        super().__init__(f"Fabric MCP v{__version__}")
        self.mcp = self
        self.logger = logging.getLogger(__name__)
        self.__tools: list[Callable[..., Any]] = []
        self.log_level = log_level
        self._register_tools()

    def _make_fabric_api_request(
        self,
        endpoint: str,
        pattern_name: str | None = None,
        operation: str = "API request",
    ) -> Any:
        """Make a request to the Fabric API with consistent error handling.

        Args:
            endpoint: The API endpoint to call (e.g., "/patterns/names")
            pattern_name: Pattern name for pattern-specific error messages
            operation: Description of the operation for error messages

        Returns:
            The parsed JSON response from the API

        Raises:
            McpError: For any API errors, connection issues, or parsing problems
        """
        try:
            api_client = FabricApiClient()
            try:
                response = api_client.get(endpoint)
                return response.json()
            finally:
                api_client.close()
        except httpx.RequestError as e:
            raise McpError(
                ErrorData(
                    code=-32603,  # Internal error
                    message="Failed to connect to Fabric API",
                )
            ) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 500 and pattern_name:
                # Check for pattern not found (500 with file not found message)
                error_message = e.response.text or ""
                if "no such file or directory" in error_message:
                    raise McpError(
                        ErrorData(
                            code=-32602,  # Invalid params - pattern doesn't exist
                            message=f"Pattern '{pattern_name}' not found",
                        )
                    ) from e
                # Other 500 errors for pattern requests
                raise McpError(
                    ErrorData(
                        code=-32603,  # Internal error
                        message=f"Fabric API internal error: {error_message}",
                    )
                ) from e
            # Generic HTTP status errors
            status_code = e.response.status_code
            reason = e.response.reason_phrase or "Unknown error"
            raise McpError(
                ErrorData(
                    code=-32603,  # Internal error
                    message=f"Fabric API error: {status_code} {reason}",
                )
            ) from e
        except Exception as e:
            raise McpError(
                ErrorData(
                    code=-32603,  # Internal error
                    message=f"Unexpected error during {operation}: {e}",
                )
            ) from e

    def _register_tools(self):
        """Register all MCP tools with the server."""

        @self.tool()
        def fabric_list_patterns() -> list[str]:
            """Return a list of available fabric patterns."""
            # Use helper method for API request
            response_data = self._make_fabric_api_request(
                "/patterns/names", operation="retrieving patterns"
            )

            # Validate response is a list
            if not isinstance(response_data, list):
                error_msg = "Invalid response format from Fabric API: expected list"
                raise McpError(
                    ErrorData(code=-32603, message=error_msg)  # Internal error
                )

            # Ensure all items are strings
            validated_patterns: list[str] = []
            for item in response_data:  # type: ignore[misc]
                if isinstance(item, str):
                    validated_patterns.append(item)
                else:
                    # Log warning but continue with valid patterns
                    item_any = cast(Any, item)
                    item_type = (
                        type(item_any).__name__ if item_any is not None else "None"
                    )
                    logging.warning("Non-string pattern name found: %s", item_type)

            return validated_patterns

        self.__tools.append(fabric_list_patterns)

        @self.tool()
        def fabric_get_pattern_details(pattern_name: str) -> dict[str, str]:
            """Retrieve detailed information for a specific Fabric pattern."""
            # Use helper method for API request with pattern-specific error handling
            response_data = self._make_fabric_api_request(
                f"/patterns/{pattern_name}",
                pattern_name=pattern_name,
                operation="retrieving pattern details",
            )

            # Transform Fabric API response to MCP expected format
            details = {
                "name": response_data.get("Name", ""),
                "description": response_data.get("Description", ""),
                "system_prompt": response_data.get("Pattern", ""),
            }

            return details

        self.__tools.append(fabric_get_pattern_details)

        @self.tool()
        def fabric_run_pattern(
            pattern_name: str,
            input_text: str = "",
            stream: bool = False,
            config: PatternExecutionConfig | None = None,
        ) -> dict[Any, Any]:
            """
            Execute a Fabric pattern with options and optional streaming.

            Args:
                pattern_name: The name of the fabric pattern to run.
                input_text: The input text to be processed by the pattern.
                stream: Whether to stream the output.
                config: Optional configuration for execution parameters.

            Returns:
                dict[Any, Any]: Contains the output format and text.
            """
            if config is None:
                config = PatternExecutionConfig()

            # Use config to avoid unused warnings
            _ = (
                stream,
                config.model_name,
                config.strategy_name,
                config.variables,
                config.attachments,
                config.temperature,
                config.top_p,
                config.presence_penalty,
                config.frequency_penalty,
            )

            return {
                "output_format": "markdown",
                "output_text": (
                    f"Pattern {pattern_name} executed with input: {input_text}"
                ),
            }

        self.__tools.append(fabric_run_pattern)

        @self.tool()
        def fabric_list_models() -> dict[Any, Any]:
            """Retrieve configured Fabric models by vendor."""
            # This is a placeholder for the actual implementation
            return {
                "models": ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"],
                "vendors": {
                    "openai": ["gpt-4", "gpt-3.5-turbo"],
                    "anthropic": ["claude-3-opus"],
                },
            }

        self.__tools.append(fabric_list_models)

        @self.tool()
        def fabric_list_strategies() -> dict[Any, Any]:
            """Retrieve available Fabric strategies."""
            # This is a placeholder for the actual implementation
            return {
                "strategies": [
                    {
                        "name": "default",
                        "description": "Default strategy for pattern execution",
                        "prompt": "Execute the pattern with default settings",
                    },
                    {
                        "name": "creative",
                        "description": "Creative strategy with higher temperature",
                        "prompt": "Execute the pattern with creative parameters",
                    },
                ]
            }

        self.__tools.append(fabric_list_strategies)

        @self.tool()
        def fabric_get_configuration() -> dict[Any, Any]:
            """Retrieve Fabric configuration with sensitive values redacted."""
            # This is a placeholder for the actual implementation
            return {
                "openai_api_key": "[REDACTED_BY_MCP_SERVER]",
                "ollama_url": "http://localhost:11434",
                "anthropic_api_key": "[REDACTED_BY_MCP_SERVER]",
                "fabric_config_dir": "~/.config/fabric",
            }

        self.__tools.append(fabric_get_configuration)

    def http_streamable(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        mcp_path: str = DEFAULT_MCP_HTTP_PATH,
    ):
        """Run the MCP server with StreamableHttpTransport."""
        try:
            self.mcp.run(
                transport="streamable-http", host=host, port=port, path=mcp_path
            )
        except (KeyboardInterrupt, CancelledError, WouldBlock) as e:
            # Handle graceful shutdown
            self.logger.debug("Exception details: %s: %s", type(e).__name__, e)
            self.logger.info("Server stopped by user.")

    def sse(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        path: str = DEFAULT_MCP_SSE_PATH,
    ):
        """Run the MCP server with SSE transport."""
        try:
            self.mcp.run(transport="sse", host=host, port=port, path=path)
        except (KeyboardInterrupt, CancelledError, WouldBlock) as e:
            # Handle graceful shutdown
            self.logger.debug("Exception details: %s: %s", type(e).__name__, e)
            self.logger.info("Server stopped by user.")

    def stdio(self):
        """Run the MCP server."""
        try:
            self.mcp.run()
        except (KeyboardInterrupt, CancelledError, WouldBlock):
            # Handle graceful shutdown
            self.logger.info("Server stopped by user.")
