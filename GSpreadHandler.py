import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

'''
responsible for all the interactions and transformations
that are involved with google spreadsheets 
'''

class GoogleSpreadHandler():

    def __init__(self):
        return None

    def get_finance_worksheet(self, json_file, url_key, worksheet_name):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(url_key).worksheet(worksheet_name)
        self.worksheet = worksheet

    def convert_worksheet(self, worksheet):
        list_of_lists = worksheet.get_all_values()
        googlesheet = pd.DataFrame(list_of_lists)
        col = list(googlesheet.ix[0])
        googlesheet.columns = col #grab headers
        googlesheet.drop(0, inplace=True) # drop headers
        googlesheet['Date'] = pd.to_datetime(list(googlesheet['Date']), utc=True)
        return googlesheet

    def find_new_entries(self, existing, newentries):
        merged = existing.merge(newentries, how='outer') # combine the google doc with the uploads list
        newentries = pd.concat([merged, existing]).drop_duplicates(['Date','Submitter','Owner'], keep=False) #remove the files that are already on the doc
        newentries = newentries.reset_index().drop('index',axis=1)
        return newentries

    def get_column_names(self, sheetsframe): # returns the correct alphabet letters for the columns
            alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            column = []
            max_cols = sheetsframe.shape[1]
            for i in range(max_cols):
                column.append(alpha[i])
            return column

    def update_workbook(self, newentries): #append to existing items
        existingsheet = self.convert_worksheet(self.worksheet)

        alpha = self.get_column_names(existingsheet)
        lnewentries = len(newentries)
        lgdf = len(existingsheet)

        for index, letter in enumerate(alpha):
            for i in range(lnewentries):
                value = newentries.ix[i,index]
                wk_index = lgdf+i+2 #plus two because of header & index at 0
                cell = str(letter)+str(wk_index)
                self.worksheet.update_acell(cell, value)
        return print('Updating Google Docs Complete!')

    def calculate_owed(self, filter_date):
        googlesheet = self.convert_worksheet(self.worksheet)

        filter_date = pd.to_datetime(filter_date)
        googlesheet['Month'] = googlesheet['Date'].dt.month
        googlesheet['Year'] = googlesheet['Date'].dt.year
        googlesheet = googlesheet[googlesheet['Month'] == filter_date.month]
        googlesheet = googlesheet[googlesheet['Year']== filter_date.year]

        googlesheet['Amount'] = googlesheet['Amount'].astype(float)
        paid_amount = googlesheet.groupby('Submitter')['Amount'].sum()
        equitable_amount = googlesheet.groupby('Owner')['Amount'].sum()

        try:
            paid_partner_1 = paid_amount[account_id_beta]
            paid_partner_2 = paid_amount[expense_account_id_two]
            payment = paid_amount[account_id_beta] - equitable_amount[account_id_beta]
            #whoever pays more means they are to be compensated by the other
            payment_partner_1 = payment
        except:
            paid_partner_1 = 0
            paid_partner_2 = 0
            payment = 0

        return payment, paid_partner_1, paid_partner_2