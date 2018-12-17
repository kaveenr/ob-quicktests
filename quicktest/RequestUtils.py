import requests
import jwt
import logging
import hashlib
import time
import random
import urllib3
import configparser
import uuid

class RequestUtils:
    url, certs = None, None
    noverbose = [200,201]

    def __init__(self, url, config):
        self.url = url
        cert_paths = PUBLIC_KEY_PATH, PRIVATE_KEY_PATH = config['MTLS']['publicKey'], config['MTLS']['privateKey']
        self.FINANCIAL_ID = config['Server']['financialId']
        self.certs = cert_paths

    def getStandardHeaders(self, token):
        return {
            "x-fapi-financial-id" : self.FINANCIAL_ID,
            "x-idempotency-key" : str(uuid.uuid1()),
            "Authorization" : "Bearer {0}".format(token)
        }
    
    def doTokenRequest(self, client_id, scope, code=None, grant="client_credentials", redirect_uri=None):
        payload = {
            "grant_type" : grant,
            "scope" : scope,
            "client_id" : client_id
        }

        if (code):
            payload["code"] = code
        if (redirect_uri):
            payload["redirect_uri"] = redirect_uri
        
        req = requests.post('{0}/token'.format(self.url), data=payload , cert=self.certs, verify=False)
        #req = self.doBasicRequest('/token', payload)
        return req.json()

    def doBasicRequest(self, url, payload, token=None):
        if token:
            headers = self.getStandardHeaders(token=token)
        else:
            headers = {}
        req = requests.post('{0}{1}'.format(self.url,url), json=payload , cert=self.certs, headers=headers, verify=False)
        if req.status_code not in self.noverbose:
            print('\n########## {0} - {1}'.format(req.status_code, url))
            print('**********\n{0}\n*************'.format(req.content))
        return req.json()
