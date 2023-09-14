import logging
import subprocess
import time
import os
import json

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
wallet_blacklist = ['douceur', 'yolo', 'chimera']
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
        for pattern in wallet_blacklist:
            if pattern not in line['name']:
                wallets.append({'name': line['name'], 'address': line['address']})
                continue
    return wallets


def delete_wallet(name: str):
    args = 'nibiru --home /opt/chimera/nibiru keys delete {} -y'.format(name)
    logger.log(INFO, 'Gonna play {}'.format(args))
    process = subprocess.Popen([args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    if wallet_password != '':
        stdout, stderr = process.communicate(wallet_password)
        print(stdout, stderr)
    process = subprocess.Popen(["echo", "cleanup"],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    stdout, stderr = process.communicate()
    print(stdout, stderr)

def collect_wallet_by_denom(address: str, asset: str, amount: float):
    args = 'nibiru --home /opt/chimera/nibiru tx bank send {} {} {}{} --fees 5000unibi --log_format json -y'.format(address,
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
        stdout, stderr = process.communicate(wallet_password)
        print(stdout, stderr)
    process = subprocess.Popen(["echo", "cleanup"],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    stdout, stderr = process.communicate()
    print(stdout, stderr)
    
def harvest_wallet(address: str, name: str, wallet: dict):
    unibi = 0
    uusdt = 0
    unusd = 0
    for coin in wallet['balances']:
        if coin['denom'] == 'unibi':
            unibi = float(coin['amount'])
        elif coin['denom'] == 'unusd':
            unusd = float(coin['amount'])
        elif coin['denom'] == 'uusdt':
            uusdt = float(coin['amount'])
    if unusd > 0:
        collect_wallet_by_denom(address, 'unusd', unusd)
    if uusdt > 0:
        collect_wallet_by_denom(address, 'uusdt', uusdt)
    if unibi > 16000:
        collect_wallet_by_denom(address, 'unibi', (unibi - 15000.0))
#    if unibi > 0 and unibi < 4500:
#        delete_wallet(name)
    
        
# This method run nibid tx
def fire_cmd(address, name):
    harvestable = {}
    save = 0
    args = 'nibiru query  bank balances {}'.format(address)
    with subprocess.Popen([args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               shell=True, text=True) as process:
        stdout, stderr = process.communicate()

        
        parsed_dicts = yaml.safe_load(stdout)
        if len(parsed_dicts['balances']) > 0:
               harvest_wallet(address, name, parsed_dicts)


                
# This is the main loop who harvest all wallet & all asset
def loop_wallet(wallets):
    for wallet in wallets:
        wallet_name = wallet['name']
        wallet_address = wallet['address']
        fire_cmd(wallet_address, wallet_name)


if __name__ == '__main__':
    wallets_from_file = collect_wallet_info()
    loop_wallet(wallets_from_file)
