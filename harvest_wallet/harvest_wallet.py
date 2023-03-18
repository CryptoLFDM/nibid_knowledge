import logging
import subprocess
import time
import os

import requests  # Thoses packages need to be installed
import yaml
import colorlog

# Logging part
DEFAULT = 1
INFO = 2
SUCCESS = 3
ABORTED = 4
WARNING = 5
FAILED = 6
logging.addLevelName(DEFAULT, 'INFO')
logging.addLevelName(INFO, 'INFO')
logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(ABORTED, 'ABORTED')
logging.addLevelName(WARNING, 'WARNING')
logging.addLevelName(FAILED, 'FAILED')
color_mapping = {
    "DEFAULT": 'grey',
    "INFO": 'cyan',
    'SUCCESS': 'green',
    "ABORTED": 'yellow',
    "WARNING": 'purple',
    "FAILED": 'red'
}
log_pattern = "%(asctime)s %(log_color)s%(levelname)s%(reset)s | %(name)s | %(log_color)s%(message)s"
formatter = colorlog.ColoredFormatter(log_pattern, log_colors=color_mapping)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger('harvest_wallet')
logger.addHandler(handler)
logger.setLevel(DEFAULT)

#  CONFIG PART
wallet_who_collect = os.getenv('NIBID_ADDR')  # put the address who should collectd
wallet_password = os.getenv('NIBID_ADDR_PASSWORD')  # put your password prompt
wallet_to_harvest_pattern = ['bern', 'douceur', 'harvest', 'lfdm', 'londre', 'oslow', 'prague', 'remote', 'rookie', 'yolo', 'chimera-alpha', 'lisbonne', 'madrid', 'paris', 'rome', 'vienne']
wallet_minimum_harvest = 25000  # minimal unibi to get
file_to_read = 'sample.yml'  # output file generated from nibib keys list > sample.yml
reroll_enabled = True  # This option allow to generate a file with address unused.
reroll = []
reroll_location = 'reroll.yml'
delete_enabled = True  # This option allow to generate a file with address unused.
delete = []
delete_location = 'delete.yml'

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
        logger.log(WARNING,
                   'Not gonna harvest {} | {}, not enought unibi minimun is set to {} unibi'.format(wallet_name,
                                                                                                    response[
                                                                                                        'address'],
                                                                                                    wallet_minimum_harvest))
        logger.log(SUCCESS, '{} | {} added to delete.yml'.format(response['address'], wallet_name))
        delete.append({'name': wallet_name, 'address': response['address']})
    return None


# This method run nibid tx
def fire_cmd(address, asset, amount):
    args = '/usr/local/bin/nibid tx bank send {} {} {}{} --fees 5000unibi --log_format json -y'.format(address,
                                                                                                       wallet_who_collect,
                                                                                                       amount,
                                                                                                       asset)
    logger.log(INFO, 'Gonna play {}'.format(args))
    process = subprocess.Popen([args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    if wallet_password != '':
        process.communicate(wallet_password)


def harvest_wallet(harvestable):
    fees = 5000
    for asset in harvestable['assets']:
        logger.log(DEFAULT,
                   'Gonna harvest {} from {} | {}'.format(asset, harvestable['wallet_name'], harvestable['address']))
        fire_cmd(harvestable['address'], asset, harvestable['assets'][asset])
        time.sleep(2)
        logger.log(DEFAULT, 'Wait 2 seconds between calls')
        fees = fees + 5000
    logger.log(INFO,
               'Gonna harvest {} from {} | {}'.format('unibi', harvestable['wallet_name'], harvestable['address']))
    fire_cmd(harvestable['address'], 'unibi', harvestable['unibi'] - fees)
    time.sleep(2)
    logger.log(DEFAULT, 'Wait 2 seconds between calls')


def get_wallet_amount(wallet_address, wallet_name):
    resp = requests.get('https://api.nibiru.exploreme.pro/accounts/{}'.format(wallet_address))
    if resp.status_code != 200:
        logger.log(ABORTED, '{} | {} not found on explorer'.format(wallet_address, wallet_name))
        if reroll_enabled:
            logger.log(SUCCESS, '{} | {} added to reroll.yml'.format(wallet_address, wallet_name))
            reroll.append({'name': wallet_name, 'address': wallet_address})
    return resp

# This is the main loop who harvest all wallet & all asset
def loop_wallet(wallets):
    for wallet in wallets:
        wallet_name = wallet['name']
        wallet_address = wallet['address']
        logger.log(INFO, 'Proceed {} | {}'.format(wallet_address, wallet_name))
        resp = get_wallet_amount(wallet_address, wallet_name)
        if resp.status_code != 200:
            continue
        harvestable = check_wallet_amount(resp.json(), wallet_name)
        if harvestable is None:
            logger.log(ABORTED, '{} | {} nothing to harvest'.format(wallet_address, wallet_name))
            continue
        logger.log(DEFAULT, 'Gonna harvest {}'.format(harvestable))
        harvest_wallet(harvestable)


if __name__ == '__main__':
    wallets_from_file = collect_wallet_info()
    loop_wallet(wallets_from_file)
    if reroll_enabled:
        logger.log(DEFAULT, 'dumping reroll to {}'.format(reroll_location))
        with open(reroll_location, 'w') as file:
            yaml.dump(reroll, file)
    if delete_enabled:
        logger.log(DEFAULT, 'dumping delete to {}'.format(delete_location))
        with open(delete_location, 'w') as file:
            yaml.dump(delete, file)