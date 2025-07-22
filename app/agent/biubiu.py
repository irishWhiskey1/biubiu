import json
from typing import Optional, Dict, Any, List
from app.agent.base import BaseAgent
from app.llm.base import BaseLLM
from app.llm.excutemodel import ExcuteModel
from app.llm.thinkmodel import ThinkModel
from app.memory.base import BaseMemory
from app.memory.simplememory import SimpleMemory
from app.tool.mcptool import InitMCPTools,GetMCPToolsDescription
from app.tool.base import BaseTool
from app.logger.logger import logger
from pydantic import Field
from contextlib import AsyncExitStack

class Biubiu(BaseAgent):
    name:str = "Biubiu"
    thinkModel: BaseLLM = Field(default=None, exclude=True)  # 使用Field标记非序列化字段
    excuteModel: BaseLLM = Field(default=None, exclude=True)
    thinkMemory: BaseMemory = Field(default=None, exclude=True)
    excuteMemory: BaseMemory = Field(default=None, exclude=True)
    mcpTools: List[BaseTool] = Field(default_factory=list, exclude=True)
    stack:AsyncExitStack = Field(default=None, exclude=True)

    def __init__(self,thinkModel,excuteModel,thinkMemory,excuteMemory, mcpTools,stack):
        super().__init__()
        self.thinkModel = thinkModel
        self.excuteModel = excuteModel
        self.thinkMemory = thinkMemory
        self.excuteMemory = excuteMemory
        self.mcpTools = mcpTools

        # 初始化思考模型的记忆
        thinkPrompt = '你是一个任务流程规划器，你可以使用的工具有：\r\n'
        thinkPrompt += GetMCPToolsDescription(self.mcpTools)
        thinkPrompt += '输出格式为json，例子为' + '{"steps":[{"stepNum":1,"useTool":Searcher,"purpose":"搜集资料"}]}'
        self.thinkMemory.set_context([{'role':'system','content':thinkPrompt}])

        # 初始化执行模型的记忆
        excutePrompt = '你是一个任务流程执行器，你只可以严格按照下面所给出的任务步骤进行决策和执行，当没给出任务步骤时，你可以自由发挥'
        self.excuteMemory.set_context([{'role':'system','content':excutePrompt}])
        self.stack = stack
    # async def __aenter__(self):
    #     return self

    async def close(self):
        await self.stack.aclose()
    @classmethod
    async def create(cls,conf:dict) -> None:
        if "biubiu" not in conf:
            raise ValueError("biubiu config not found")
        biubiuConf = conf["biubiu"]

        if "thinkmodel" not in biubiuConf:
            raise ValueError("thinkmodel config not found")
        thinkModel = ThinkModel(biubiuConf["thinkmodel"])

        if "excutemodel" not in biubiuConf:
            raise ValueError("excutemodel config not found")
        excuteModel = ExcuteModel(biubiuConf["excutemodel"])

        if "thinkmemory" not in biubiuConf:
            raise ValueError("thinkmemory config not found")
        thinkMemory = SimpleMemory(biubiuConf["thinkmemory"].get("max_context_size",None))

        if "excutememory" not in biubiuConf:
            raise ValueError("excutememory config not found")
        excuteMemory = SimpleMemory(biubiuConf["excutememory"].get("max_context_size",None))

        if "tools" not in biubiuConf:
            raise ValueError("tools config not found")
        stack = AsyncExitStack()
        mcpTools = await InitMCPTools(conf["biubiu"]["tools"],stack)
        return cls(thinkModel,excuteModel,thinkMemory,excuteMemory, mcpTools,stack)

    async def run(self,query:str) -> str:
        thinkSteps = await self.__think(query)
        if len(thinkSteps) == 0:
            self.excuteMemory.set_context([{'role':'user','content':f'帮我解决下面的问题{query}'}])
            return await self.excuteModel.execute(self.excuteMemory.get_context(),None)

        for step in thinkSteps:
            logger.info(f"step:{step['stepNum']}, 使用工具: {step['useTool']}, 目的: {step['purpose']}")
            await self.__excute(query,step)
        
        return self.excuteMemory.get_context()[-1].get('content',None)
    async def __think(self,query:str):
        queryPrompt = f'请规划下面的问题：{query}'
        self.thinkMemory.set_context([{'role':'user','content':queryPrompt}])
        llmResp = await self.thinkModel.execute(self.thinkMemory.get_context(),None)
        
        thinkSteps = json.loads(llmResp)['steps']
        if len(thinkSteps) == 0:
            return
        for step in thinkSteps:
           logger.info(f"step:{step['stepNum']}, 使用工具: {step['useTool']}, 目的: {step['purpose']}")
        return thinkSteps
    async def __excute(self,query:str,thinkStep:dict):
        stepNum = thinkStep['stepNum']
        stepToolName = thinkStep['useTool']
        stepPurpose = thinkStep['purpose']
        funcs = []
        if stepToolName == 'Excuter':
            self.excuteMemory.set_context([{'role':'system','content':f'根据上述内容，解决一下问题：{query}'}])
        else:
            mcpTool = [tool for tool in self.mcpTools if tool.name == stepToolName][0]
            funcCallPrompt = f'步骤{stepNum}：结合上面的内容，使用{stepToolName}工具，目的{stepPurpose}'
            self.excuteMemory.set_context([{'role':'system','content':funcCallPrompt}])
            funcs = [mcpTool.to_param()]
        llmResp = await self.excuteModel.execute(self.excuteMemory.get_context(),funcs)
        funcCallList = llmResp['tool_calls']
        if len(funcCallList) == 0:
            self.excuteMemory.set_context([{'role':'assistant','content':llmResp['content']}])
            return
        for funcCall in funcCallList:
            mcpTool = [tool for tool in self.mcpTools if tool.name == stepToolName][0]
            funcResp = await mcpTool.execute(funcCall["args"])
            self.excuteMemory.set_context([{'role':'assistant','content':f'{funcResp}'}])

        return
