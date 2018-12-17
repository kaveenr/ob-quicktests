import requests
import jwt
import logging
import hashlib
import time
import random
import urllib3
import configparser
import uuid

class JWTHelper:
    tlsHelper = None

    def __init__(self, tlsHelper):
        self.tls = tlsHelper
    
    def encode(self, payload):
        additional_headers = {
            "kid" : self.tls.calculateThumbprint()
        }

        raw_jwt =  jwt.encode(payload, self.tls.getPrivate() , algorithm='RS256', headers=additional_headers)
        encodedJWT = raw_jwt.decode("utf-8")
        return encodedJWT

