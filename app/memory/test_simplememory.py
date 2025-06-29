import unittest
from app.memory.simplememory import SimpleMemory

class TestSimpleMemory(unittest.TestCase):
    def test_execute(self):
        # 用于设置的context，能取到的最新的context
        testcases = [
            {
                "set": [{"a1": "b1"}],
                "get": {"a1": "b1"}
            },
            {
                "set": [{"a1":"b1"},{"a2": "b2"},{"a3": "b3"},{"a4": "b4"},{"a5": "b5"},{"a6": "b6"},
                        {"a7": "b7"},{"a8": "b8"},{"a9": "b9"},{"a10": "b10"},{"a11": "b11"}],
                "get": {"a11": "b11"}
            },
        ]
        for tc in testcases:
            with self.subTest(tc=tc):
                memory = SimpleMemory()
                memory.set_context(tc.get("set"))
                lis = memory.get_context()
                print(lis)
                self.assertDictEqual(lis[-1], tc.get("get"))
if __name__ == '__main__':
    unittest.main()