__author__ = 'shovan'

import twilio
from twilio.rest import TwilioRestClient


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_bangladeshi_number(number):
    number = str(number)
    if is_number(number):
        if len(number) == 13 and number[:4] == '8801':
            return True
        else:
            return False
    else:
        return False

# +818043605187
#
# +819024955484


def is_japanese_number(number):
    number = str(number)
    if is_number(number):
        if len(number) >= 5:
            return True
        else:
            return False
    else:
        return False


def send_sms(body, number):
    if is_bangladeshi_number(number) or is_japanese_number(number):
        phone_number = '+' + number
        account_sid = "AC437477fe6d2500ac00bd6a743b9b4f80"
        auth_token = "02f01bb4158b27b867519aa72e179560"
        client = TwilioRestClient(account_sid, auth_token)
        try:
            message = client.messages.create(to=phone_number, from_="+14439633299",
                                         body=body)
            print('sent')
            return 'its sent!'
        except twilio.TwilioRestException as e:
            print e
            return 'something bad happened'


    else:
        print('not sent')
        return 'something bad happened'