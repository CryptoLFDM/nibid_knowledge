import argparse
import asyncio
import aiohttp
import yaml
import json

def epur_yaml():
    stream = open('wallet.yml', 'r')
    obj = yaml.safe_load(stream)
    if patterns == []:
        stream.close()
        return obj

    harvest = []
    for wallet in obj:
        for pattern in patterns:
            if pattern in wallet['name']:
                harvest.append(wallet)
    stream.close()
    return harvest


async def make_numbers(obj):
    for i in obj:
        yield i


async def make_account():
    stream = open('sample/{}'.format(args.iterator), 'r')
    obj = yaml.safe_load(stream)
    url = "https://faucet.itn-1.nibiru.fi/"
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        # prepare the coroutines that post
        async for x in make_numbers(obj):
            post_tasks.append(do_post(session, url, x))
        # now execute them all at once
        await asyncio.gather(*post_tasks)
    stream.close()


async def do_post(session, url, x):
    req = {"address": x, "coins": ["110000000unibi", "100000000unusd", "100000000uusdt"]}
    json_object = json.dumps(req, indent=4)
    async with session.post(url, data=json_object) as response:
        data = await response.text()


parser = argparse.ArgumentParser(
    prog='Fast & furious request',
    description='Only Maxxroot nee to know',
)
parser.add_argument('-m', '--mode')
parser.add_argument('-b', '--batch', type=int)  # option that takes a value
parser.add_argument('-i', '--iterator', type=int)
args = parser.parse_args()
addresses = []
patterns = []

if args.mode == 'gen':
    i = 1
    wallets = epur_yaml()
    for x, line in enumerate(wallets):
        addresses.append(line['address'])
        if x % args.batch == 0 and x > 0:
            with open('sample/{}'.format(i), 'w') as file:
                yaml.dump(addresses, file)
            i = i + 1

    if x % 40 != 0:
        i + i + 1
        with open('sample/{}'.format(i), 'w') as file:
            yaml.dump(addresses, file)

else:
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(make_account())
    except:
        pass
