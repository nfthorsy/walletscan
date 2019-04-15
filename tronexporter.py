from enum import Enum 
import tronparser
import tronscanner

class CTTransferType(Enum):
        Einzahlung = 'Einzahlung'
        Einnahmen = 'Einnahmen'
        Mining = 'Mining'
        Geschenk = 'Geschenk'
        Auszahlung = 'Auszahlung'
        Ausgabe = 'Ausgabe'
        Spende = 'Spende'
        Schenkung = 'Schenkung'
        Gestohlen = 'Gestohlen'
        Verlust = 'Verlust'


class CoinTrackingExporter(object):

    def __init__(self, wallet_address, wallet_name = None):
        self.wallet_address = wallet_address
        self.wallet_name = wallet_name
        self.assignments = []
        self.groups = []

    def add_assign(self, transfer_type : CTTransferType, from_address = None, to_address = None):
        """
        Adds transfer assignments. Transfers are assigned to specific transfer types based on the assignment. 
        Without assignment, transfers will be declared as deposits or withdrawals.
        
        Arguments:
            transfer_type {CTTransferType} -- Type which will be assigned to the transfers.
        
        Keyword Arguments:
            from_address {str} -- Affected transfers with this sender address. (default: {None})
            to_address {str} -- Affected transfers with this destination address. (default: {None})
        """

        if from_address is None and to_address is None:
            print('Either sender address or destination address must be set.')
            return

        self.assignments.append({'transfer_type' : transfer_type, 'from_address' : from_address, 'to_address' : to_address})

    def add_group(self, currency : str, from_address = None, to_address = None):
        """
        Adds transfers from specific senders or receivers to a group. Grouped transfers are merged into one transfer when exported.
        
        Keyword Arguments:
            currency {str} -- Currencies which will be grouped together.
            from_address {str} -- Affected transfers with this sender address. (default: {None})
            to_address {str} -- Affected transfers with this destination address. (default: {None})
        """

        if from_address is None and to_address is None:
            print('Either sender address or destination address must be set.')
            return

        self.groups.append({'currency' : currency, 'from_address' : from_address, 'to_address' : to_address})

    def _group_transfers(self, transfers : [tronparser.TronTransfer]):
        if not self.groups:
            return {}, transfers

        sorted_tr = sorted(transfers, key = lambda x: x.timestamp)

        grouped_tr = {}
        ungrouped_tr = []
        new_group_currenys = []
        for g in self.groups:
            for t in sorted_tr:
                if g['currency'] == t.tokenName:
                             
                    # deposit
                    if g['from_address'] is not None and g['from_address'] == t.transferFromAddress:
                        if t.tokenName not in grouped_tr:
                            grouped_tr[t.tokenName] = {'count' : 0, 'groups' : []}

                        if grouped_tr[t.tokenName]['count'] == 0:
                            grouped_tr[t.tokenName]['groups'].append({'is_outgoing' : False, 'transfers' : []})
                            grouped_tr[t.tokenName]['count'] = 1

                        group_index = grouped_tr[t.tokenName]['count'] - 1
                        if grouped_tr[t.tokenName]['groups'][group_index]['is_outgoing'] or t.tokenName in new_group_currenys:
                            grouped_tr[t.tokenName]['groups'].append({'is_outgoing' : False, 'transfers' : []})
                            grouped_tr[t.tokenName]['count'] += 1 
                            group_index = grouped_tr[t.tokenName]['count'] - 1
                            if t.tokenName in new_group_currenys: new_group_currenys.remove(t.tokenName)

                        grouped_tr[t.tokenName]['groups'][group_index]['transfers'].append(t)

                    # withdrawal
                    elif g['to_address'] is not None and g['to_address'] == t.transferToAddress:
                        if t.tokenName not in grouped_tr:
                            grouped_tr[t.tokenName] = {'count' : 0, 'groups' : []}

                        if grouped_tr[t.tokenName]['count'] == 0:
                            grouped_tr[t.tokenName]['groups'].append({'is_outgoing' : True, 'transfers' : []})
                            grouped_tr[t.tokenName]['count'] = 1

                        group_index = grouped_tr[t.tokenName]['count'] - 1
                        if grouped_tr[t.tokenName]['groups'][group_index]['is_outgoing'] or t.tokenName in new_group_currenys:
                            grouped_tr[t.tokenName]['groups'].append({'is_outgoing' : True, 'transfers' : []})
                            grouped_tr[t.tokenName]['count'] += 1 
                            group_index = grouped_tr[t.tokenName]['count'] - 1
                            if t.tokenName in new_group_currenys: new_group_currenys.remove(t.tokenName)

                        grouped_tr[t.tokenName]['groups'][group_index]['transfers'].append(t)

                    else:
                        if t.tokenName in grouped_tr and t.tokenName not in new_group_currenys:
                            new_group_currenys.append(t.tokenName)
                            
                        ungrouped_tr.append(t)

        groups = []
        for _, value in grouped_tr.items():
            for g in value['groups']:
                groups.append(g['transfers'])

        return groups, ungrouped_tr

    def _merge_transfers(self, transfers : [tronparser.TronTransfer]):
        """
        Merges grouped transfers into one transfer. Transfers with different currencies will be not merged. 
        Groups can be created with the "add_group()" function.
        
        
        Arguments:
            transfers {[tronparser.TronTransfer]} -- List of TronTransfer
        """

        if not self.groups:
            return transfers

        groups, trs = self._group_transfers(transfers)

        for g in groups:
            transfer = tronparser.TronTransfer()
            transfer.amount = 0
            transfer.transferFromAddress = g[0].transferFromAddress
            transfer.transferToAddress = g[0].transferToAddress
            transfer.tokenName = g[0].tokenName
            transfer.confirmed = True

            for t in g:
                transfer.timestamp = t.timestamp
                transfer.amount += t.amount
                transfer.confirmed &= g[0].confirmed

            trs.append(transfer)

        trs.sort(key = lambda x: x.timestamp)

        return trs

    def export_csv(self, filename: str):
        """
        Fetches the transfers from the wallet and exports them to a csv file.
        
        Arguments:
            filename {str} -- Destination file.
        """

        print("Fetching transfers from tronscan.org API ...")
        scanner = tronscanner.TronScan(self.wallet_address)
        transfers = scanner.get_all_transfers()
        ptr = tronparser.TronTransfer.parse_transfers(transfers)
        print("Fetching success.")

        if self.groups:
            print("Mergin grouped transfers ...")
            ptr = self._merge_transfers(ptr)
            print("Mergin success.")

        print("Writing CSV for CoinTracking.info ...")
        
        with open(filename, 'w') as csvf:
            # "Typ","Kauf","Cur.","Verkauf","Cur.","Gebühr","Cur.","Börse","Gruppe","Kommentar","Datum"

            csvf.write(r'"Typ","Kauf","Cur.","Verkauf","Cur.","Gebühr","Cur.","Börse","Gruppe","Kommentar","Datum"' + '\n')

            for tr in ptr:
                line = ''
                has_assign = False
                tr_type = CTTransferType('Einzahlung')

                # Type
                for assign in self.assignments:
                    if tr.transferFromAddress == assign['from_address'] or tr.transferToAddress == assign['to_address']:
                        tr_type = assign['transfer_type']
                        has_assign = True
                        break

                if not has_assign:
                    if tr.transferToAddress == self.wallet_address:
                        tr_type = CTTransferType.Einzahlung

                    elif tr.transferFromAddress == self.wallet_address:
                        tr_type = CTTransferType.Auszahlung

                    else:
                        print('Something went wrong.')
                        exit()
                
                line += '\"' + tr_type.value + '\",'

                amount = 0
                cur = ''

                if tr.tokenName == '_':
                    # 3754437233 = 3,754.437233 TRX
                    amount = tr.amount / 1000000
                    cur = 'TRX'
                else:
                    amount = tr.amount
                    # ToDo: Currency value to str
                    cur = tr.tokenName

                if tr_type.value == CTTransferType.Einzahlung.value or \
                   tr_type.value == CTTransferType.Einnahmen.value or \
                   tr_type.value == CTTransferType.Mining.value or \
                   tr_type.value == CTTransferType.Geschenk.value:

                    # Buy
                    line += '\"' + str(amount) + '\",\"' + cur + '\",'
                    
                    # Sell
                    line += r'"","",'

                else:
                    # Buy
                    line += r'"","",'

                    # Sell
                    line += '\"' + str(amount) + '\",\"' + cur + '\",'


                # ToDo: Fee 
                line += r'"","",'

                # Exchange
                line += '\"' + '' if self.wallet_name is None else self.wallet_name + '\",'

                # Group
                line += r'"",'

                # Comment
                line += r'"",'

                # Date
                # ToDo: Local
                line += '\"' + tr.get_date(timezone = 'Europe/Berlin') + '\n'

                csvf.write(line)

        print('Writing CSV finished.')



                    
                    
                
