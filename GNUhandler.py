import pandas as pd
import gnucashxml

class GNUhandler():

    def __init__(self, account_id_alpha, account_id_beta, bookfile = "GNUCashLatest.gnca"):
        self.account_id_alpha = account_id_alpha
        self.account_id_beta = account_id_beta
        self.book = gnucashxml.from_filename(bookfile)

    def parse_bookfile(self, acctype='EXPENSE'):
        #only return expenses
        book = self.book
        splitslist = []
        for account, subaccounts, splits in book.walk(): 
            for split in splits: # for every split in the account
                sp = split
                if account.actype == acctype: # if it is an expense
                        splitslist.append(sp) # append account
        self.splitslist = splitslist

    def get_transactions(self, shared=True):
        #only take transactions that have a int memo corresponding to the percentage split
        splitslist = self.splitslist
        transactions = []
        for split in splitslist:
            try:
                notes = split.transaction.slots['notes']
            except KeyError:
                notes = 100
            transactions.append([split.account.name,split.transaction.description,split.transaction.date,
                                notes,split.transaction.currency,split.value, split.account.description, split.account.actype])
        
        transactions = self.transform_to_df(transactions) #turn into DF

        if shared == True: #reurns only the shared costs
            transactions = self.assign_payment_ownership(transactions) #assign cost ownership based on who submitted the expense into their app 
            transactions = self.calculate_shared_expenses(transactions)  #based on cost ownership, figure out who owes money to the other person

        self.transactions = transactions

        return transactions

    def transform_to_df(self, transactions):
        trans = pd.DataFrame(transactions)
        trans[2] = pd.to_datetime(list(trans[2]),utc=True)
        trans.columns = ['Account Name','Description','Date','Memo','Currency','Amount','Account Description','Type']
        return trans

    def assign_payment_ownership(self, trans):
        '''
        using the specially named account in GNU file
        find out who submitted this backup and by
        extension who paid for everything submitted
        and what the split for payment is going to be
        '''
        account_id_alpha = self.account_id_alpha
        account_id_beta = self.account_id_beta

        account_id_alpha_length = len(trans[trans['Account Name'] == account_id_alpha])
        account_id_beta_length = len(trans[trans['Account Name'] == account_id_beta])

        if account_id_alpha_length != 0:
            trans['Submitter'] = account_id_alpha
        else:
            trans['Submitter'] = account_id_beta
        submitter_paid = trans[trans['Memo'] != 100]
        submitter_paid['Memo'] = pd.to_numeric(submitter_paid['Memo'], errors='coerce')
        submitter_paid['Memo'].fillna(100,inplace=True)
        submitter_paid = submitter_paid[submitter_paid['Memo'] != 100]
        self.submitter_paid = submitter_paid

        return submitter_paid

    def calculate_shared_expenses(self, transactions):
        '''
        figure out the costs 
        based on the splits
        '''
        account_id_alpha = self.account_id_alpha
        account_id_beta = self.account_id_beta
        splitexpenses = transactions

        splitexpenses['Memo'] = splitexpenses['Memo']*(1/100)
        splitexpenses['Owner'] = account_id_alpha
        splitexpenses['Amount'] = splitexpenses['Amount'].astype(float)

        splitexpenses_partner_one = splitexpenses.copy()
        splitexpenses_partner_two = splitexpenses.copy()

        splitexpenses_partner_two['Owner'] = account_id_beta
        splitexpenses_partner_two['Memo'] = splitexpenses_partner_two['Memo'].apply(lambda x: 1 - x)
        
        splitexpenses = splitexpenses_partner_one.merge(splitexpenses_partner_two,how='outer')
        splitexpenses['Original Price'] = splitexpenses['Amount']
        splitexpenses['Amount'] = splitexpenses['Memo'] * splitexpenses['Amount']

        expenses_frame = splitexpenses

        return expenses_frame
