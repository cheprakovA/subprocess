import asyncio
import sys


async def get_date():
    code = 'import datetime, time; print(datetime.datetime.now()); time.sleep(2); ' + \
        'print(datetime.datetime.now()); time.sleep(2)'

    proc = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code,
        stdout=asyncio.subprocess.PIPE)

    await proc.wait()
    data1 = await proc.stdout.readline()
    data2 = await proc.stdout.readline()
    line = data1.decode('ascii').rstrip() + ' ' + \
        data2.decode('ascii').rstrip()

    # await proc.wait()
    return line

date = asyncio.run(get_date())
print(f"Timestamps: {date}")
