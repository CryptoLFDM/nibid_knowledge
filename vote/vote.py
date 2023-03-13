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
#wallet_to_harvest_pattern = ['berlin', 'vienne', 'paris', 'madrid', 'lisbonne']
wallet_to_harvest_pattern = [ 'bern', 'douceur', 'harvest', 'lfdm', 'londre', 'oslow', 'prague', 'remote', 'rookie', 'yolo', 'chimera-alpha', 'lisbonne', 'madrid', 'paris', 'rome', 'vienne']
wallet_minimum_harvest = 25000  # minimal unibi to get
file_to_read = 'sample.yml'  # output file generated from nibib keys list > sample.yml
reroll_enabled = True  # This option allow to generate a file with address unused.
reroll = []
reroll_location = 'reroll_rome.yml'


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

# This method run nibid tx
def fire_cmd_send(wallet):
    args = 'nibid tx bank send {} {} 100000unibi --fees 5000unibi -y'.format(wallet_who_collect, wallet)
    logger.log(INFO, 'Gonna play {}'.format(args))
    process = subprocess.Popen([args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    if wallet_password != '':
        process.communicate(wallet_password)

# This method run nibid tx
def fire_cmd(address):
    args = 'nibid tx gov vote 5 yes --from {} --chain-id nibiru-itn-1 --gas 500000 --fees 12500unibi -y'.format(address)
    logger.log(INFO, 'Gonna play {}'.format(args))
    process = subprocess.Popen([args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               universal_newlines=True,
                               shell=True)
    if wallet_password != '':
        process.communicate(wallet_password)


# This is the main loop who harvest all wallet & all asset
def loop_wallet(wallets):
    for wallet in wallets:
        wallet_name = wallet['name']
        wallet_address = wallet['address']
        fire_cmd_send(wallet_address)
        time.sleep(2)
        fire_cmd(wallet_name)
        logger.log(INFO, 'Proceed {} | {}'.format(wallet_address, wallet_name))
        #final_check(harvestable)


if __name__ == '__main__':
    wallets_from_file = collect_wallet_info()
    loop_wallet(wallets_from_file)
