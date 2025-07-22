from typing import Optional, Dict, Any, List
from pydantic import model_validator
from openai import AsyncOpenAI, APIError

from app.llm.base import BaseLLM

class ThinkModel(BaseLLM):
    def __init__(self, conf):
        super().__init__(**conf)
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
                response_format={
                    'type': 'json_object'
                }
            )
            return self.parse_response(response)
        except APIError as e:
            raise ValueError(f"OpenAI Error {e}")
        except Exception as e:
            raise ValueError(f"Unknown error {e}")

    def parse_response(self, response: Any) -> str:
        """Parse the entire API response"""
        if not response or not hasattr(response, "choices"):
            return None
        first_choice = response.choices[0] if len(response.choices) > 0 else None
        if not first_choice or not hasattr(first_choice, "message"):
            return None
        message = first_choice.message
        if not message or not hasattr(message, "content"):
            return None
        
        return message.content