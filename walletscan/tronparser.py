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
    """Class of a transfer in the Tron Network."""

    def __init__(self, transfer_dict = None):
        if transfer_dict is None:
            self.id = None
            self.block = None
            self.transaction_hash = None
            self.timestamp = None
            self.from_address = None
            self.to_address = None
            self.amount = None
            self.token_name = None
            self.confirmed = None
            self.data = None
        else:
            self.id = transfer_dict['id']
            self.block = int(transfer_dict['block'])
            self.transaction_hash = transfer_dict['transactionHash']
            self.timestamp = int(transfer_dict['timestamp'])
            self.from_address = transfer_dict['transferFromAddress']
            self.to_address = transfer_dict['transferToAddress']
            self.amount = int(transfer_dict['amount'])
            self.token_name = str(transfer_dict['tokenName'])
            self.confirmed = transfer_dict['confirmed']
            if not self.confirmed:
                print("Warning: Transfer " + self.id + " is not confirmed!")
            self.data = transfer_dict['data']

        self.comment = ''

    def get_date(self, timezone = 'Europe/Berlin', date_format = '%Y-%m-%d %H:%M:%S'):
        """Converts the timestamp of transfer in a date.
        
        Keyword Arguments:
            timezone {str} -- Timezone. (default: {'Europe/Berlin'})
            date_format {str} -- Format of the date. (default: {'%Y-%m-%d %H:%M:%S'})
        
        Returns:
            str -- Date.
        """
        ts = self.timestamp / 1000
        tz = pytz.timezone(timezone)
        dt = datetime.fromtimestamp(ts, tz)
        return dt.strftime(date_format)

    @staticmethod
    def parse_transfers(transfer_dict):
        """Parse transfers to a list of TronTransfer objects.
        
        Arguments:
            transfer_dict {dict} -- Transfers.
        
        Returns:
            [TronTransfer] -- List of TronTransfer objects.
        """

        transfers = []

        for i in range(0, transfer_dict['total']):
            transfers.append(TronTransfer(transfer_dict['data'][i]))

        return transfers


class TronTransaction(object):
    """Class of a transactions in the Tron Network."""

    def __init__(self, transaction_dict):
        self.block = int(transaction_dict['block'])
        self.hash = transaction_dict['hash']
        self.timestamp = int(transaction_dict['timestamp'])
        self.owner_address = transaction_dict['ownerAddress']
        self.contract_type = ContractType(transaction_dict['contractType'])
        self.to_address = transaction_dict['toAddress']
        self.contract_data = TronContract(self.contract_type, transaction_dict['contractData'])
        self.smart_calls = transaction_dict['SmartCalls']
        self.events = transaction_dict['Events']
        self.id = transaction_dict['id']
        self.confirmed = transaction_dict['confirmed']
        if not self.confirmed:
            print("Warning: Transaction " + self.id + " is not confirmed!")
        self.data = transaction_dict['data']
        self.fee = transaction_dict['fee']

    def get_date(self, timezone = 'Europe/Berlin', date_format = '%Y-%m-%d %H:%M:%S'):
        """Converts the timestamp of transaction in a date.
        
        Keyword Arguments:
            timezone {str} -- Timezone. (default: {'Europe/Berlin'})
            date_format {str} -- Format of the date. (default: {'%Y-%m-%d %H:%M:%S'})
        
        Returns:
            str -- Date.
        """

        ts = self.timestamp / 1000
        tz = pytz.timezone(timezone)
        dt = datetime.fromtimestamp(ts, tz)
        return dt.strftime(date_format)

    @staticmethod
    def parse_transactions(transaction_dict):
        """Parse transactions to a list of TronTransaction objects.
        
        Arguments:
            transaction_dict {dict} -- Tratransactionsnsfers.
        
        Returns:
            [TronTransaction] -- List of TronTransaction objects.
        """

        transaction = []

        for i in range(0, transaction_dict['total']):
            transaction.append(TronTransaction(transaction_dict['data'][i]))

        return transaction
    
class TronVote(object):
    """Class of vote informations."""

    def __init__(self, vote_dict):    
        self.vote_address = vote_dict['vote_address']
        self.vote_count = vote_dict['vote_count']

    @staticmethod
    def parse_votes(votes_list):
        """Parse the votes from a list of json.
        
        Arguments:
            votes_list {[json]} -- List of votes.
        
        Returns:
            [TronVote] -- List of TronVote objects.
        """

        votes = []

        for v in votes_list:
            votes.append(TronVote(v))

        return votes

class TronContract(object):
    """Contract informations of a transaction."""

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
        
        
        
