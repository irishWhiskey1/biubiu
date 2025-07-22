from typing import Optional, Any
from mcp import ClientSession
from contextlib import AsyncExitStack


from app.tool.base import BaseTool
from app.tool.session import Connection,_create_stdio_session,DEFAULT_ENCODING,DEFAULT_ENCODING_ERROR_HANDLER

class MCPTool(BaseTool):
    name: str
    description: str
    parameters: Optional[dict] = None
    session: Optional[ClientSession] = None

    def __init__(self,session: Optional[ClientSession],name: str,description: str,parameters: dict):
        if session is None:
            raise ValueError("A session must be provided")
        self.session = session
        self.name = name
        self.description = description
        self.parameters = parameters

    """MCP Tool 调用方法"""
    async def execute(self, kwargs) -> Any:
       resp = await self.session.call_tool(self.name, kwargs)
       return resp

async def InitMCPTools(connConfigs:dict[str,Connection], stack:AsyncExitStack)->list[MCPTool]:
    mcpTools = []

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
        session = await stack.enter_async_context(_create_stdio_session(
            command=config["command"],
            args=config["args"],
            env=config.get("env",None),
            cwd=config.get("cwd",None),
            encoding=config.get("encoding", DEFAULT_ENCODING),
            encoding_error_handler=config.get(
                "encoding_error_handler", DEFAULT_ENCODING_ERROR_HANDLER
            ),
            session_kwargs=config.get("session_kwargs",None),))
        await session.initialize()
        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            mcpTool = MCPTool(session,tool.name,tool.description,tool.inputSchema['properties'])
            mcpTools.append(mcpTool)
    return mcpTools

def GetMCPToolsDescription(tools:list[MCPTool])->str:
    str = f"1、Excuter：大语言模型，负责内容总结、汇总、生成等工作，并且可以使用function call 产生其他工具的入参\r\n"
    for index,tool in enumerate(tools):
       str += f"{index+2}、{tool.name}：{tool.description}\r\n"
    return str
