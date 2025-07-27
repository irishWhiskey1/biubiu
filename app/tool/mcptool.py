from typing import Optional, Any
from mcp import ClientSession
from contextlib import AsyncExitStack
from typing import Any, Dict

from app.tool.base import BaseTool
from app.tool.session import Connection,_create_stdio_session,DEFAULT_ENCODING,DEFAULT_ENCODING_ERROR_HANDLER

class MCPTool(BaseTool):
    # MCP工具名称
    name: str
    # 和MCP工具建立通信的客户端
    session: Optional[ClientSession] = None
    # 对该MCP工具的描述
    # 其中key为工具名称，value为工具的描述
    descriptions: dict = None
    # 该MCP工具的参数
    # 其中key为工具名称，value为工具的参数
    parameters:dict = None
    def __init__(self,session: Optional[ClientSession],name: str,descriptions: dict,parameters: dict):
        if session is None:
            raise ValueError("A session must be provided")
        self.session = session
        self.name = name
        self.descriptions = descriptions
        self.parameters = parameters

    """MCP Tool 调用方法"""
    async def execute(self,toolName:str, kwargs) -> Any:
       if toolName not in self.descriptions:
           raise ValueError("toolName not found")
       resp = await self.session.call_tool(toolName, kwargs)
       return resp
    """获取MCP某个工具的参数"""
    def to_param(self,toolName :str) -> Dict:
        function_name = f"{self.name}-{toolName}"
        return {
            "type": "function",
            "function": {
                "name": function_name,
                "description": self.descriptions.get(toolName,None),
                "parameters": {
                   "type": "object",
                   "properties": self.parameters.get(toolName,None),
                }
            },
        }

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
        descriptions = {}
        parameters = {}
        for tool in tools_response.tools:
            descriptions[tool.name] = tool.description
            parameters[tool.name] = tool.inputSchema['properties']

        mcpTool = MCPTool(session,confName,descriptions,parameters)
        mcpTools.append(mcpTool)

    return mcpTools

def GetMCPToolsDescription(mcpTools:list[MCPTool])->str:
    str = f"1、Excuter：通用大语言模型，负责内容总结、汇总、生成等工作，并且可以使用function call 产生其他工具的入参\r\n"
    index = 2
    for mcpTool in mcpTools:
        for toolName,toolDescription in mcpTool.descriptions.items():
            str += f"{index}、{mcpTool.name}-{toolName}:{toolDescription}\r\n"
            index += 1

    return str
