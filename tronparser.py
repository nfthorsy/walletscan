import json
import pytz
from enum import Enum 
from datetime import datetime

class ContractType(Enum):
        AccountCreate = 0
        Transfer = 1
        TransferAsset = 2
        VoteAsset = 3
        VoteWitness = 4
        WitnessCreate = 5
        AssetIssue = 6
        Deploy = 7
        WitnessUpdate = 8
        ParticipateAssetIssue = 9
        Freeze = 11
        Unfreeze = 12

class TronTransfer(object):
    def __init__(self, transfer_dict = None):
        if transfer_dict is None:
            self.id = None
            self.block = None
            self.transactionHash = None
            self.timestamp = None
            self.transferFromAddress = None
            self.transferToAddress = None
            self.amount = None
            self.tokenName = None
            self.confirmed = None
            self.data = None
        else:
            self.id = transfer_dict['id']
            self.block = int(transfer_dict['block'])
            self.transactionHash = transfer_dict['transactionHash']
            self.timestamp = int(transfer_dict['timestamp'])
            self.transferFromAddress = transfer_dict['transferFromAddress']
            self.transferToAddress = transfer_dict['transferToAddress']
            self.amount = int(transfer_dict['amount'])
            self.tokenName = str(transfer_dict['tokenName'])
            self.confirmed = transfer_dict['confirmed']
            if not self.confirmed:
                print("Warning: Transfer " + self.id + " is not confirmed!")
            self.data = transfer_dict['data']

    def get_date(self, timezone = 'Europe/Berlin', date_format = '%Y-%m-%d %H:%M:%S'):
        ts = self.timestamp / 1000
        tz = pytz.timezone(timezone)
        dt = datetime.fromtimestamp(ts, tz)
        return dt.strftime(date_format)

    @staticmethod
    def parse_transfers(transfer_dict):
        transfers = []

        for i in range(0, transfer_dict['total']):
            transfers.append(TronTransfer(transfer_dict['data'][i]))

        return transfers


class TronTransaction(object):
    def __init__(self, transaction_dict):
        self.block = int(transaction_dict['block'])
        self.hash = transaction_dict['hash']
        self.timestamp = int(transaction_dict['timestamp'])
        self.ownerAddress = transaction_dict['ownerAddress']
        self.contractType = ContractType(transaction_dict['contractType'])
        self.toAddress = transaction_dict['toAddress']
        self.confirmed = transaction_dict['confirmed']
        if not self.confirmed:
            print('Not confirmed: ' + self.hash)
        self.contractData = TronContract(self.contractType, transaction_dict['contractData'])
        self.smartCalls = transaction_dict['SmartCalls']
        self.events = transaction_dict['Events']
        self.id = transaction_dict['id']
        self.data = transaction_dict['data']
        self.fee = transaction_dict['fee']

    def get_date(self, timezone = 'Europe/Berlin', date_format = '%Y-%m-%d %H:%M:%S'):
        ts = self.timestamp / 1000
        tz = pytz.timezone(timezone)
        dt = datetime.fromtimestamp(ts, tz)
        return dt.strftime(date_format)

    @staticmethod
    def parse_transactions(transaction_dict):
        transaction = []

        for i in range(0, transaction_dict['total']):
            transaction.append(TronTransaction(transaction_dict['data'][i]))

        return transaction
    
class TronVote(object):
    def __init__(self, vote_dict):    
        self.vote_address = vote_dict['vote_address']
        self.vote_count = vote_dict['vote_count']

    @staticmethod
    def parse_votes(votes_list):
        votes = []

        for v in votes_list:
            votes.append(TronVote(v))

        return votes

class TronContract(object):
    def __init__(self, ctype : ContractType, contract_dict):
        self.owner_address = contract_dict['owner_address']

        # Transfer
        if ctype == ContractType.Transfer:
            self.asset_name = '_'
            self.to_address = contract_dict['to_address']
            self.amount = int(contract_dict['amount'])

        # TransferAsset
        elif ctype == ContractType.TransferAsset:
            self.asset_name = contract_dict['asset_name']
            self.to_address = contract_dict['to_address']
            self.amount = int(contract_dict['amount'])

        # Freeze
        elif ctype == ContractType.Freeze:
            self.frozen_duration = int(contract_dict['frozen_duration'])
            self.frozen_balance = int(contract_dict['frozen_balance'])

        # Unfreeze
        elif ctype == ContractType.Unfreeze:
            pass

        # VoteWitness
        elif ctype == ContractType.VoteWitness:
            self.votes = TronVote.parse_votes(contract_dict['votes'])

        # Else
        else:
            print(ctype)
            self.asset_name = contract_dict['asset_name']
            self.to_address = contract_dict['to_address']
            self.amount = int(contract_dict['amount'])
        
        
        
