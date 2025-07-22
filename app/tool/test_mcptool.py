import unittest
import asyncio
from app.tool.mcptool import InitMCPTools
from contextlib import AsyncExitStack

class TestInitMCPTools(unittest.TestCase):
    def test_execute(self):
        async def run_test():
            async with AsyncExitStack() as stack:
                tools = await InitMCPTools({
                    "demo": {
                        "transport": "stdio",
                        "command": "/Users/niuzhenqian/Library/Python/webui-3.11/bin/python",
                        "args": ["-m", "demo"],
                        "env": {'PYTHONPATH': '/Users/niuzhenqian/myCodeSpace/mypythonspace/py11demo'}
                    }
                }, stack)
                print(tools[0].to_param())
                print(tools[0].name)
                resp = await tools[0].execute({"a":1, "b":1})
                print(resp)
        asyncio.run(run_test())
if __name__ == '__main__':
    unittest.main()