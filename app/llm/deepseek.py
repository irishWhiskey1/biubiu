from typing import Optional, Dict, Any, List
from pydantic import model_validator
from openai import AsyncOpenAI, APIError

from app.llm.base import BaseLLM

class DeepSeek(BaseLLM):
    def __init__(self, conf):
        super().__init__(**conf)
        self.name = "deepseek"
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def execute(self, context, tools):
        try:
            tool_choice = "auto"
            if not tools:
                tool_choice = "none"
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=context,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=tools,
                tool_choice=tool_choice,
                stream=False,
            )
            return self.parse_response(response)
        except APIError as e:
            raise ValueError(f"OpenAI Error {e}")
        except Exception as e:
            raise ValueError(f"Unknown error {e}")

    def parse_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """Parse the entire API response"""
        if not response or not hasattr(response, "choices"):
            return None
        first_choice = response.choices[0] if len(response.choices) > 0 else None
        if not first_choice or not hasattr(first_choice, "message"):
            return None
        return self.parse_message(first_choice.message)

    def parse_message(self, message: Any) -> Dict[str, Any]:
        """Parse a single message, including content or tool_calls"""
        result = {"content": None, "tool_calls": []}
        if not message:
            return result

        # Parse content
        if hasattr(message, "content") and message.content:
            result["content"] = str(message.content)

        # Parse tool_calls
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