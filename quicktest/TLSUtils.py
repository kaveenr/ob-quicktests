import requests
import jwt
import logging
import hashlib
import time
import random
import urllib3
import configparser
import uuid

class TLSHelper:
    PUBLIC_KEY_PATH = None
    PRIVATE_KEY_PATH = None
    publicKey, privateKey = None, None
    thumbprint = None

    def __init__(self, config):
        self.PUBLIC_KEY_PATH, self.PRIVATE_KEY_PATH = config['MTLS']['publicKey'], config['MTLS']['privateKey']
        self.publicKey, self.privateKey = self.loadCerts(self.PUBLIC_KEY_PATH, self.PRIVATE_KEY_PATH)
    
    def loadCerts(self, pub, priv):
        p_cert, pk_cert = None, None
        with open(pub, 'r') as f:
            p_cert = f.read()
        with open(priv, 'r') as f:
            pk_cert = f.read()
        
        return p_cert, pk_cert

    def getCertificates(self):
        return (self.publicKey, self.privateKey)

    def getPrivate(self):
        return self.privateKey

    def calculateThumbprint(self):
        h = hashlib.sha1()
        with open(self.PUBLIC_KEY_PATH, 'rb') as crt:
            h.update(crt.read())
            cert_hash = h.hexdigest()
        return cert_hash

