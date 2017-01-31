from time import sleep
import decimal
import gnucashxml
import gspread

import dropbox #https://github.com/dropbox/dropbox-sdk-python
import datetime as dt
import pandas as pd

from slackclient import SlackClient

import warnings
warnings.filterwarnings("ignore")

from private import keys
import dbox

SLACK_CHANNEL = keys.SLACK_CHANNEL
SLACK_TOKEN = keys.SLACK_TOKEN
dbox_accesstoken = keys.dbox_accesstoken
account_id_alpha = keys.account_id_alpha
account_id_beta = keys.account_id_beta

google_json = keys.google_json
spreadsheet_key = keys.spreadsheet_key
worksheet_name = keys.worksheet_name

sc = SlackClient(SLACK_TOKEN)

import GNUhandler as gnuh
import GSpreadHandler as gsph
import SlackHandler as sh

sent = False
latestfile = None
prevfile = None

if __name__ == "__main__":

    while True:

      
      db = dbox.dboxGrabber(accesstoken = dbox_accesstoken) #grab the latest file
      latestfile = db.grab_latest_file_path(path='/Apps/GnuCash Android')

      if latestfile != prevfile:

        db.save_latest_gnu(filepath=latestfile, saveas='GNUCashLatest.gnca')
        db.log_downloads(latestfile, logfile='download_log.csv')
        prevfile = latestfile
        #dgb.delete_latest_gnu(prevfile) in dropbox

        gnu = gnuh.GNUhandler(account_id_alpha, account_id_beta, bookfile = "GNUCashLatest.gnca")
        gnu.parse_bookfile(acctype = 'EXPENSE')
        sharedexpenses = gnu.get_transactions(shared = True)

        gsp = gsph.GoogleSpreadHandler()
    
        gsp.get_finance_worksheet(json_file=google_json, url_key=spreadsheet_key, worksheet_name=worksheet_name)
        #grab and convert to df
        googlesheet = gsp.convert_worksheet(worksheet=gsp.worksheet)
        print('Loaded Google')
        newentries = gsp.find_new_entries(googlesheet, sharedexpenses) #find any new entries  and update workbook

        if len(newentries):
          print('Updating Spreadsheet')
          gsp.update_workbook(newentries) # append to existing items

      #we always want to be checking for the date to send slack updates

      #get current time
      current_day, current_hour= sh.get_time()

      #if current date/time match conditions, proceed to calc and craft message to be sent
      #if not already sent included in message_cond_check function
      grab_message_cond, months_back = sh.message_cond_check(sent, current_day, current_hour)

      if grab_message_cond:
        filter_date = sh.get_message_time(months_back)
        #update api tokens? // prob not necesasry
        payment, paid_partner_1, paid_partner_2 = gsp.calculate_owed(filter_date)
        message = sh.grab_message(payment, paid_partner_1, paid_partner_2, filter_date)

        #send to slack
        sh.send_to_slack(SLACK_CHANNEL, message)
        sent = True

      #reset sent counter the day after notifcations are set to send
      if int(current_day) == 2 or int(current_day) == 16:
        sent = False

      print('sleeping')
      sleep(200)
