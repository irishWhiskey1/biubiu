import unittest
import asyncio
from app.tool.mcptool import InitMCPTools,GetMCPToolsDescription
from contextlib import AsyncExitStack

class TestInitMCPTools(unittest.TestCase):
    def test_execute(self):
        async def run_test():
            async with AsyncExitStack() as stack:
                tools = await InitMCPTools({
                    "jino": {
                        "transport": "stdio",
                        "command": "uv",
                        "args": [ 
                                    "--directory",
                                    "/Users/niuzhenqian/myCodeSpace/mypythonspace/jina/mcp-server",
                                    "run",
                                    "main.py",
                        ],
                        "env": {
                            'JINA_API_KEY': 'jina_b64db9f29ba64242acf409cc69a6a4a2N7jRxU7k6HQ7RgOdRPClfuRnezMN',
                            'PYTHONIOENCODING':'utf-8'
                        }
                    }
                }, stack)
                print(GetMCPToolsDescription(tools))
                resp = await tools[0].execute("search",{"q":"gta5"})
                print(resp)
        asyncio.run(run_test())
if __name__ == '__main__':
    unittest.main()