from django.shortcuts import render, HttpResponse
from .models import BuyerSellerAccount, Transaction, ProductsInTransaction
from subscriber.models import Consumer, ConsumerType
from voice_records.models import VoiceRecord
from product.models import Product
from shop_inventory.models import Inventory, ProductInventory, BuySellProfitInventory, ProductBuySellProfitInventory, BuySellProfitInventoryIndividual
from django.views.decorators.csrf import csrf_exempt
from local_lib.v3 import is_number, is_float, is_bangladeshi_number, is_japanese_number, send_sms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from transcriber_management.models import Transcriber, \
    TranscriberInTranscription, \
    FailedTranscription
import datetime


# Create your views here.


@login_required(login_url='/login/')
def add_transaction(request):
    post_data = request.POST
    print(post_data)
    response = 'not_ok'
    if 'csrfmiddlewaretoken' in post_data:
        if 'call_id' in post_data and 'caller_id' in post_data and 'otherParty' in post_data:
            call_id = post_data['call_id']
            call_object = VoiceRecord.objects.get(pk=call_id)
            caller_id = post_data['caller_id']
            caller_object = Consumer.objects.get(pk=caller_id)
            other_party = post_data['otherParty']
            if post_data['distributorTransaction'] == '0':
                if other_party == '0':
                    if Consumer.objects.filter(name=('Unknown ' + caller_object.name)).exists():
                        other_party_object = Consumer.objects.get(name=('Unknown' + caller_object.name))
                    else:
                        subscriber_type = ConsumerType.objects.get(type_name__exact='Buyer')
                        other_party_object = Consumer(name=('Unknown ' + caller_object.name),
                                                      type=subscriber_type,
                                                      phone='',
                                                      gender='None')
                        other_party_object.save()

                elif is_number(other_party) and not other_party == '0':
                    other_party_object = Consumer.objects.get(pk=other_party)
                else:
                    if Consumer.objects.filter(name=('Unknown' + caller_object.name)).exists():
                        other_party_object = Consumer.objects.get(name=('Unknown' + caller_object.name))
                    else:
                        subscriber_type = ConsumerType.objects.get(type_name__exact='Buyer')
                        other_party_object = Consumer(name=('Unknown' + caller_object.name),
                                                      type=subscriber_type,
                                                      phone='',
                                                      gender='None')
                        other_party_object.save()

            else:
                if Consumer.objects.filter(name=('Distributor' + caller_object.name)).exists():
                    other_party_object = Consumer.objects.get(name=('Distributor' + caller_object.name))
                else:
                    subscriber_type = ConsumerType.objects.get(type_name__exact='Distributor')
                    other_party_object = Consumer(name=('Distributor' + caller_object.name),
                                                  type=subscriber_type,
                                                  phone='',
                                                  gender='None')
                    other_party_object.save()

            if caller_object.type.type_name == 'Buyer':
                buyer_object = caller_object
                seller_object = other_party_object
            elif caller_object.type.type_name == 'Distributor' or caller_object.type.type_name == 'SR':
                buyer_object = other_party_object
                seller_object = caller_object
            else:
                if other_party_object.type.type_name == 'Buyer':
                    buyer_object = other_party_object
                    seller_object = caller_object
                elif other_party_object.type.type_name == 'Distributor' or other_party_object.type.type_name == 'SR':
                    buyer_object = caller_object
                    seller_object = other_party_object
                else:
                    buyer_object = caller_object
                    seller_object = other_party_object
            # balance Update done here
            if BuyerSellerAccount.objects.filter(seller=seller_object, buyer=buyer_object).exists():
                balance = BuyerSellerAccount.objects.get(seller=seller_object, buyer=buyer_object)
                balance.total_amount_of_transaction += float(post_data['transactionTotal'])
                balance.total_paid += float(post_data['transactionPaid'])
                balance.total_due += float(post_data['transactionDue'])
                balance.last_paid_amount = float(post_data['transactionPaid'])
                balance.save()
            else:
                balance = BuyerSellerAccount(seller=seller_object,
                                             buyer=buyer_object,
                                             total_amount_of_transaction=float(post_data['transactionTotal']),
                                             total_paid=float(post_data['transactionPaid']),
                                             total_due=float(post_data['transactionDue']),
                                             last_paid_amount=float(post_data['transactionPaid']))
                balance.save()
            # transaction added here
            transcriber = request.session['user']
            if Transcriber.objects.filter(name=transcriber).exists():
                transcriber_object = Transcriber.objects.get(name=transcriber)
            else:
                transcriber_object = Transcriber(name=transcriber)
                transcriber_object.save()

            transaction = Transaction(seller=seller_object,
                                      buyer=buyer_object,
                                      total_amount=float(post_data['transactionTotal']),
                                      total_paid=float(post_data['transactionPaid']),
                                      total_due=float(post_data['transactionDue']),
                                      transcriber=transcriber_object,
                                      callID=call_object)
            transaction.save()
            tr = transaction.id
            print(transaction.id)
            # product transaction added here
            product_string = post_data['transactionProducts']
            product_string = product_string.strip(';')
            product_array = product_string.split(';')
            # this section covers fraud detection

            if float(post_data['transactionDue']) > 0:
                if buyer_object.type.type_name == 'Buyer':
                    if BuyerSellerAccount.objects.filter(buyer=buyer_object).exists():
                        fraud = False
                        for transaction in BuyerSellerAccount.objects.filter(buyer=buyer_object):
                            if transaction.total_due > 200 and not transaction.seller == seller_object:
                                fraud = True
                                break
                        if fraud:
                            fraud_text = '%s er onno dokan e 200.00 takar beshi baki royeche.' \
                                         'Er sathe shabdhan e len den korun. Dhonnobad.' % buyer_object.name
                            print(fraud_text)
                            phone_number_to_send_sms = seller_object.phone
                            send_sms(fraud_text, phone_number_to_send_sms)
            count = 0
            # finding the shop and transaction with buyer or distributor
            is_shop = False
            if buyer_object.type.type_name == 'Seller':
                is_shop = True
                shop = buyer_object
                transaction_with = seller_object.type.type_name
            elif seller_object.type.type_name == 'Seller':
                is_shop = True
                shop = seller_object
                transaction_with = buyer_object.type.type_name
            number_of_products = len(product_array)

            sms_text_products = ''
            while count < len(product_array):
                new_product = product_array[count]
                product_breakdown = new_product.split('-')
                product_name = product_breakdown[0]
                product_object = Product.objects.get(name=product_name)
                product_quantity = product_breakdown[1]
                product_price = float(product_breakdown[2])
                # sms_text_products = product_name + ' ' +
                if is_shop:
                    if Inventory.objects.filter(shop=shop, product=product_object).exists():
                        inventory = Inventory.objects.get(shop=shop, product=product_object)
                        if transaction_with == 'Buyer':
                            inventory.left -= float(product_quantity)
                            inventory.save()
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            inventory.left += float(product_quantity)
                            inventory.save()
                    else:
                        if transaction_with == 'Buyer':
                            left = 0
                            inventory = Inventory(shop=shop,
                                                  product=product_object,
                                                  unit=product_object.retail_unit,
                                                  left=left)
                            inventory.save()
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            left = float(product_quantity)
                            inventory = Inventory(shop=shop,
                                                  product=product_object,
                                                  unit=product_object.retail_unit,
                                                  left=left)
                            inventory.save()
                    # list of sold product is added here
                    if ProductInventory.objects.filter(product=product_object).exists():
                        pro_inventory = ProductInventory.objects.get(product=product_object)
                        if transaction_with == 'Buyer':
                            pro_inventory.sold += float(product_quantity)
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            pro_inventory.sold += float(product_quantity)
                        pro_inventory.save()
                    else:
                        if transaction_with == 'Buyer':
                            sold = float(product_quantity)
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            sold = float(product_quantity)
                        pro_inventory = ProductInventory(product=product_object,
                                                         unit=product_object.retail_unit,
                                                         sold=sold)
                        pro_inventory.save()
                    # list of profit per shop in per product

                    if transaction_with == 'Buyer':
                        if ProductBuySellProfitInventory.objects.filter(product=product_object).exists():
                            buying_price_for_this_transaction = ProductBuySellProfitInventory.objects.get(product=product_object).buying_price
                        else:
                            new_added = ProductBuySellProfitInventory(product=product_object)
                            new_added.save()
                            buying_price_for_this_transaction = new_added.buying_price

                        profit_of_this_product = product_price - buying_price_for_this_transaction
                        new_transcriber_transcription_for_this_product = BuySellProfitInventoryIndividual(shop=shop,
                                                                                                          product=product_object,
                                                                                                          unit=product_object.retail_unit,
                                                                                                          buying_price=buying_price_for_this_transaction,
                                                                                                          selling_price=product_price, profit=profit_of_this_product)
                        new_transcriber_transcription_for_this_product.save()

                    if BuySellProfitInventory.objects.filter(shop=shop, product=product_object).exists():
                        buy_sell_profit = BuySellProfitInventory.objects.get(shop=shop, product=product_object)
                        if transaction_with == 'Buyer':
                            if buy_sell_profit.selling_price == 0:
                                buy_sell_profit.selling_price = product_price
                            else:
                                buy_sell_profit.selling_price = (buy_sell_profit.selling_price + product_price) / 2
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            if buy_sell_profit.buying_price == 0:
                                buy_sell_profit.buying_price = (product_price)
                            else:
                                buy_sell_profit.buying_price = ((buy_sell_profit.buying_price +
                                                                 (product_price)) / 2)
                        buy_sell_profit.profit = buy_sell_profit.selling_price - buy_sell_profit.buying_price
                        buy_sell_profit.save()
                    else:
                        if transaction_with == 'Buyer':
                            buy_sell_profit = BuySellProfitInventory(shop=shop,
                                                                     product=product_object,
                                                                     unit=product_object.retail_unit,
                                                                     selling_price=product_price)
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            buy_sell_profit = BuySellProfitInventory(shop=shop,
                                                                     product=product_object,
                                                                     unit=product_object.retail_unit,
                                                                     buying_price=(product_price))
                        buy_sell_profit.profit = buy_sell_profit.selling_price - buy_sell_profit.buying_price
                        buy_sell_profit.save()

                    # list of profit per product

                    if ProductBuySellProfitInventory.objects.filter(product=product_object).exists():
                        product_buy_sell_profit = ProductBuySellProfitInventory.objects.get(product=product_object)
                        if transaction_with == 'Buyer':
                            if product_buy_sell_profit.selling_price == 0:
                                product_buy_sell_profit.selling_price = product_price
                            else:
                                product_buy_sell_profit.selling_price = (product_buy_sell_profit.selling_price + product_price) / 2
                            product_buy_sell_profit.total_sold += float(product_quantity)
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            if product_buy_sell_profit.buying_price == 0:
                                product_buy_sell_profit.buying_price = (product_price)
                            else:
                                product_buy_sell_profit.buying_price = ((product_buy_sell_profit.buying_price +
                                                                         (product_price)) / 2)
                        product_buy_sell_profit.profit = product_buy_sell_profit.selling_price - product_buy_sell_profit.buying_price
                        product_buy_sell_profit.q_profit = product_buy_sell_profit.profit * product_buy_sell_profit.total_sold
                        product_buy_sell_profit.save()
                    else:
                        if transaction_with == 'Buyer':
                            product_buy_sell_profit = ProductBuySellProfitInventory(product=product_object,
                                                                                    unit=product_object.retail_unit,
                                                                                    selling_price=product_price,
                                                                                    total_sold=float(product_quantity))
                        elif transaction_with == 'Distributor' or transaction_with == 'SR':
                            product_buy_sell_profit = ProductBuySellProfitInventory(product=product_object,
                                                                                    unit=product_object.retail_unit,
                                                                                    buying_price=(product_price))
                        profit_here = product_buy_sell_profit.selling_price - product_buy_sell_profit.buying_price
                        product_buy_sell_profit.profit = profit_here
                        product_buy_sell_profit.q_profit = profit_here * product_buy_sell_profit.total_sold
                        product_buy_sell_profit.save()

                if buyer_object.type.type_name == 'Distributor' or seller_object.type.type_name == 'Distributor' or buyer_object.type.type_name == 'SR' or seller_object.type.type_name == 'SR':
                    product_unit = product_object.retail_unit
                else:
                    product_unit = product_object.retail_unit
                # product_quantity = float(product_quantity)
                print(product_object)
                print(product_unit)
                print(product_price)
                print(product_quantity)
                if float(product_quantity)>0:
                    sms_text_products += product_name + ' ' + str(round(float(product_quantity),2)) + ' ' + product_unit + ' price: taka ' + str(format((float(product_price)*float(product_quantity)),'.2f')) + ','
                    print(sms_text_products)
                else:
                    sms_text_products += ''
                # transaction =
                tr_object = Transaction.objects.get(pk=tr)
                product_transaction = ProductsInTransaction(TID=tr_object,
                                                            product=product_object,
                                                            unit=product_unit,
                                                            price_per_unit=product_price,
                                                            quantity=product_quantity)

                product_transaction.save()
                count += 1
            sms_text_products = sms_text_products[:-1]
            sms_text_seller = seller_object.name
            sms_text_buyer = buyer_object.name
            sms_text_id = tr
            date = datetime.date.today()
            sms_total_bill = post_data['transactionTotal']
            sms_total_paid = post_data['transactionPaid']
            sms_total_due = post_data['transactionDue']
            # buyer_sms = '%s, you have purchased %s ' \
            #             'from %s.' \
            #             ' Total bill : taka %s, Paid : taka %s, Due : taka %s.' \
            #             ' Thanks for shopping with Hishab Limited ' % (sms_text_buyer,
            #                                                            sms_text_products, sms_text_seller,
            #                                                            format(float(sms_total_bill),'.2f'),
            #                                                            format(float(sms_total_bill)-float(sms_total_due),'.2f'),
            #                                                            format(float(sms_total_due),'.2f'))
            buyer_sms = '%s, Apni %s -er kach theke kroy korechen %s ' \
                        ' Mot bill : taka %s, porishodh kora hoyeche : taka %s, Baki ache : taka %s.' \
                        ' Hishab Ltd-er shathe kenakata korar jonno dhonnobad ' % (sms_text_buyer, sms_text_seller,
                                                                               sms_text_products,
                                                                               format(float(sms_total_bill),'.2f'),
                                                                               format(float(sms_total_bill)-float(sms_total_due),'.2f'),
                                                                               format(float(sms_total_due),'.2f'))
            # seller_sms = '%s, you have sold %s ' \
            #              'to %s.' \
            #              ' Total bill : taka %s, Paid : taka %s,Due : taka %s.' \
            #              ' Thanks for shopping with Hishab Limited ' % (sms_text_seller,
            #                                                             sms_text_products, sms_text_buyer,
            #                                                             format(float(sms_total_bill),'.2f'),
            #                                                             format(float(sms_total_bill)-float(sms_total_due),'.2f'),
            #                                                             format(float(sms_total_due),'.2f'))
            seller_sms = '%s, Apni %s -er kache bikroy korechen %s ' \
                         ' Mot Bill : taka %s, Porishodh kora hoyeche : taka %s, Baki ache : taka %s.' \
                         ' Hishab Ltd-er shathe kenakata korar jonno dhonnobad ' % (sms_text_seller, sms_text_buyer,
                                                                                    sms_text_products,
                                                                                    format(float(sms_total_bill),'.2f'),
                                                                                    format(float(sms_total_bill)-float(sms_total_due),'.2f'),
                                                                                    format(float(sms_total_due),'.2f'))
            # caller scoring update !
            send_sms(buyer_sms, buyer_object.phone)
            send_sms(seller_sms, seller_object.phone)
            caller_object.total_successful_call += 1
            caller_object.save()
            call_object.transcribed = True
            call_object.save()
            # add transcriber info here
            transcriber = request.session['user']
            if Transcriber.objects.filter(name=transcriber).exists():
                transcriber_object = Transcriber.objects.get(name=transcriber)
            else:
                transcriber_object = Transcriber(name=transcriber)
                transcriber_object.save()
            new_transcriber_transcription = TranscriberInTranscription(name=transcriber_object,
                                                                       callID=call_object,
                                                                       number_of_products=number_of_products,
                                                                       time_taken=post_data['timetaken'])
            new_transcriber_transcription.save()

            response = 'ok'

    return HttpResponse(response)


@csrf_exempt
def failed_transaction(request):
    post_data = request.POST
    print(post_data)
    response = 'not_ok'
    if 'reason_fail' in post_data:
        print('here')
        call_id = int(post_data['failCallerID'])
        print(call_id)
        call_object = VoiceRecord.objects.get(pk=call_id)
        call_object.with_error = True
        caller_object = call_object.caller
        caller_object.number_of_calls_with_error += 1
        call_object.save()
        caller_object.save()
        transcriber = request.session['user']
        reason = str(post_data['reason_fail'])
        print(transcriber)
        if not FailedTranscription.objects.filter(callID=call_object).exists():
            if Transcriber.objects.filter(name=transcriber).exists():
                transcriber_object = Transcriber.objects.get(name=transcriber)
            else:
                transcriber_object = Transcriber(name=transcriber)
                transcriber_object.save()
            new_fail_transcription = FailedTranscription(name=transcriber_object,
                                                         callID=call_object,
                                                         remarks=reason)
            new_fail_transcription.save()
            call_object.transcribed = True
            call_object.save()

        response = 'ok'

    return HttpResponse(response)


@csrf_exempt
def detailed_transaction(request):
    get_data = request.GET
    response = '{ '
    if 'id' in get_data:
        transaction_id = get_data['id']
        transaction_object = Transaction.objects.get(id=transaction_id)
        count = 0
        response += '"transaction_id": "%s", "date": "%s", "translate_by": "%s",' \
                    ' "consumer": "%s", "seller": "%s", ' \
                    '"total": "%s", "paid": "%s", ' \
                    '"due": "%s","products": { ' % (transaction_id, transaction_object.DateAdded,
                                                    transaction_object.transcriber, transaction_object.buyer,
                                                    transaction_object.seller, transaction_object.total_amount,
                                                    transaction_object.total_paid, transaction_object.total_due)
        for product_in_transaction in ProductsInTransaction.objects.filter(TID=transaction_object):
            response += '"%s": { "name": "%s", "quantity": "%s", ' \
                        '"unit_price": "%s", "unit": "%s" } ,' % (count, product_in_transaction.product.name,
                                                                  product_in_transaction.quantity,
                                                                  product_in_transaction.price_per_unit,
                                                                  product_in_transaction.unit)
            count += 1
        response = response[:-1]
        response += '}}'
    return HttpResponse(response)
