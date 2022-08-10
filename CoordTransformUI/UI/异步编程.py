import asyncio
# async def func():
#     print('156')
#     response = await asyncio.sleep(2)
#     print('OK', response)
# asyncio.run(func())

async def func1():
    print(1)
    await asyncio.sleep(2)
    print('fun1回调')
    return '123'

async def func2():
    print(2)
    await asyncio.sleep(2)
    print('fun2回调')
    return '456'


async def main():
    print('main开始')

    taks1 = asyncio.create_task(func1())
    task2 = asyncio.create_task(func2())
    print('main结束')

    print(await taks1)

asyncio.run(main())
