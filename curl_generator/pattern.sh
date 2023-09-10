#!/bin/bash

myArray=(

)

for str in "${myArray[@]}"; do
    curl -X POST -s -d '{"address": "'"$str"'", "coins": ["110000000unibi","100000000unusd","100000000uusdt"]}' "https://faucet.itn-2.nibiru.fi/" &
done
