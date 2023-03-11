import yaml

stream = open('wallet.yml', 'r')
obj = yaml.safe_load(stream)
addresses = []

def add_address(x):
    a = open("pattern.sh", "r")
    d = open("sample/shell_{}.sh".format(x), "w")
    for i, sample in enumerate(a):
        d.write(sample)
        if i == 2:
            for address in addresses:
                d.write("{}\n".format(address))
    d.close()
    a.close()

for x, line in enumerate(obj):
    addresses.append(line['address'])
    if x % 10 == 0 and x > 0:
        add_address(x)
        addresses = []
add_address(x)

stream.close()
