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

    def __init__(self, wallet_address, wallet_name):
        self.wallet_address = wallet_address
        self.wallet_name = wallet_name
        self.assignments = []

    def add_assign(self, transfer_type : CTTransferType, from_address = None, to_address = None):
        assignment = {'transfer_type' : transfer_type, 'from_address' : from_address, 'to_address' : to_address}
        self.assignments.append(assignment)

    def export_csv(self, filename):

        print("Fetching transfers from tronscan.org API ...")
        scanner = tronscanner.TronScan(self.wallet_address)
        transfers = scanner.get_all_transfers()
        ptr = tronparser.TronTransfer.parse_transfers(transfers)
        print("Fetching success.")

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
                line += '\"' + self.wallet_name + '\",'

                # Group
                line += r'"",'

                # Comment
                line += r'"",'

                # Date
                # ToDo: Local
                line += '\"' + tr.get_date(timezone = 'Europe/Berlin') + '\n'

                csvf.write(line)

        print('Writing CSV finished.')



                    
                    
                
