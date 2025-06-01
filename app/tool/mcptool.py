
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

from .base import BaseTool
load_dotenv()  # load environment variables from .env

class MCPClient(BaseTool):
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
    
    async def connect_to_server(self, server_script_conf: dict):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        
        command = server_script_conf.get("command")
        args = server_script_conf.get("args")
        env = server_script_conf.get("env")
        if not command:
            raise ValueError("No 'command' found in server_script_conf.")
        if not isinstance(args, list[str]):
            raise ValueError("args in server_script_conf should be a list")
        if not isinstance(env, dict[str,str]):
            raise ValueError("env in server_script_conf should be a dict")

        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
   