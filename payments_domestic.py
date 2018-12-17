from quicktest import *
from pydash import has,get

class PaymentsDomestic(AbstractTestCase):

    def setUp(self):
        self._payload = {
            "Data": {
                "Initiation": {
                    "InstructionIdentification": "ACME412",
                    "EndToEndIdentification": "FRESCO.21302.GFX.20",
                    "InstructedAmount": {
                        "Amount": "165.88",
                        "Currency": "GBP"
                    },
                    "CreditorAccount": {
                        "SchemeName": "UK.OBIE.SortCodeAccountNumber",
                        "Identification": "08080021325698",
                        "Name": "ACME Inc",
                        "SecondaryIdentification": "0002"
                    },
                    "RemittanceInformation": {
                        "Reference": "FRESCO-101",
                        "Unstructured": "Internal ops code 5120101"
                    }
                }
            },
            "Risk": {
                "PaymentContextCode": "EcommerceGoods",
                "MerchantCategoryCode": "5967",
                "MerchantCustomerIdentification": "053598653254",
                "DeliveryAddress": {
                    "AddressLine": [
                        "Flat 7",
                        "Acacia Lodge"
                    ],
                    "StreetName": "Acacia Avenue",
                    "BuildingNumber": "27",
                    "PostCode": "GU31 2ZZ",
                    "TownName": "Sparsholt",
                    "CountrySubDivision": [
                        "Wessex"
                    ],
                    "Country": "UK"
                }
            }
        }

    # Get Token
    def test_1(self):
        token_response = self.req.doTokenRequest(self.CLIENT_ID, scope="payments")
        PaymentsDomestic.token = get(token_response,'access_token')
        self.log.info("Retrieved Token %s", PaymentsDomestic.token)
        return PaymentsDomestic.token is not None

    # Do Payment Initiation
    def test_2(self):
        resp = self.req.doBasicRequest('/PaymentsAPI/v3.0.0/domestic-payment-consents', self._payload, PaymentsDomestic.token)
        PaymentsDomestic.ConsentId = get(resp, 'Data.ConsentId')
        self.log.info("Retrieved Consent %s", PaymentsDomestic.ConsentId)
        return PaymentsDomestic.ConsentId is not None

    # Build Auth URL
    def test_3(self):
        _token_payload = {
            "max_age": 86400,
            "aud": "{0}/token".format(self.URL),
            "scope": "payments openid",
            "iss": self.CLIENT_ID,
            "claims": {
                "id_token": {
                "acr": {
                    "values": [
                    "urn:openbanking:psd2:sca",
                    "urn:openbanking:psd2:ca"
                    ],
                    "essential": True
                },
                "openbanking_intent_id": {
                    "value": PaymentsDomestic.ConsentId,
                    "essential": True
                }
                },
                "userinfo": {
                "openbanking_intent_id": {
                    "value": PaymentsDomestic.ConsentId,
                    "essential": True
                }
                }
            },
            "response_type": "code id_token",
            "redirect_uri": self.REDIRECT_URL,
            "state": "YWlzcDozMTQ2",
            "nonce": "n-0S6_WzA2M",
            "client_id": self.CLIENT_ID
        }

        encodedJWT = self.jwt.encode(_token_payload)
        uri = "{0}/authorize/?response_type=code id_token&client_id={1}&scope={2} openid&redirect_uri={3}&request={4}".format(self.URL,self.CLIENT_ID,"payments",self.REDIRECT_URL,encodedJWT)
        
        print("\n\nAuth Url\n{0}\n".format(uri))
        return True

    # Get User Token
    def test_4(self):
        code = input("\n\nEnter Code: ")
        token_response = self.req.doTokenRequest(self.CLIENT_ID,code=code, scope="payments", grant="authorization_code", redirect_uri=self.REDIRECT_URL)
        PaymentsDomestic.token = get(token_response,'access_token')
        self.log.info("Retrieved User Token %s", PaymentsDomestic.token)
        return PaymentsDomestic.token is not None

    # Do Payment Submission
    def test_5(self):
        payload = self._payload
        payload["Data"]["ConsentId"] = PaymentsDomestic.ConsentId
        resp = self.req.doBasicRequest('/PaymentsAPI/v3.0.0/domestic-payment', self._payload, PaymentsDomestic.token)
        PaymentsDomestic.ConsentId = get(resp, 'Data.ConsentId')
        self.log.info("Retrieved Consent %s", PaymentsDomestic.ConsentId)
        return PaymentsDomestic.ConsentId is not None



        
       
        
