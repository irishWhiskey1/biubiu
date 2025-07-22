from app.agent.biubiu import Biubiu
import json
import asyncio

async def main():
    with open('/Users/niuzhenqian/myCodeSpace/mypythonspace/biubiu/conf.json', 'r') as f:
        conf = json.load(f)
    agent = await Biubiu.create(conf=conf)
    query = input('请输入你的问题:')
    answer = await agent.run(query)
    print(answer)
    await agent.close()

if __name__ == '__main__':
    asyncio.run(main())