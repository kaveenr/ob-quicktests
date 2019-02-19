import unittest
import random
import configparser
import logging
import urllib3
from colorama import init, Fore, Back, Style

from . import *

class AbstractTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print(Fore.GREEN + 'Setting Up Test Framework\nhttps://github.com/kaveenr/ob-quicktests\n' + Style.RESET_ALL)
        # Set Up Config
        config = configparser.ConfigParser()
        config.read('config.ini')
        # Set Up Logger
        logger = logging.getLogger(__class__.__name__)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('\n\n%(asctime)s - %(levelname)s -{0} %(message)s {1}\n'.format(Fore.YELLOW,Style.RESET_ALL))
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # Set Class Attributes
        cls.CLIENT_ID = config['App']['clientId']
        cls.REDIRECT_URL = config['App']['redirectUrl']
        cls.URL = config['Server']['host']
        cls.FINANCIAL_ID = config['Server']['financialId']

        cls.log = logger
        cls.tls = TLSHelper(config)
        cls.jwt = JWTHelper(cls.tls)
        cls.req = RequestUtils(cls.URL, config)