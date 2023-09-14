import yaml

stream = open('wallet.yml', 'r')
obj = yaml.safe_load(stream)
addresses = []
patterns = ['london', 'paris']

def epur_yaml(wallets):
    harvest = []
    for wallet in wallets:
        for pattern in patterns:
            if pattern in wallet['name']:
                harvest.append(wallet)
    return harvest

def add_address(x, i):
    a = open("pattern.sh", "r")
    d = open("sample/{}".format(i), "w")
    for i, sample in enumerate(a):
        d.write(sample)
        if i == 2:
            for address in addresses:
                d.write("{}\n".format(address))
    d.close()
    a.close()


wallets = epur_yaml(obj)
i = 1
for x, line in enumerate(wallets):
    addresses.append(line['address'])
    if x % 40 == 0 and x > 0:
        add_address(x, i)
        addresses = []
        i = i + 1

if x % 40 != 0:
    add_address(x, i)

stream.close()
