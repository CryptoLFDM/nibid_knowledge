    import yaml

    file_to_read = "sample.yml"  # output file generated from nibib keys list > sample.yml
    curl_pattern = "curl_background.bash"
    dest = "sample/shell_"

    stream = open(file_to_read, 'r')
    obj = yaml.safe_load(stream)
    addresses = []
    for x, line in enumerate(obj):
        addresses.append(line['address'])
        if x % 10 == 0 and x > 0:
            a = open(curl_pattern, "r")
            d = open("{}{}.sh".format(dest, x), "w")
            for i, sample in enumerate(a):
                d.write(sample)
                if i == 2:
                    for address in addresses:
                        d.write('{}\n'.format(address))
            addresses = []
            d.close()
            a.close()

    stream.close()

