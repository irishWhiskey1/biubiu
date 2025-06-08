
import asyncio
from typing import Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

from .base import BaseTool
load_dotenv()  # load environment variables from .env

class MCPTool(BaseTool):
    session: Optional[ClientSession] = None
    def __init__(self,session: Optional[ClientSession],name: str,description: str,parameters: dict):
        if session is None:
            raise ValueError("A session must be provided")
        self.session = session
        self.name = name
        self.description = description
        self.parameters = parameters
    """MCP Tool 调用方法"""
    async def execute(self, **kwargs) -> Any:
       await self.session.call_tool(self.name, kwargs)