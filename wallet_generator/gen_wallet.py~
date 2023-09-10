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
file_to_read = 'wallet.yml'  # output file generated from nibib keys list > sample.yml
whitelist = ['yolo', 'douceur', 'douceur_1', 'chimera-delta', 'chimera-alpha']

def collect_wallet_info():
    stream = open(file_to_read, 'r')  # 'document.yaml' contains a single YAML document.
    nibid_wallet = yaml.safe_load(stream)
    return nibid_wallet

# This method run nibid tx
def fire_cmd(name):
    args = '/usr/local/bin/nibid keys delete {} -y'.format(name)
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
        if wallet['name'] not in whitelist:
            logger.log(INFO, 'Delete {}'.format(wallet['name']))
            fire_cmd(wallet['name'])
        else:
            logger.log(INFO, 'Skip {} for whitelist protection'.format(wallet['name']))


if __name__ == '__main__':
    wallets_from_file = collect_wallet_info()
    loop_wallet(wallets_from_file)
