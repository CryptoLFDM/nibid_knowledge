import yaml

stream = open('harvest_key.yml', 'r')
obj = yaml.safe_load(stream)
addresses = []
for x, line in enumerate(obj):
    addresses.append(line['address'])
    if x % 10 == 0 and x > 0:
        a = open("pattern.sh", "r")
        d = open("sample/shell_{}.sh".format(x), "w")
        for i, sample in enumerate(a):
            d.write(sample)
            if i == 2:
                for address in addresses:
                    d.write("{}\n".format(address))
        addresses = []
        d.close()
        a.close()

stream.close()