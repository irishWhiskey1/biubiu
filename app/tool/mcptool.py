from typing import Optional, Any
from mcp import ClientSession
from contextlib import AsyncExitStack


from app.tool.base import BaseTool
from app.tool.session import Connection,_create_stdio_session,DEFAULT_ENCODING,DEFAULT_ENCODING_ERROR_HANDLER

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

async def InitMCPTools(connConfigs:dict[str,Connection])->list[MCPTool]:
    asyncStack = AsyncExitStack()
    mcpTools = list[MCPTool]

    for confName,config in connConfigs.items():
        if "transport" not in config:
            raise ValueError(
                'config error: missing required key transport'
                'now supported transports are stdio'
            )

        if config["transport"] == "stdio":
            if "command" not in config:
                raise ValueError("'command' parameter is required for stdio config")
            if "args" not in config:
                raise ValueError("'args' parameter is required for stdio config")
        session = await asyncStack.enter_async_context(_create_stdio_session(
            command=config["command"],
            args=config["args"],
            env=config.get("env"),
            cwd=config.get("cwd"),
            encoding=config.get("encoding", DEFAULT_ENCODING),
            encoding_error_handler=config.get(
                "encoding_error_handler", DEFAULT_ENCODING_ERROR_HANDLER
            ),
            session_kwargs=config.get("session_kwargs"),))
        await session.initialize()
        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            mcpTool = MCPTool(session,tool.name,tool.description,tool.parameters)
            mcpTools.append(mcpTool)
    return mcpTools