from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from local_lib.v3 import is_number, is_float, send_sms
from subscriber.models import Consumer, ConsumerType
from transaction.models import BuyerSellerAccount, Transaction, ProductsInTransaction, dueTransaction
from .models import SMSPayment
import datetime
# Create your views here.
"""
# TODO have to complete this function.
# could not finish it due to insufficient balance
"""


@csrf_exempt
def get_sms(request):
    get_data = request.GET
    # print(get_data)
    # todo have to change the parameters of get data
    # sender_phone = get_data['From']
    # if sender_phone[0] == '+':
    #     sender_phone = sender_phone[1:]
    #     print(sender_phone)
    sms_body = get_data['Body']
    sms_body_into_array = sms_body.split(' ')
    sender_phone = sms_body_into_array[0]
    print(sender_phone)
    if len(sms_body_into_array) > 3:
        if sender_phone[0] == '+':
            sender_phone = sender_phone[1:]
            print(sender_phone)

        other_party_phone = sms_body_into_array[1]
        print(other_party_phone)
        if other_party_phone[0] == '+':
            other_party_phone = other_party_phone[1:]
            print(other_party_phone)
        amount = 0
        if is_number(sms_body_into_array[2]):
            amount = int(sms_body_into_array[2])
        elif is_float((sms_body_into_array[2])):
            amount = float(sms_body_into_array[2])
        if not Consumer.objects.filter(phone__endswith=sender_phone).exists():
            amount = 0
        if not Consumer.objects.filter(phone__endswith=other_party_phone).exists():
            amount = 0
        if amount > 0:
            if Consumer.objects.filter(phone__endswith=sender_phone).exists():
                sender_object = Consumer.objects.get(phone__endswith=sender_phone)
                if Consumer.objects.filter(phone__endswith=other_party_phone).exists():
                    other_party_object = Consumer.objects.get(phone__endswith=other_party_phone)
                else:
                    if Consumer.objects.filter(name='Unknown ' + sender_object.name).exists():
                        other_party_object = Consumer.objects.get(phone__endswith=other_party_phone)
                    else:
                        subscriber_type = ConsumerType.objects.get(type_name__exact='Buyer')
                        other_party_object = Consumer(name=('Unknown ' + sender_object.name),
                                                      type=subscriber_type,
                                                      phone='',
                                                      gender='None')
                        other_party_object.save()
                if sender_object.type.type_name == 'Buyer':
                    buyer_object = sender_object
                    seller_object = other_party_object
                else:
                    if other_party_object.type.type_name == 'Buyer':
                        buyer_object = other_party_object
                        seller_object = sender_object
                    else:
                        buyer_object = sender_object
                        seller_object = other_party_object
                if BuyerSellerAccount.objects.filter(seller=seller_object, buyer=buyer_object).exists():
                    balance = BuyerSellerAccount.objects.get(seller=seller_object, buyer=buyer_object)
                    # previousDue = balance.total_due
                    balance.total_paid += amount
                    remain_due = balance.total_due - amount
                    balance.total_due = remain_due
                    balance.last_paid_amount = amount
                    balance.save()
                else:
                    remain_due = 0
                    # previousDue = 0
                    balance = BuyerSellerAccount(seller=seller_object,
                                                 buyer=buyer_object,
                                                 total_amount_of_transaction=0,
                                                 total_paid=amount,
                                                 total_due=0,
                                                 last_paid_amount=amount)
                    balance.save()
                new_sms_payment = SMSPayment(buyer=buyer_object,
                                             seller=seller_object,
                                             amount=amount)
                new_sms_payment.save()

                transaction = dueTransaction(seller=seller_object,
                                             buyer=buyer_object,
                                             total_amount=0,
                                             total_paid=amount,
                                             total_due=0)
                transaction.save()
                sms_text = 'You have received taka %s from %s. The remaining due amount is taka %s. Thanks for shopping with Hishab Limited.' %(format(amount,'.2f'), buyer_object.name, format(remain_due, '.2f'))
                send_sms(sms_text, seller_object.phone)
                sms_text = 'You have paid taka %s due to %s. The remaining due amount is taka %s. Thanks for shopping with Hishab Limited.' %(format(amount,'.2f'), seller_object.name, format(remain_due, '.2f'))
                send_sms(sms_text, buyer_object.phone)
            return HttpResponse('got_it', content_type="plain/text")
        else:
            sender_object = Consumer.objects.get(phone__endswith=sender_phone)
            sms_text = 'You have entered wrong input. Please try again with correct information. Thanks for shopping with Hishab Limited.'
            send_sms(sms_text, sender_object.phone)




@csrf_exempt
def send_sms_for_dues(request):
    today_weekday = (datetime.date.today().isoweekday() + 1) % 7
    # print(today_weekday)
    # , total_due__gt=0
    all_balance = BuyerSellerAccount.objects.filter(total_due__gt=0)
    for a in all_balance:
        seller_name = a.seller.name
        buyer_name = a.buyer.name
        due = a.total_due
        # print(seller_name)
        # print(buyer_name)
        sms_text = 'Dear %s, you have taka %s due to %s. Please pay the bills as soon as possible. ' \
                   'Thanks for shopping with Hishab Limited.' % (buyer_name, format(due,'.2f'), seller_name)
        print(a.buyer.phone)
        print(sms_text)


        send_sms(sms_text, a.buyer.phone)

    return HttpResponse('got_it', content_type="plain/text")

