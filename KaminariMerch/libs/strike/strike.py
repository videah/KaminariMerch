from requests import post, get
from requests.auth import HTTPBasicAuth
import json


class Strike(object):

    def __init__(self, api_key):

        self.api_key = api_key
        self.endpoint = "https://api.dev.strike.acinq.co/api/v1"

    def _request(self, method, url, data=None):

        if method == 'POST':
            response = post(self.endpoint + url, auth=HTTPBasicAuth(self.api_key, ''), data=data)
        elif method == 'GET':
            response = get(self.endpoint + url, auth=HTTPBasicAuth(self.api_key, ''))
        else:
            response = 'ERROR'  # TODO: This is makeshift error handling, do it properly.

        if response.ok:
            return json.loads(response.content)

    def create_charge(self, amount, currency='btc', description='A Lightning Payment'):

        data = {
            'amount': amount,
            'currency': currency,
            'description': description,
        }

        return self._request('POST', '/charges', data)

    def list_charges(self, page=0, size=30):
        return self._request('GET', '/charges?page=' + str(page) + '&size=' + str(size))

    def get_charge(self, charge_id):
        return self._request('GET', '/charges/' + charge_id)
