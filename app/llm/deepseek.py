from typing import  Optional, Dict, Any, List
from pydantic import model_validator
from openai import AsyncOpenAI,APIError

from llm.base import BaseLLM

class DeepSeek(BaseLLM):
    def __init__(self, conf):
        super().__init__(conf["deepseek"])
        self.name = "deepseek"
        self.client = AsyncOpenAI(api_key=self.apiKey,base_url=self.baseURL)
    @model_validator(mode="before")
    def validate_before(cls, conf: dict[str,dict]):
        if "deepseek" not in conf:
            raise ValueError("DeepSeek configuration is missing")
        return conf
    async def execute(self, context, tools):
        try:
            response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=context,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    tools=tools,
                    tool_choice="auto",
                    stream=False,
                )
            return self.parse_response(response)
        except APIError as e:
            raise ValueError(f"OpenAI Error {e}")
        except Exception as e:
            raise ValueError(f"Unknown error {e}")
    def parse_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """解析整个 API 响应"""
        if not response or not hasattr(response, "choices"):
            return None
        first_choice = response.choices[0] if len(response.choices) > 0 else None
        if not first_choice or not hasattr(first_choice, "message"):
            return None
        return self.parse_message(first_choice.message)
    def parse_message(self, message: Any) -> Dict[str, Any]:
        """解析单条消息，包括 content 或 tool_calls"""
        result = {"content": None, "tool_calls": List}
        if not message:
            return result

        # 解析 content
        if hasattr(message, "content") and message.content:
            result["content"] = str(message.content)

        # 解析 tool_calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = str(tool_call.function.name) if hasattr(tool_call.function, "name") else None
                tool_args = str(tool_call.function.arguments) if hasattr(tool_call.function, "arguments") else None
                if tool_name and tool_args:
                    result["tool_calls"].append({
                        "id": str(tool_call.id) if hasattr(tool_call, "id") else None,
                        "name": tool_name,
                        "args": tool_args
                    })
        return result
        