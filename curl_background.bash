#!/bin/bash

myArray=(

)

for str in ${myArray[@]}; do
    curl -X POST -s -d '{"address": "'"$str"'", "coins": ["110000000unibi","100000000unusd","100000000uusdt"]}' "https:\
//faucet.itn-1.nibiru.fi/" &
done