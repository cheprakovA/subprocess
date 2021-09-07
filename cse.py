import asyncio
import sys


async def test():
    
    with open('mqi.py', 'r') as fin:
        code = '; '.join([u.strip() for u in fin.read().split('\n')])

    proc = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    for _ in range(5):
        await asyncio.sleep(6)
        data = await proc.stdout.readline()
        line = data.decode('ascii').rstrip()
        print(line)

    await proc.wait()


asyncio.run(test())