from slackclient import SlackClient
import datetime as dt
import locale
import pandas as pd

'''
Handles all the functions related
to sending slack messages
'''

def create_payment_message(payment, paid_partner_1, paid_partner_2, filter_date):

    filter_date = pd.to_datetime(filter_date)
    creditor = None
    debitor = None

    if payment > 0:
        creditor = account_id_beta
        debitor = account_id_alpha
        print(account_id_beta, ' owes ',account_id_alpha, '$',payment)
    if payment < 0:
        creditor = account_id_alpha
        debitor = account_id_beta
        print(account_id_alpha, 'owes',account_id_beta, '$', -payment)
        payment = -payment
    if payment == 0:
        print('Nothing is owed')
    locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
    payment = locale.currency(payment, grouping=True)
    paid_partner_1 = locale.currency(paid_partner_1, grouping=True)
    paid_partner_2 = locale.currency(paid_partner_2, grouping=True)
    if creditor != None:
        message = '{}, {}: {} owes {} {}. {} and {} spent {}, {} respectively.'.format(filter_date.strftime('%B'),filter_date.year,creditor,
                                                                                      debitor,payment,account_id_alpha,account_id_beta,paid_partner_1,paid_partner_2)
    else:
        message = 'Nothing is owed! {} and {} spent {}, {} respectively.'.format(account_id_alpha,account_id_beta,paid_partner_1,paid_partner_2)

    return message

def get_time():
    N = dt.datetime.now()
    current_hour = pd.to_datetime(N).strftime('%H')
    current_day = pd.to_datetime(N).strftime('%d')
    return current_day, current_hour

def get_message_time(month): #time used to fileter the dataset
    month = 30*month
    N = dt.datetime.now() - dt.timedelta(days=month)
    filter_date = pd.to_datetime(N).strftime('%m/%d/%Y')
    return filter_date

def message_cond_check(sent, current_day, current_hour):
    grab_message_cond = False
    months_back = None
    if sent == False:
        if int(current_day) == 1:
            if int(current_hour) == 19:
                grab_message_cond = True
                months_back = 1
        if int(current_day) == 15:
            if int(current_hour) == 19:
                grab_message_cond = True
                months_back = 0
        return grab_message_cond, months_back
    return grab_message_cond, months_back

def grab_message(payment, paid_partner_1, paid_partner_2, filter_date):
    message = create_payment_message(payment, paid_partner_1, paid_partner_2, filter_date)
    return message

def send_to_slack(SLACK_CHANNEL, message):
    try:
        sc.api_call("chat.postMessage", channel=SLACK_CHANNEL, text=message,
                    username='FINcalc', icon_emoji=':robot_face:')
    except:
        print('Error sending message')
    return print('Messsage sent')