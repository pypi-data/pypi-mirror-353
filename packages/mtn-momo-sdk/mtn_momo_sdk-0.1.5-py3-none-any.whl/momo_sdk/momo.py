
import requests, json, base64
import uuid

class Momo:
    def __init__(self, api_user, api_key, subscription_key, mode=None, callback_url=None):
        self.api_user = api_user
        self.api_key = api_key
        self.subscription_key = subscription_key 
        self.mode = mode 
        if self.mode == 'development':
            self.url = 'https://sandbox.momodeveloper.mtn.com'
            self.callback_url = callback_url
        else:
            self.url = 'https://proxy.momoapi.mtn.com'
            self.callback_url = callback_url

    def get_url(self):
        return self.url

    def get_api_user(self):
        return self.api_user

    def get_api_key(self):
        return self.api_key

    def get_subscription_key(self):
        return self.subscription_key

    def get_env(self):
        if 'sandbox' in self.url:
            return 'sandbox'
        else:
            return 'mtnuganda'

    def get_callback(self):
        return self.callback_url 

    def encode_token(self):
        txt = "{}:{}".format(self.api_user, self.api_key)
        encodedBytes = base64.b64encode(txt.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")
        return encodedStr

    def get_live_token(self):
        url = "{}/collection/token/".format(self.url)
        payload = ""
        headers = {
            'Ocp-Apim-Subscription-Key': '{}'.format(self.subscription_key),
            'Authorization': 'Basic {}'.format(self.encode_token()),
            'X-Target-Environment': 'mtnuganda'
        }
        response = requests.post(url, headers=headers, data=payload)
        if 'access_token' in response.text:
            return response.json()['access_token']
        else:
            return response.json()

    def get_token(self):
        url = "{}/collection/token/".format(self.url)
        payload = ""
        headers = {
            'Ocp-Apim-Subscription-Key': '{}'.format(self.subscription_key),
            'Authorization': 'Basic {}'.format(self.encode_token()),
            'X-Target-Environment': 'sandbox'
        }
        response = requests.post(url, headers=headers, data=payload)
        if 'access_token' in response.text:
            return response.json()['access_token']
        else:
            return response.json()

    def get_accountholder(self, ac_msisdn):
        ac_type = 'msisdn'
        url = "{}/collection/v1_0/accountholder/{}/{}/active".format(self.url, ac_type, ac_msisdn)
        headers = {
            'Authorization': 'Bearer {}'.format(self.get_token()),
            'X-Target-Environment': str(self.get_env()),
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': '{}'.format(self.subscription_key),
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def deposit_money(self, msisdn, amount, reference, payer_message=None, payee_note=None):
        url = "{}/collection/v1_0/requesttopay".format(self.url)
        tkn = self.get_token() if self.mode == 'development' else self.get_live_token()
        headers = {
            'Authorization': 'Bearer {}'.format(tkn),
            'X-Reference-Id': str(reference),
            'X-Target-Environment': str(self.get_env()),
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': '{}'.format(self.subscription_key),
        }
        if self.mode != 'development':
            headers['X-Callback-Url'] = self.callback_url
        currency = "EUR" if self.mode == 'development' else "UGX"
        payload = json.dumps({
            "amount": amount,
            "currency": currency,
            "externalId": str(reference),
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": str(msisdn)
            },
            "payerMessage": payer_message if payer_message else "MTN Collection",
            "payeeNote": payee_note if payee_note else "MTN Collection",
        })
        response = requests.post(url, headers=headers, data=payload)
        with open("mtn_deposit_transaction_log.txt", "a") as log_file:
            log_file.write("Collection Request:\n")
            log_file.write(f"URL: {url}\n")
            log_file.write(f"Headers: {json.dumps(headers, indent=4)}\n")
            log_file.write(f"Payload: {payload}\n")
            log_file.write("\nResponse:\n")
            log_file.write(f"Status Code: {response.status_code}\n")
            log_file.write(f"Response Body: {response.text}\n")
            log_file.write("-" * 80 + "\n")
        result = {'status_code': response.status_code, 'trans_id': reference}
        return json.dumps(result)

    def get_transaction(self, reference):
        url = "{}/collection/v1_0/requesttopay/{}".format(self.url, reference)
        headers = {
            'Authorization': 'Bearer {}'.format(self.get_token()),
            'X-Target-Environment': str(self.get_env()),
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': '{}'.format(self.subscription_key),
        }
        response = requests.get(url, headers=headers)
        with open("mtn_check_transaction_log.txt", "a") as log_file:
            log_file.write("Checking Transaction Request:\n")
            log_file.write(f"URL: {url}\n")
            log_file.write(f"Headers: {json.dumps(headers, indent=4)}\n")
            log_file.write("\nResponse:\n")
            log_file.write(f"Status Code: {response.status_code}\n")
            log_file.write(f"Response Body: {response.text}\n")
            log_file.write("-" * 80 + "\n")
        return response.json()
