import requests
import jwt
import logging
import hashlib
import time
import random
import urllib3
import configparser
import uuid
from colorama import init, Fore, Back, Style
import pprint
import json

class RequestUtils:
    url, certs = None, None
    noverbose = [200,201]

    def __init__(self, url, config):
        self.url = url
        cert_paths = PUBLIC_KEY_PATH, PRIVATE_KEY_PATH = config['MTLS']['publicKey'], config['MTLS']['privateKey']
        sig_cert_paths = PUBLIC_KEY_PATH, PRIVATE_KEY_PATH = config['Signing']['publicKey'], config['Signing']['privateKey']
        self.FINANCIAL_ID = config['Server']['financialId']
        self.certs = cert_paths
        self.sig_certs = sig_cert_paths

    def getStandardHeaders(self, token):
        return {
            "x-fapi-financial-id" : self.FINANCIAL_ID,
            "x-idempotency-key" : str(uuid.uuid1()),
            "Authorization" : "Bearer {0}".format(token),
            "Content-Type" : "application/json"
        }

    def signJWS(self, payload):
        cfile = open(self.sig_certs[1])
        try:
            return jwt.encode(payload, cfile.read(), algorithm='RS256').decode("utf-8")
        finally:
            cfile.close()

    def getJwsSignature(self, payload):
        cfile = open(self.sig_certs[1])
        sig = None
        addit_headers = {
            "kid": "",
            "b64": False,
            "http://openbanking.org.uk/iat": 1549900962,
            "http://openbanking.org.uk/iss": "",
            "http://openbanking.org.uk/tan": "openbanking.org.uk",
            "crit": [ "b64", "http://openbanking.org.uk/iat", "http://openbanking.org.uk/iss", "http://openbanking.org.uk/tan"]
        }

        try:
            jws = jwt.encode(payload, cfile.read(), algorithm='RS256', headers=addit_headers)
            print(jws.decode("utf-8"))
            stripped_jws = jws.decode("utf-8").split(".")
            stripped_jws[1] = ""
            sig = ".".join(stripped_jws)
        finally:
            cfile.close()

        return sig

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
            headers["x-jws-signature"] = self.getJwsSignature(payload)
        else:
            headers = {}

        json_payload = json.dumps(
            payload,
            separators=(',', ':'),
        ).encode('utf-8')
        req = requests.post('{0}{1}'.format(self.url,url), data=json_payload , cert=self.certs, headers=headers, verify=False)
        #if req.status_code not in self.noverbose:
        if True:
            print('\n\n{0}{1} - {2}'.format(Fore.BLUE,req.status_code, url))
            print(Back.WHITE)
            print('{0}'.format(pprint.pprint(payload)))
            if req.status_code in self.noverbose:
                print('\n{0}\n'.format(pprint.pprint(req.json())))
            else:
                print('\n{0}\n'.format(req.content))
            print(Style.RESET_ALL)
        return req.json()
