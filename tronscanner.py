import json
import requests
import sys

class TronScan(object):
    API_URL_BASE = "https://apilist.tronscan.org/api/"

    TRANSFER_PATH = "transfer"
    TRANSFER_PARAMS = { 'address' : 'address=',
                        'tstamp_start' : 'start_timestamp=',
                        'tstamp_end' : 'end_timestamp=',
                        'limit' : 'limit=',
                        'start_index' : 'start=' }

    TRANSACTION_PATH = "transaction"
    TRANSACTION_PARAMS = { 'address' : 'address=',
                           'tstamp_start' : 'start_timestamp=',
                           'tstamp_end' : 'end_timestamp',
                           'limit' : 'limit=',
                           'start_index' : 'start=' }
    PAGE_LIMIT = 50
    

    def __init__(self, wallet_address):
        self.wallet_address = wallet_address

    def __request_api(self, path, req_param):
        try:
            response = requests.get(self.API_URL_BASE + path, params=req_param, timeout=3)
        except requests.exceptions.Timeout:
            print("Request " + self.API_URL_BASE + " TIMEOUT!")
            return None

        if response.status_code == 200:
            js = json.loads(response.content.decode('utf-8'))
            return js
        return None

    def get_all_transfers(self):
        param = self.TRANSFER_PARAMS['address'] + self.wallet_address + '&' + self.TRANSFER_PARAMS['limit'] + '1'
        js = self.__request_api(self.TRANSFER_PATH, param)
        total = js['total']
        print("Total count of transfers to receive: " + str(total))

        max_index = int(total / self.PAGE_LIMIT)
        param = self.TRANSFER_PARAMS['address'] + self.wallet_address + '&' + \
                self.TRANSFER_PARAMS['limit'] + str(self.PAGE_LIMIT) + '&' + \
                self.TRANSFER_PARAMS['start_index']

        data = {'total' : total, 'data' : []}
        sys.stdout.write("\r0%")
        for i in range(0, max_index + 1):
            js = self.__request_api(self.TRANSFER_PATH, param + str(i * self.PAGE_LIMIT))
            data['data'].extend(js['data'])
            progress = ((i + 1) / (max_index + 1)) * 100
            sys.stdout.write("\r%d%%" % progress)

        data_len = len(data['data'])
        data['total'] = data_len
        print('\n' + str(data_len) + ' transfers received.')
        return data

    def get_all_transactions(self):
        param = self.TRANSACTION_PARAMS['address'] + self.wallet_address + '&' + self.TRANSACTION_PARAMS['limit'] + '1'
        js = self.__request_api(self.TRANSACTION_PATH, param)
        total = js['total']
        print("Total count of transcations to receive: " + str(total))

        max_index = int(total / self.PAGE_LIMIT)
        param = self.TRANSACTION_PARAMS['address'] + self.wallet_address + '&' + \
                self.TRANSACTION_PARAMS['limit'] + str(self.PAGE_LIMIT) + '&' + \
                self.TRANSACTION_PARAMS['start_index']

        data = {'total' : total, 'data' : []}
        sys.stdout.write("\r0%")
        for i in range(0, max_index + 1):
            js = self.__request_api(self.TRANSACTION_PATH, param + str(i * self.PAGE_LIMIT))
            data['data'].extend(js['data'])
            progress = ((i + 1) / (max_index + 1)) * 100
            sys.stdout.write("\r%d%%" % progress)

        data_len = len(data['data'])
        data['total'] = data_len
        print('\n' + str(data_len) + ' transcations received.')
        return data

            