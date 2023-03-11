import logging
import subprocess
import time
import os

import requests  # Thoses packages need to be installed
import yaml

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level='INFO')  # Just a looger

#  CONFIG PART
wallet_who_collect = os.getenv('NIBID_ADDR')  # put the address who should collectd
wallet_password = os.getenv('NIBID_ADDR_PASSWORD')  # put your password prompt
wallet_to_harvest_pattern = ['harvest']  # wallet pattern to harvest
wallet_minimum_harvest = 25000  # minimal unibi to get
file_to_read = 'sample.yml'  # output file generated from nibib keys list > sample.yml
reroll_enabled = True  # This option allow to generate a file with address unused.
reroll = []
reroll_location = 'reroll.yml'

# This method parse the whole wallet file and only return the one who match pattern
def collect_wallet_info():
    stream = open(file_to_read, 'r')  # 'document.yaml' contains a single YAML document.
    nibid_wallet = yaml.safe_load(stream)
    wallets = []
    for x, line in enumerate(nibid_wallet):
        for pattern in wallet_to_harvest_pattern:
            if pattern in line['name']:
                wallets.append({'name': line['name'], 'address': line['address']})
    return wallets


# This method ask explorer.pro to get wallet status and create a custom object of what should be harvested
def check_wallet_amount(response, wallet_name):
    #    var = {'address': 'nibi1y3cehkfcvk5wml52yz2aeqqf92et8xwcwcne8a',
    #           'wallet': {'available': 110000000, 'vesting': 0, 'delegated': 0, 'unbonding': 0, 'reward': 0,
    #                      'commission': 0},
    #           'assets': [{'denom': 'unibi', 'amount': 110000000}, {'denom': 'unusd', 'amount': 100000000},
    #                      {'denom': 'uusdt', 'amount': 100000000}]}
    custom_response = {'address': '', 'wallet_name': wallet_name, 'assets': {}}
    if response['wallet']['available'] > wallet_minimum_harvest:
        custom_response['address'] = response['address']
        custom_response['unibi'] = response['wallet']['available']
        for asset in response['assets']:
            if ('uusdt' in asset['denom'] or 'unusd' in asset['denom']) and asset['amount'] == 100000000:
                custom_response['assets'][asset['denom']] = asset['amount']
        return custom_response
    else:
        logging.warning('Not gonna harvest {} | {}, not enought unibi minimun is set to {} unibi'.format(wallet_name,
                                                                                                         response[
                                                                                                             'address'],
                                                                                                           wallet_minimum_harvest))
    return None

# This method run nibid tx
def run_harvest(address, asset, amount):
    args = '/usr/local/bin/nibid tx bank send {} {} {}{} --fees 5000unibi --log_format json -y'.format(address,
                                                                                                       wallet_who_collect,
                                                                                                       amount,
                                                                                                       asset)
    process = subprocess.Popen([args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    if wallet_password != '':
        process.communicate(wallet_password)


# This is the main loop who harvest all wallet & all asset
def harvest_wallet(wallets):
    for wallet in wallets:
        wallet_name = wallet['name']
        wallet_address = wallet['address']
        logging.info('Proceed {} | {}'.format(wallet_address, wallet_name))
        resp = requests.get('https://api.nibiru.exploreme.pro/accounts/{}'.format(wallet_address))
        if resp.status_code != 200:
            logging.warning('{} | {} not found on explorer'.format(wallet_address, wallet_name))
            if reroll_enabled:
                logging.info('{} | {} added to reroll'.format(wallet_address, wallet_name))
                reroll.append({'name': wallet_name, 'address': wallet_address})
            continue
        else:
            harvestable = check_wallet_amount(resp.json(), wallet_name)
            if harvestable is None:
                continue
        logging.info('Gonna harvest {}'.format(harvestable))

        fees = 5000
        for asset in harvestable['assets']:
            logging.info('Gonna harvest {} from {} | {}'.format(asset, wallet_name, wallet_address))
            run_harvest(harvestable['address'], asset, harvestable['assets'][asset])
            time.sleep(2)
            logging.info('Wait 2 seconds between calls')
            fees = fees + 5000
        logging.info('Gonna harvest {} from {} | {}'.format('unibi', wallet_name, wallet_address))
        run_harvest(harvestable['address'], 'unibi', harvestable['unibi'] - fees)
        time.sleep(2)
        logging.info('Wait 2 seconds between calls')


if __name__ == '__main__':
    wallets_from_file = collect_wallet_info()
    harvest_wallet(wallets_from_file)
    if reroll_enabled:
        logging.info('dumping reroll to {}'.format(reroll_location))
        with open(reroll_location, 'w') as file:
            yaml.dump(reroll, file)
