import unittest
import asyncio
from app.llm.deepseek import DeepSeek

class TestDeepSeek(unittest.TestCase):
    def test_execute(self):
        deepseek = DeepSeek({
                "name":"deepseek",
                "model":"deepseek-chat",
                "api_key":"sk-ac7c513428394dc0a5418eafd6858e34",
                "base_url":"https://api.deepseek.com",
        })
        result = asyncio.run(deepseek.execute([{"role": "user", "content": "Hello"}], []))
        print(result)

if __name__ == '__main__':
    unittest.main()