#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from subscriber.models import Consumer, ConsumerType, Recharge, TotalRecharge, ACL
from product.models import Product
from voice_records.models import VoiceRecord, VoiceReg
from sms.models import SMSPayment
# from local_lib.v3 import is_number, is_float
from local_lib.v3 import is_number, is_float, is_bangladeshi_number, is_japanese_number, send_sms
from transaction.models import Transaction, ProductsInTransaction, BuyerSellerAccount, dueTransaction
from shop_inventory.models import Inventory, BuySellProfitInventoryIndividual, BuySellProfitInventory
from transcriber_management.models import Transcriber, TranscriberInTranscription, FailedTranscription
import datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Count




@csrf_exempt
def login_page(request):
    return render(request, 'pages/login.html')


@csrf_exempt
def login_auth(request):
    postdata = request.POST
    print(postdata)
    if 'username' and 'password' in postdata:
        print(postdata['username'])
        login_username = postdata['username']
        print(postdata['password'])
        if ACL.objects.filter(loginID=postdata['username'][-9:]).exists():
            login_username = login_username[-9:]
        else:
            login_username = login_username
        user = authenticate(username=login_username, password=postdata['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['user'] = login_username
                if user.is_superuser:
                    res = redirect('/admin')
                else:
                    res = redirect('/')
            else:
                res = render(request, 'pages/login.html',
                             {'wrong': True,
                              'text': 'The password is valid, but the account has been disabled!'})
        else:
            res = render(request, 'pages/login.html',
                         {'wrong': True,
                          'text': 'The username and password you have entered is not correct. Please retry'})
    else:
        res = render(request, 'pages/login.html', {'wrong': False})

    res['Access-Control-Allow-Origin'] = "*"
    res['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    res['Access-Control-Allow-Methods'] = "PUT, GET, POST, DELETE, OPTIONS"
    return res


def logout_now(request):
    logout(request)
    return render(request, 'pages/login.html')


@login_required(login_url='/login/')
def home(request):
    transcriber_name = request.session['user']
    print request.session['user']
    if ACL.objects.filter(loginID=transcriber_name).exists():
        login_user = ACL.objects.get(loginID=transcriber_name)
        print(login_user.loginUser.name)
        transcriber_name = login_user.loginUser.name
        if login_user.loginUser.type.type_name == 'Distributor':
            if login_user.loginUser.number_of_child == 'CHANGED !!!':
                return render(request, 'pages/Distributor/index.html', {'transcriber_name': transcriber_name})
            else:
                return redirect('/change_password/')
        elif login_user.loginUser.type.type_name == 'SR':
            if login_user.loginUser.number_of_child == 'CHANGED !!!':
                return render(request, 'pages/SR/index.html', {'transcriber_name': transcriber_name})
            else:
                return redirect('/change_password/')
        elif login_user.loginUser.type.type_name == 'Seller':
            if login_user.loginUser.number_of_child == 'CHANGED !!!':
                return render(request, 'pages/Shop/index.html', {'transcriber_name': transcriber_name})
            else:
                return redirect('/change_password/')
        elif login_user.loginUser.type.type_name == 'Buyer':
            if login_user.loginUser.number_of_child == 'CHANGED !!!':
                return render(request, 'pages/Consumer/index.html', {'transcriber_name': transcriber_name})
            else:
                return redirect('/change_password/')
    else:
        number_of_reg_calls = VoiceReg.objects.filter().count()
        number_of_transaction_calls = VoiceRecord.objects.filter().count()
        total = number_of_reg_calls + number_of_transaction_calls
        if total > 0:
            reg_call_percentage = (number_of_reg_calls / float(total)) * 100
            transaction_call_percentage = (number_of_transaction_calls / float(total)) * 100
        else:
            transaction_call_percentage = 0
            reg_call_percentage = 0
        today_month = datetime.date.today().month
        today_year = datetime.date.today().year
        count = 1
        data_2 = ''
        data_3 = ''
        data_4 = ''
        data_5 = ''
        data_6 = ''
        max = 0
        max_table_2 = 0
        total_sell = VoiceRecord.objects.filter(purpose='sell').count()
        total_buy = VoiceRecord.objects.filter(purpose='buy').count()
        total_money_transaction = SMSPayment.objects.filter().count()
        total_for_chart2 = number_of_reg_calls + number_of_transaction_calls
        if total_for_chart2 > 0:
            sell_percentage = (total_sell / float(total_for_chart2)) * 100
            buy_percentage = (total_buy / float(total_for_chart2)) * 100
            money_transaction_percentage = (total_money_transaction / float(total_for_chart2)) * 100
        else:
            sell_percentage = 0
            buy_percentage = 0
            money_transaction_percentage = 0
        while count < 32:
            total_call_that_day = VoiceRecord.objects.filter(DateAdded__month=today_month,
                                                             DateAdded__year=today_year, DateAdded__day=count).count()
            total_reg_that_day = VoiceReg.objects.filter(DateAdded__month=today_month,
                                                         DateAdded__year=today_year, DateAdded__day=count).count()
            if max < total_call_that_day:
                max = total_call_that_day + 2
            if max < total_reg_that_day:
                max = total_reg_that_day + 2

            data_2 += '[gd(%s, %s, %s), %s],' % (today_year, today_month, count, total_call_that_day)
            data_3 += '[gd(%s, %s, %s), %s],' % (today_year, today_month, count, total_reg_that_day)
            total_buy_that_day = VoiceRecord.objects.filter(DateAdded__month=today_month,
                                                            DateAdded__year=today_year,
                                                            DateAdded__day=count,
                                                            purpose='buy').count()
            total_sell_that_day = VoiceRecord.objects.filter(DateAdded__month=today_month,
                                                             DateAdded__year=today_year,
                                                             DateAdded__day=count,
                                                             purpose='sell').count()
            total_payment_that_day = SMSPayment.objects.filter(DateAdded__month=today_month,
                                                               DateAdded__year=today_year,
                                                               DateAdded__day=count).count()
            if max_table_2 < total_buy_that_day:
                max_table_2 = total_buy_that_day + 2
            if max_table_2 < total_sell_that_day:
                max_table_2 = total_sell_that_day + 2
            if max_table_2 < total_payment_that_day:
                max_table_2 = total_payment_that_day + 2
            data_4 += '[gd(%s, %s, %s), %s],' % (today_year, today_month, count, total_buy_that_day)
            data_5 += '[gd(%s, %s, %s), %s],' % (today_year, today_month, count, total_sell_that_day)
            data_6 += '[gd(%s, %s, %s), %s],' % (today_year, today_month, count, total_payment_that_day)

            count += 1
        data_2 = data_2[:-1]
        data_3 = data_3[:-1]
        data_4 = data_4[:-1]
        data_5 = data_5[:-1]
        data_6 = data_6[:-1]
        number_of_transactions = Transaction.objects.filter().count()
        number_of_transactions_with_due = Transaction.objects.filter(total_due__gt=0).count()
        number_of_transactions_without_due = Transaction.objects.filter(total_due__lte=0).count()
        shop_consumer = ConsumerType.objects.get(type_name='Seller')
        all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
        all_user_for_base = Consumer.objects.all()
        shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
        all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)
        print(all_consumer_for_base.count)
        return render(request, 'pages/index.html', {'shop_list_base': all_shop_for_base,
                                                    'number_of_reg_calls': number_of_reg_calls,
                                                    'transcriber_name': transcriber_name,
                                                    'number_of_transaction_calls': number_of_transaction_calls,
                                                    'all_consumer_for_base' :all_consumer_for_base,
                                                    'reg_call_percentage': reg_call_percentage,
                                                    'transaction_call_percentage': transaction_call_percentage,
                                                    'data_2': data_2,
                                                    'data_3': data_3,
                                                    'data_4': data_4,
                                                    'data_5': data_5,
                                                    'data_6': data_6,
                                                    'max': max,
                                                    'number_of_transactions': number_of_transactions,
                                                    'number_of_transactions_with_due': number_of_transactions_with_due,
                                                    'number_of_transactions_without_due': number_of_transactions_without_due,
                                                    'max_table_2': max_table_2,
                                                    'total_sell': total_sell,
                                                    'total_buy': total_buy,
                                                    'total_money_transaction': total_money_transaction,
                                                    'sell_percentage': sell_percentage,
                                                    'buy_percentage': buy_percentage,
                                                    'money_transaction_percentage': money_transaction_percentage,
                                                    'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def translator_page(request):
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/translator.html', {'shop_list_base': all_shop_for_base,
                                                     'all_consumer_for_base' :all_consumer_for_base,
                                                     'transcriber_name': transcriber_name,
                                                     'all_user_for_base': all_user_for_base})


# all report views are here
@login_required(login_url='/login/')
def report_monthly_shop(request):
    get_data = request.GET
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False

    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    shop_id = shop_object.id
    total_sell = 0
    total_sell_due = 0
    total_sell_paid = 0
    total_purchase = 0
    total_purchase_due = 0
    total_purchase_paid = 0
    for month_sell in BuyerSellerAccount.objects.filter(seller=shop_object):
        total_sell += month_sell.total_amount_of_transaction
        total_sell_due += month_sell.total_due
        total_sell_paid += month_sell.total_paid
    for month_purchase in BuyerSellerAccount.objects.filter(buyer=shop_object):
        total_purchase += month_purchase.total_amount_of_transaction
        total_purchase_due += month_purchase.total_due
        total_purchase_paid += month_purchase.total_paid



    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_monthly_shop.html', {'shop_list_base': all_shop_for_base,
                                                              'shop_name': shop_name,
                                                              'shop_id': shop_id,
                                                              'all_consumer_for_base' :all_consumer_for_base,
                                                              'total_sell': total_sell,
                                                              'transcriber_name': transcriber_name,
                                                              'total_sell_due': total_sell_due,
                                                              'total_sell_paid': total_sell_paid,
                                                              'bangla': bangla,
                                                              'total_purchase': total_purchase,
                                                              'total_purchase_due': total_purchase_due,
                                                              'total_purchase_paid': total_purchase_paid,
                                                              'all_user_for_base': all_user_for_base})

# report_monthly_shop_json
@login_required(login_url='/login/')
def report_monthly_shop_json(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(id=shop_name)

    shop_inventory = BuySellProfitInventoryIndividual.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    output = '{"data": [ '

    if get_data['t'] == '1':
        rank = 1
        this_year = datetime.date.today().year
        # this_month = 1
        this_day = 1
        for this_month in range(1, 13, 1):
            count = 0
            for this_day in range(1, 32, 1):
                for a_product in Product.objects.all():

                    product_price = 0
                    product_name = a_product.name
                    total_sell = 0
                    total_due = 0
                    total_paid = 0
                    for this_day_sell_transaction in Transaction.objects.filter(seller=shop_object,
                                                                                DateAdded__year=this_year,
                                                                                DateAdded__month=this_month,
                                                                                DateAdded__day=this_day):
                        total_sell += this_day_sell_transaction.total_amount
                        total_due += this_day_sell_transaction.total_due
                        total_paid += this_day_sell_transaction.total_paid
                        count += 1

                    total_purchase = 0
                    total_purchase_due = 0
                    total_purchase_paid = 0
                    for this_day_purchase_transaction in Transaction.objects.filter(buyer=shop_object,
                                                                                    DateAdded__year=this_year,
                                                                                    DateAdded__month=this_month,
                                                                                    DateAdded__day=this_day):
                        total_purchase += this_day_purchase_transaction.total_amount
                        total_purchase_due += this_day_purchase_transaction.total_due
                        total_purchase_paid += this_day_purchase_transaction.total_paid
                        count += 1

                if count > 0:
                    output += '["%s/%s/%s","%s","%s","%s","%s","%s","%s"] ,' % (this_day, this_month, this_year,
                                                                                total_sell, total_paid, total_due,
                                                                                total_purchase, total_purchase_paid,
                                                                                total_purchase_due)
                    count = 0
                    # this_day += 1
                    # this_month = this_month + 1
    if get_data['t'] == '2':
        for this_day_transaction in Transaction.objects.filter(Q(seller=shop_object) | Q(buyer=shop_object)):
            # start counting for this product
            id = this_day_transaction.pk
            date = this_day_transaction.DateAdded
            if this_day_transaction.seller == shop_object:
                with_trade = this_day_transaction.buyer
                trade_type = 'Sell'
            elif this_day_transaction.buyer == shop_object:
                with_trade = this_day_transaction.seller
                trade_type = 'Buy'
            number_of_items = ProductsInTransaction.objects.filter(TID=this_day_transaction).count()
            total_amount = this_day_transaction.total_amount
            total_paid = this_day_transaction.total_paid
            total_due = this_day_transaction.total_due

            output += '["%s","%s","%s","%s","%s","%s","%s","%s"] ,' % (id, date, with_trade, trade_type,
                                                                       number_of_items, total_amount,
                                                                       total_paid, total_due)

    output = output[:-1]
    output += ']}'
    return HttpResponse(output, content_type="text/plain")


@login_required(login_url='/login/')
def report_sales_analysis(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    shop_id = shop_object.id
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_sales_analysis.html', {'shop_list_base': all_shop_for_base,
                                                                'shop_name': shop_name,
                                                                'all_consumer_for_base' :all_consumer_for_base,
                                                                'shop_id': shop_id,
                                                                'bangla': bangla,
                                                                'transcriber_name': transcriber_name,
                                                                'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_sales_analysis_json(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(id=shop_name)

    shop_inventory = BuySellProfitInventoryIndividual.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    output = '{"data": [ '

    if get_data['t'] == '1':
        rank = 1
        for a_product in Product.objects.all():
            count = 0
            product_price = 0
            product_name = a_product.name
            for this_day_transaction in Transaction.objects.filter(seller=shop_object):
                # start counting for this product
                for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):
                    if product_in_this_transaction.product == a_product:
                        if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                            if a_product.bulk_to_retail_unit == 0:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit
                            else:
                                count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                        else:
                            count = count + product_in_this_transaction.quantity
                            product_price = product_price + product_in_this_transaction.price_per_unit

            if count > 0:
                output += '["%s","%s","%s"] ,' % (rank, product_name, str(count) + ' ' + a_product.retail_unit)
                rank += 1
    if get_data['t'] == '2':
        rank = 1
        for a_product in Product.objects.all():
            count = 0

            product_price = 0
            previous_product_price = 0
            change = 0
            product_name = a_product.name
            for this_day_transaction in Transaction.objects.filter(seller=shop_object):
                # start counting for this product
                for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):
                    if product_in_this_transaction.product == a_product:
                        if count == 0:
                            previous_product_price = product_in_this_transaction.price_per_unit
                        product_price = product_in_this_transaction.price_per_unit
                        change += abs(previous_product_price - product_price)
                        count += 1
            if count > 0:
                output += '["%s","%s","%s","%s"] ,' % (rank, product_name, count,
                                                       change/count)
                rank += 1
    if get_data['t'] == '3':
        this_year = datetime.date.today().year
        this_month = datetime.date.today().month
        day = 1

        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        while day < 32:
            day_string = True
            rank = 1
            for a_product in Product.objects.all():
                count = 0
                product_price = 0
                product_name = a_product.name

                for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__year=this_year,
                                                                       DateAdded__month=this_month, DateAdded__day=day):
                    # start counting for this product

                    for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):

                        if product_in_this_transaction.product == a_product:
                            if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                                if a_product.bulk_to_retail_unit == 0:
                                    count = count + product_in_this_transaction.quantity
                                    product_price = product_price + product_in_this_transaction.price_per_unit
                                else:
                                    count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                    product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                            else:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit

                if count > 0:
                    if day_string:
                        output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
                        day_string = False
                    output += '["","%s","%s","%s","%s"] ,' % (rank, product_name,
                                                              str(count) + ' ' + a_product.retail_unit,
                                                              float(product_price / count))
                    rank += 1
            day += 1
            # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
    if get_data['t'] == '4':
        day = 1

        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        while day < 8:
            day_string = True
            rank = 1
            for a_product in Product.objects.all():
                count = 0
                product_price = 0
                product_name = a_product.name

                for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__week_day=day):
                    # start counting for this product

                    for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):

                        if product_in_this_transaction.product == a_product:
                            if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                                if a_product.bulk_to_retail_unit == 0:
                                    count = count + product_in_this_transaction.quantity
                                    product_price = product_price + product_in_this_transaction.price_per_unit
                                else:
                                    count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                    product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                            else:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit

                if count > 0:
                    if day_string:
                        if day == 1:
                            output += '["%s","","","",""] ,' % 'Sunday'
                        elif day == 2:
                            output += '["%s","","","",""] ,' % 'Monday'
                        elif day == 3:
                            output += '["%s","","","",""] ,' % 'Tuesday'
                        elif day == 4:
                            output += '["%s","","","",""] ,' % 'Wednesday'
                        elif day == 5:
                            output += '["%s","","","",""] ,' % 'Thursday'
                        elif day == 6:
                            output += '["%s","","","",""] ,' % 'Friday'
                        elif day == 7:
                            output += '["%s","","","",""] ,' % 'Saturday'
                        day_string = False
                    output += '["","%s","%s","%s","%s"] ,' % (rank, product_name,
                                                              str(count) + ' ' + a_product.retail_unit,
                                                              float(product_price / count))
                    rank += 1
            day += 1
    if get_data['t'] == '5':
        this_year = datetime.date.today().year
        day_string = True
        for a_product in Product.objects.all():
            count = 0
            product_profit = 0
            product_name = a_product.name
            for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object):
                # start counting for this product
                if this_day_transaction.product == a_product:
                    product_profit += this_day_transaction.profit
                    count += 1
            output += '["%s","%s"] ,' % (product_name, product_profit)
    output = output[:-1]
    output += ']}'
    return HttpResponse(output, content_type="text/plain")


@login_required(login_url='/login/')
def report_payment(request):
    get_data = request.GET
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False

    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    sell_transaction_with_due = Transaction.objects.filter(seller_id=shop_object, total_due__lte=0)
    buy_transaction_with_due = Transaction.objects.filter(buyer_id=shop_object, total_due__lte=0)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    buyer_account = BuyerSellerAccount.objects.filter(seller=shop_object,  total_due__lte=0)
    seller_account = BuyerSellerAccount.objects.filter(buyer=shop_object,  total_due__lte=0)
    all_user_for_base = Consumer.objects.all()
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    transcriber_name = request.session['user']
    return render(request, 'pages/report_payment.html', {'shop_list_base': all_shop_for_base,
                                                         'sell_transaction_with_due': sell_transaction_with_due,
                                                         'buy_transaction_with_due': buy_transaction_with_due,
                                                         'all_consumer_for_base' :all_consumer_for_base,
                                                         'buyer_account': buyer_account,
                                                         'transcriber_name': transcriber_name,
                                                         'seller_account': seller_account,
                                                         'shop_name': shop_name,
                                                         'bangla': bangla,
                                                         'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_due(request):
    get_data = request.GET
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    sell_transaction_with_due = Transaction.objects.filter(seller_id=shop_object, total_due__gt=0)
    buy_transaction_with_due = Transaction.objects.filter(buyer_id=shop_object, total_due__gt=0)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    buyer_account = SMSPayment.objects.filter(seller=shop_object)
    seller_account = SMSPayment.objects.filter(buyer=shop_object)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_due.html', {'shop_list_base': all_shop_for_base,
                                                     'sell_transaction_with_due': sell_transaction_with_due,
                                                     'buy_transaction_with_due': buy_transaction_with_due,
                                                     'buyer_account': buyer_account,
                                                     'all_consumer_for_base' :all_consumer_for_base,
                                                     'bangla': bangla,
                                                     'seller_account': seller_account,
                                                     'transcriber_name': transcriber_name,
                                                     'shop_name': shop_name,
                                                     'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_profit(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    shop_id = shop_object.id
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_profit.html', {'shop_list_base': all_shop_for_base,
                                                        'shop_name': shop_name,
                                                        'shop_id': shop_id,
                                                        'all_consumer_for_base' :all_consumer_for_base,
                                                        'bangla': bangla,
                                                        'transcriber_name': transcriber_name,
                                                        'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_profit_json(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(id=shop_name)
    shop_inventory = BuySellProfitInventoryIndividual.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    output = '{"data": [ '

    if get_data['t'] == '1':
        this_year = datetime.date.today().year
        this_month = 1
        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        while this_month < 13:
            day_string = True
            for a_product in Product.objects.all():
                count = 0
                product_profit = 0
                product_name = a_product.name
                for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object,
                                                                                            DateAdded__year=this_year,
                                                                                            DateAdded__month=this_month):
                    # start counting for this product
                    if this_day_transaction.product == a_product:
                        product_profit += this_day_transaction.profit
                        count += 1

                if count > 0:
                    if day_string:
                        if this_month == 1:
                            output += '["January","",""], '
                        elif this_month == 2:
                            output += '["February","",""], '
                        elif this_month == 3:
                            output += '["March","",""], '
                        elif this_month == 4:
                            output += '["April","",""], '
                        elif this_month == 5:
                            output += '["May","",""], '
                        elif this_month == 6:
                            output += '["June","",""], '
                        elif this_month == 7:
                            output += '["July","",""], '
                        elif this_month == 8:
                            output += '["August","",""], '
                        elif this_month == 9:
                            output += '["September","",""], '
                        elif this_month == 10:
                            output += '["October","",""], '
                        elif this_month == 11:
                            output += '["November","",""], '
                        elif this_month == 12:
                            output += '["December","",""], '
                        day_string = False
                    output += '["","%s","%s"] ,' % (product_name, product_profit)
            # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
            this_month += 1
    if get_data['t'] == '2':
        this_year = datetime.date.today().year
        this_month = 1

        while this_month < 13:
            day = 1
            while day < 32:
                day_string = True
                for a_product in Product.objects.all():
                    count = 0
                    product_profit = 0
                    product_name = a_product.name
                    for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object,
                                                                                                DateAdded__year=this_year,
                                                                                                DateAdded__month=this_month,
                                                                                                DateAdded__day=day):
                        # start counting for this product
                        if this_day_transaction.product == a_product:
                            product_profit += this_day_transaction.profit
                            count += 1

                    if count > 0:
                        if day_string:
                            output += '["%s/%s/%s","",""] ,' % (day, this_month, this_year)
                            day_string = False
                        output += '["","%s","%s"] ,' % (product_name, product_profit)
                day += 1
            this_month += 1
    if get_data['t'] == '3':
        this_year = datetime.date.today().year
        this_month = datetime.date.today().month
        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        day_string = True
        for a_product in Product.objects.all():
            count = 0
            product_profit = 0
            product_name = a_product.name
            for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object,
                                                                                        DateAdded__year=this_year,
                                                                                        DateAdded__month=this_month):
                # start counting for this product
                if this_day_transaction.product == a_product:
                    product_profit += this_day_transaction.profit
                    count += 1
            output += '["%s","%s"] ,' % (product_name, product_profit)
            # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
    if get_data['t'] == '4':
        this_year = datetime.date.today().year
        day_string = True
        for a_product in Product.objects.all():
            count = 0
            product_profit = 0
            product_name = a_product.name
            for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object,
                                                                                        DateAdded__year=this_year):
                # start counting for this product
                if this_day_transaction.product == a_product:
                    product_profit += this_day_transaction.profit
                    count += 1
            output += '["%s","%s"] ,' % (product_name, product_profit)
    if get_data['t'] == '5':
        this_year = datetime.date.today().year
        day_string = True
        for a_product in Product.objects.all():
            count = 0
            product_profit = 0
            product_name = a_product.name
            for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object):
                # start counting for this product
                if this_day_transaction.product == a_product:
                    product_profit += this_day_transaction.profit
                    count += 1
            output += '["%s","%s"] ,' % (product_name, product_profit)
    output = output[:-1]
    output += ']}'
    return HttpResponse(output, content_type="text/plain")





@login_required(login_url='/login/')
def report_product(request):

    get_data = request.GET
    shop_name = get_data['shop']
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False
    shop_object = Consumer.objects.get(name=shop_name)
    shop_id = shop_object.id
    shop_inventory = Inventory.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    selected_products = ProductsInTransaction.objects.filter(TID=Transaction.objects.filter(seller=shop_object))

    selected_products_buy = ProductsInTransaction.objects.filter(TID=Transaction.objects.filter(buyer=shop_object))
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_product.html', {'shop_list_base': all_shop_for_base,
                                                         'shop_inventory': shop_inventory,
                                                         'shop_name': shop_name,
                                                         'shop_id': shop_id,
                                                         'bangla': bangla,
                                                         'all_consumer_for_base' :all_consumer_for_base,
                                                         'transcriber_name': transcriber_name,
                                                         'selected_products_buy': selected_products_buy,
                                                         'selected_products': selected_products,
                                                         'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_product_json(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(id=shop_name)
    shop_inventory = Inventory.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    output = '{"data": [ '

    if get_data['t'] == '1':
        this_year = datetime.date.today().year
        this_month = datetime.date.today().month
        day = 1

        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        while day < 32:
            day_string = True
            for a_product in Product.objects.all():
                count = 0
                product_price = 0
                product_name = a_product.name
                for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__year=this_year,
                                                                       DateAdded__month=this_month, DateAdded__day=day):
                    # start counting for this product

                    for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):

                        if product_in_this_transaction.product == a_product:
                            # if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                            #     if a_product.bulk_to_retail_unit == 0:
                            #         count = count + product_in_this_transaction.quantity
                            #         product_price = product_price + product_in_this_transaction.price_per_unit
                            #     else:
                            #         count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                            #         product_price = product_price + product_in_this_transaction.price_per_unit
                            # else:
                            count = count + product_in_this_transaction.quantity
                            product_price = product_price + product_in_this_transaction.price_per_unit * product_in_this_transaction.quantity

                if count > 0:
                    if day_string:
                        output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
                        day_string = False
                    output += '["","%s","%s","%s","%s"] ,' % (product_name, count,
                                                              a_product.retail_unit,
                                                              float(product_price / count))
            day += 1
            # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
    if get_data['t'] == '2':
        this_year = datetime.date.today().year
        this_month = datetime.date.today().month
        day = 1
        while day < 32:
            day_string = True
            for a_product in Product.objects.all():
                count = 0
                product_price = 0
                product_name = a_product.name
                for this_day_transaction in Transaction.objects.filter(buyer=shop_object, DateAdded__year=this_year,
                                                                       DateAdded__month=this_month, DateAdded__day=day):
                    # start counting for this product

                    for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):

                        if product_in_this_transaction.product == a_product:
                            if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                                if a_product.bulk_to_retail_unit == 0:
                                    count = count + product_in_this_transaction.quantity
                                    product_price = product_price + product_in_this_transaction.price_per_unit
                                else:
                                    count = count + product_in_this_transaction.quantity
                                    product_price = product_price + product_in_this_transaction.price_per_unit
                            else:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit

                if count > 0:
                    if day_string:
                        output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
                        day_string = False
                    output += '["","%s","%s","%s","%s"] ,' % (product_name, count,
                                                              a_product.bulk_wholesale_unit,
                                                              float(product_price / count))
            day += 1
    if get_data['t'] == '3':
        this_year = datetime.date.today().year
        this_month = datetime.date.today().month
        for a_product in Product.objects.all():
            count = 0
            product_price = 0
            product_name = a_product.name
            for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__year=this_year, DateAdded__month=this_month):
                # start counting for this product
                for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):
                    if product_in_this_transaction.product == a_product:
                        if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                            if a_product.bulk_to_retail_unit == 0:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit
                            else:
                                count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                        else:
                            count = count + product_in_this_transaction.quantity
                            product_price = product_price + product_in_this_transaction.price_per_unit

            if count > 0:
                output += '["%s","%s","%s","%s"] ,' % (product_name, count,
                                                       a_product.retail_unit,
                                                       float(product_price / count))
    if get_data['t'] == '4':
        this_year = datetime.date.today().year
        this_month = datetime.date.today().month
        for a_product in Product.objects.all():
            count = 0
            product_price = 0
            product_name = a_product.name
            for this_day_transaction in Transaction.objects.filter(buyer=shop_object, DateAdded__year=this_year, DateAdded__month=this_month):
                # start counting for this product
                for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):
                    if product_in_this_transaction.product == a_product:
                        if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                            if a_product.bulk_to_retail_unit == 0:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit
                            else:
                                count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                        else:
                            count = count + product_in_this_transaction.quantity
                            product_price = product_price + product_in_this_transaction.price_per_unit

            if count > 0:
                output += '["%s","%s","%s","%s"] ,' % (product_name, count,
                                                       a_product.retail_unit,
                                                       float(product_price / count))
    output = output[:-1]
    output += ']}'
    selected_products_buy = ProductsInTransaction.objects.filter(TID=Transaction.objects.filter(buyer=shop_object))
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    return HttpResponse(output, content_type="text/plain")



# paste the template name of the report_analytical instead of report_product here
@login_required(login_url='/login/')
def report_analytical(request):
    all_product = Product.objects.all()
    final_output = ''
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    shop_id = shop_object.id
    for product in all_product:
        print(product.name)
        if ProductsInTransaction.objects.filter(product=product).exists():
            product_output = "[%s, " % product.name
            sold_amount = 0
            for product_details in ProductsInTransaction.objects.filter(product=product):
                sold_amount = sold_amount + product_details.quantity
            product_output += str(sold_amount)
            final_output += product_output
        final_output += "] ,"
    print(final_output)
    final_output = final_output[:-1]
    print(final_output)
    add_notification = False
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/reports_analytical.html',
                  {'all_product': all_product, 'add_notification': add_notification,
                   'shop_list_base': all_shop_for_base, 'product_sell': final_output,
                   'all_consumer_for_base' :all_consumer_for_base,
                   'transcriber_name': transcriber_name,
                   'shop_name': shop_name,
                   'shop_id': shop_id,
                   'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_analytical_json(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(id=shop_name)
    if get_data['t'] == '1':
        all_product = Product.objects.all()
        final_output = '{"cols": [ { "id": "", "label": "Topping", "pattern": "", "type": "string" }, ' \
                       '{ "id": "", "label": "Units", "pattern": "", "type": "number" } ], "rows": [ '
        for product in all_product:
            print(product.name)
            if ProductsInTransaction.objects.filter(product=product).exists():
                product_name = product.name
                sold_amount = 0
                for transaction_id in Transaction.objects.filter(seller=shop_object):
                    for product_details in ProductsInTransaction.objects.filter(product=product, TID=transaction_id):
                        sold_amount = sold_amount + product_details.quantity
                final_output += '{"c": [{"v": "%s","f": null},{"v": %s,"f": null}]},' % (product_name,
                                                                                         sold_amount)
        final_output = final_output[:-1]
        print(final_output)
    if get_data['t'] == '2':
        all_product = BuySellProfitInventory.objects.filter(shop=shop_object)
        final_output = '{"cols": [ { "id": "", "label": "Topping", "pattern": "", "type": "string" }, ' \
                       '{ "id": "", "label": "Profit", "pattern": "", "type": "number" } ], "rows": [ '
        for product in all_product:
            final_output += '{"c": [{"v": "%s","f": null},{"v": %s,"f": null}]},' % (product.product,
                                                                                     product.profit)
        final_output = final_output[:-1]
        print(final_output)
    final_output += ']}'
    print(final_output)
    return HttpResponse(final_output, content_type="text/plain")


# till this views created based on the list from mail
@login_required(login_url='/login/')
def report_recharge(request):
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_recharge.html', {'shop_list_base': all_shop_for_base,
                                                          'all_consumer_for_base' :all_consumer_for_base,
                                                          'transcriber_name': transcriber_name,
                                                          'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_callduration(request):
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_callduration_graph.html', {'shop_list_base': all_shop_for_base,
                                                                    'all_consumer_for_base' :all_consumer_for_base,
                                                                    'transcriber_name': transcriber_name,
                                                                    'all_user_for_base': all_user_for_base})

# not necessary
@login_required(login_url='/login/')
def report_transaction(request):
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_transaction.html', {'shop_list_base': all_shop_for_base,
                                                             'all_consumer_for_base' :all_consumer_for_base,
                                                             'transcriber_name': transcriber_name,
                                                             'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_calltranscription(request):
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_transcription.html', {'shop_list_base': all_shop_for_base,
                                                               'all_consumer_for_base' :all_consumer_for_base,
                                                               'transcriber_name': transcriber_name,
                                                               'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_usercall(request):
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_user_call_recharge.html', {'shop_list_base': all_shop_for_base,
                                                                    'transcriber_name': transcriber_name,
                                                                    'all_consumer_for_base' :all_consumer_for_base,
                                                                    'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def transcription_page(request):
    print(request.POST)
    number_of_pending_calls = VoiceRecord.objects.filter(transcribed=False).count()
    number_of_pending_reg_calls = VoiceReg.objects.filter(completed=False).count()

    type_of_subscriber = ConsumerType.objects.all()
    number_of_fail_calls = VoiceRecord.objects.filter(with_error=True).count()
    number_of_completed_calls = VoiceRecord.objects.filter(with_error=False, transcribed=True).count()
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    return render(request, 'pages/transcription.html',
                  dict(pending_calls=number_of_pending_calls, types=type_of_subscriber,
                       pending_calls_reg=number_of_pending_reg_calls, number_of_fail_calls=str(number_of_fail_calls),
                       number_of_completed_calls=number_of_completed_calls, transcriber_name=transcriber_name,
                       shop_list_base=all_shop_for_base,all_consumer_for_base=all_consumer_for_base,
                       all_user_for_base=all_user_for_base))


# report views ends here


@login_required(login_url='/login/')
def add_subscriber_page(request):
    all_subscriber = Consumer.objects.all()
    type_of_subscriber = ConsumerType.objects.all()
    add_notification = False
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)
    notification = ''
    if 'delete' in request.GET:
        get_data = request.GET
        add_notification = True
        delID = get_data['delete']
        if Consumer.objects.filter(id=delID).exists():
            item_for_delete = Consumer.objects.get(id=delID)
            notification = 'Daily statement for the user : ' + item_for_delete.name + ' is sent successfully.'
            # item_for_delete.delete()
            sales_statement = ''
            purchase_statement = ''
            today_date = datetime.date.today()
            today_day = today_date.day
            today_month = today_date.month
            today_year = today_date.year
            # for selling
            sell_transactions = Transaction.objects.filter(seller=item_for_delete, DateAdded__day=today_day,
                                                           DateAdded__month=today_month, DateAdded__year=today_year)
            total_sales = 0
            total_due = 0
            total_paid = 0
            for sell_transaction in sell_transactions:
                total_sales += sell_transaction.total_amount
                total_paid += sell_transaction.total_paid
                total_due += sell_transaction.total_due
            if total_sales > 0:
                sales_statement = ' bikroy korechen mot: ' + str(total_sales) + ' takar. nogod peyechen : ' + \
                                  str(total_paid) + ' taka ebong baki royeche ' + str(total_due) + ' taka.'
            buy_transactions = Transaction.objects.filter(buyer=item_for_delete, DateAdded__day=today_day,
                                                          DateAdded__month=today_month, DateAdded__year=today_year)
            total_purchase = 0
            total_due = 0
            total_paid = 0
            for buy_transaction in buy_transactions:
                total_purchase += buy_transaction.total_amount
                total_paid += buy_transaction.total_paid
                total_due += buy_transaction.total_due
            if total_purchase > 0:
                purchase_statement = ' kinechen mot: ' + str(total_purchase) + ' takar. Nogod diyechen : ' + \
                                     str(total_paid) + ' taka ebong baki royeche ' + str(total_due) + ' taka.'
            final_text = 'Aj apni' + sales_statement + purchase_statement + ' Dhonnobad'

            if total_purchase > 0 or total_sales > 0:
                print(final_text)
                send_sms(final_text, item_for_delete.phone)

        else:
            notification = 'Item not found'

    return render(request, 'pages/add_subscriber.html',
                  {'subscribers': all_subscriber, 'types': type_of_subscriber, 'add_notification': add_notification,
                   'shop_list_base': all_shop_for_base,
                   'all_consumer_for_base' :all_consumer_for_base,
                   'transcriber_name': transcriber_name,
                   'notification':notification,
                   'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def add_product_page(request):
    all_product = Product.objects.all()
    add_notification = False
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)
    notification = ''
    if 'delete' in request.GET:
        get_data = request.GET
        add_notification = True
        delID = get_data['delete']
        if Product.objects.filter(id=delID).exists():
            item_for_delete = Product.objects.get(id=delID)
            notification = 'The product : ' + item_for_delete.name + ' is deleted successfully.'
            item_for_delete.delete()
        else:
            notification = 'Item not found'

    return render(request, 'pages/add_product.html',
                  {'all_product': all_product, 'add_notification': add_notification,
                   'all_consumer_for_base' :all_consumer_for_base,
                   'transcriber_name': transcriber_name,'notification': notification,
                   'shop_list_base': all_shop_for_base, 'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_transcriber_performance(request):
    all_product = Product.objects.all()
    add_notification = False
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_transcriber_performance.html',
                  {'all_product': all_product, 'add_notification': add_notification,
                   'transcriber_name': transcriber_name,
                   'all_consumer_for_base' :all_consumer_for_base,
                   'shop_list_base': all_shop_for_base, 'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_transcriber_performance_json(request):
    final_output = '{"data": [ '
    for transcriber in Transcriber.objects.all():
        number_of_transcriptions = TranscriberInTranscription.objects.filter(name=transcriber).count()
        total_time_taken = 0
        total_product_trancribed = 0
        for transcriber_in_transaction in TranscriberInTranscription.objects.filter(name=transcriber):
            total_time_taken += float(transcriber_in_transaction.time_taken)
            total_product_trancribed += transcriber_in_transaction.number_of_products
        if number_of_transcriptions > 0:
            avg_time = total_time_taken / number_of_transcriptions
            avg_product = total_product_trancribed / number_of_transcriptions
            final_output += '["%s","%s","%s","%s","%s"] ,' % (transcriber.id, transcriber.name,
                                                              number_of_transcriptions, avg_time, avg_product)
    final_output = final_output[:-1]
    final_output += ']}'
    return HttpResponse(final_output, content_type="text/plain")


@login_required(login_url='/login/')
def user_balance_recharge(request):
    post_data = request.POST
    notification = ''
    for all_consumers in Consumer.objects.all():
        if Recharge.objects.filter(user=all_consumers).exists():
            print('Already_Added')
        else:
            new_added = Recharge(user=all_consumers)
            new_added.save()

        if TotalRecharge.objects.filter(user=all_consumers).exists():
            print('Already_Added')
        else:
            new_added = TotalRecharge(user=all_consumers)
            new_added.save()
    add_notification = False
    if 'user' in post_data and 'recharge_amount' in post_data:
        user_name = post_data['user']
        user_object = Consumer.objects.get(name=user_name)
        if is_number(post_data['recharge_amount']) or is_float(post_data['recharge_amount']):
            new_recharge_added = Recharge(user=user_object, amount=float(post_data['recharge_amount']))
            new_recharge_added.save()
            new_recharge_update = TotalRecharge.objects.get(user=user_object)
            new_recharge_update.amount += float(post_data['recharge_amount'])
            new_recharge_update.save()
            add_notification = True
            notification = 'Amount %s has been added to the number %s' %(post_data['recharge_amount'],
                                                                         user_object.phone)
        else:
            notification = 'Something went wrong. Please try again.'
    recharge_all = TotalRecharge.objects.all()
    today_date = datetime.date.today()
    today_day = today_date.day
    today_month = today_date.month
    today_year = today_date.year
    recharge_today = Recharge.objects.filter(DateAdded__day=today_day,
                                             DateAdded__month=today_month, DateAdded__year=today_year, amount__gt=0)
    all_product = Product.objects.all()
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'pages/report_user_call_recharge.html',
                  {'all_product': all_product, 'add_notification': add_notification,
                   'all_consumer_for_base' :all_consumer_for_base,
                   'shop_list_base': all_shop_for_base, 'recharge_all': recharge_all,
                   'transcriber_name': transcriber_name,
                   'recharge_today': recharge_today, 'all_user_for_base': all_user_for_base,
                   'notification': notification})
# views for printing


@login_required(login_url='/login/')
def report_monthly_shop_print(request):
    get_data = request.GET
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False

    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    total_sell = 0
    total_sell_due = 0
    total_sell_paid = 0
    total_purchase = 0
    total_purchase_due = 0
    total_purchase_paid = 0
    for month_sell in BuyerSellerAccount.objects.filter(seller=shop_object):
        total_sell += month_sell.total_amount_of_transaction
        total_sell_due += month_sell.total_due
        total_sell_paid += month_sell.total_paid
    for month_purchase in BuyerSellerAccount.objects.filter(buyer=shop_object):
        total_purchase += month_purchase.total_amount_of_transaction
        total_purchase_due += month_purchase.total_due
        total_purchase_paid += month_purchase.total_paid
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    transcriber_name = request.session['user']
    return render(request, 'print/report_monthly_shop.html', {'shop_list_base': all_shop_for_base,
                                                              'shop_name': shop_name,
                                                              'all_consumer_for_base' :all_consumer_for_base,
                                                              'total_sell': total_sell,
                                                              'transcriber_name': transcriber_name,
                                                              'total_sell_due': total_sell_due,
                                                              'total_sell_paid': total_sell_paid,
                                                              'bangla': bangla,
                                                              'total_purchase': total_purchase,
                                                              'total_purchase_due': total_purchase_due,
                                                              'total_purchase_paid': total_purchase_paid,
                                                              'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_due_print(request):
    get_data = request.GET
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    sell_transaction_with_due = Transaction.objects.filter(seller_id=shop_object, total_due__gt=0)
    buy_transaction_with_due = Transaction.objects.filter(buyer_id=shop_object, total_due__gt=0)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    buyer_account = BuyerSellerAccount.objects.filter(seller=shop_object,  total_due__gt=0)
    seller_account = BuyerSellerAccount.objects.filter(buyer=shop_object,  total_due__gt=0)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'print/report_due.html', {'shop_list_base': all_shop_for_base,
                                                     'sell_transaction_with_due': sell_transaction_with_due,
                                                     'buy_transaction_with_due': buy_transaction_with_due,
                                                     'buyer_account': buyer_account,
                                                     'all_consumer_for_base' :all_consumer_for_base,
                                                     'bangla': bangla,
                                                     'seller_account': seller_account,
                                                     'transcriber_name': transcriber_name,
                                                     'shop_name': shop_name,
                                                     'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_payment_print(request):
    get_data = request.GET
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False

    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(name=shop_name)
    sell_transaction_with_due = Transaction.objects.filter(seller_id=shop_object, total_due__lte=0)
    buy_transaction_with_due = Transaction.objects.filter(buyer_id=shop_object, total_due__lte=0)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    buyer_account = BuyerSellerAccount.objects.filter(seller=shop_object,  total_due__lte=0)
    seller_account = BuyerSellerAccount.objects.filter(buyer=shop_object,  total_due__lte=0)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'print/report_payment.html', {'shop_list_base': all_shop_for_base,
                                                         'sell_transaction_with_due': sell_transaction_with_due,
                                                         'buy_transaction_with_due': buy_transaction_with_due,
                                                         'all_consumer_for_base' :all_consumer_for_base,
                                                         'buyer_account': buyer_account,
                                                         'transcriber_name': transcriber_name,
                                                         'seller_account': seller_account,
                                                         'shop_name': shop_name,
                                                         'bangla': bangla,
                                                         'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_product_print(request):

    get_data = request.GET
    shop_name = get_data['shop']
    if 'ban' in get_data:
        bangla = True
    else:
        bangla = False
    shop_object = Consumer.objects.get(name=shop_name)
    shop_inventory = Inventory.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    selected_products = ProductsInTransaction.objects.filter(TID=Transaction.objects.filter(seller=shop_object))

    selected_products_buy = ProductsInTransaction.objects.filter(TID=Transaction.objects.filter(buyer=shop_object))
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'print/report_product.html', {'shop_list_base': all_shop_for_base,
                                                         'shop_inventory': shop_inventory,
                                                         'shop_name': shop_name,
                                                         'bangla': bangla,
                                                         'all_consumer_for_base' :all_consumer_for_base,
                                                         'transcriber_name': transcriber_name,
                                                         'selected_products_buy': selected_products_buy,
                                                         'selected_products': selected_products,
                                                         'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_sales_analysis_print(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    transcriber_name = request.session['user']
    return render(request, 'print/report_sales_analysis.html', {'shop_list_base': all_shop_for_base,
                                                                'all_consumer_for_base' :all_consumer_for_base,
                                                                'shop_name': shop_name,
                                                                'transcriber_name': transcriber_name,
                                                                'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_profit_print(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'print/report_profit.html', {'shop_list_base': all_shop_for_base,
                                                        'shop_name': shop_name,
                                                        'all_consumer_for_base':all_consumer_for_base,
                                                        'transcriber_name': transcriber_name,
                                                        'all_user_for_base': all_user_for_base})


@login_required(login_url='/login/')
def report_transcriber_performance_print(request):
    all_product = Product.objects.all()
    add_notification = False
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    transcriber_name = request.session['user']
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    return render(request, 'print/report_transcriber_performance.html',
                  {'all_product': all_product, 'add_notification': add_notification,
                   'all_consumer_for_base':all_consumer_for_base,
                   'transcriber_name': transcriber_name,
                   'shop_list_base': all_shop_for_base, 'all_user_for_base': all_user_for_base})


# SR section

@login_required(login_url='/login/')
def sr_monthly_report(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name
    allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)

    return render(request, 'pages/SR/report_monthly.html', {'transcriber_name': transcriber_name,
                                                            'allTransaction': allTransaction})


@login_required(login_url='/login/')
def sr_due_report(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name
    allBalance = BuyerSellerAccount.objects.filter(seller=sr_object)
    sell_transaction = Transaction.objects.filter(seller=sr_object)
    dueTransactions = dueTransaction.objects.filter(seller=sr_object)

    return render(request, 'pages/SR/report_due.html', {'transcriber_name': transcriber_name,
                                                        'sell_transaction': sell_transaction,
                                                        'dueTransactions': dueTransactions,
                                                        'allBalance': allBalance})


@login_required(login_url='/login/')
def sr_report_sales_analysis(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name

    post_data = request.POST
    print(post_data)
    shop_object = sr_object
    shop_name = shop_object.name
    shop_id = shop_object.id
    if 'month' in post_data and 'year' in post_data:
        month = post_data['month']
        year = post_data['year']
    else:
        month = datetime.date.today().month
        year = datetime.date.today().year
    return render(request, 'pages/SR/report_sales_analysis.html', {'shop_name': shop_name,
                                                                   # 'all_consumer_for_base' :all_consumer_for_base,
                                                                   'shop_id': shop_id,
                                                                   # 'bangla': bangla,
                                                                   'transcriber_name': transcriber_name,
                                                                   'month': month,
                                                                   'year': year})


@login_required(login_url='/login/')
def sr_report_sales_analysis_json(request):
    get_data = request.GET
    shop_name = get_data['shop']
    shop_object = Consumer.objects.get(id=shop_name)

    shop_inventory = BuySellProfitInventoryIndividual.objects.filter(shop=shop_object)
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    this_year = get_data['year']
    print(this_year)
    this_month = get_data['month']
    output = '{"data": [ '

    if get_data['t'] == '1':
        rank = 1
        for a_product in Product.objects.all():
            count = 0
            product_price = 0
            product_name = a_product.name
            for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__year=this_year,
                                                                   DateAdded__month=this_month):
                # start counting for this product
                for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):
                    if product_in_this_transaction.product == a_product:
                        if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                            if a_product.bulk_to_retail_unit == 0:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit
                            else:
                                count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                        else:
                            count = count + product_in_this_transaction.quantity
                            product_price = product_price + product_in_this_transaction.price_per_unit

            if count > 0:
                output += '["%s","%s","%s"] ,' % (rank, product_name, str(count) + ' ' + a_product.retail_unit)
                rank += 1
    if get_data['t'] == '2':
        rank = 1
        for a_product in Product.objects.all():
            count = 0
            # product_price = 0
            previous_product_price = 0
            change = 0
            product_name = a_product.name
            for this_day_transaction in Transaction.objects.filter(seller=shop_object):
                # start counting for this product
                for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):
                    if product_in_this_transaction.product == a_product:
                        if count == 0:
                            previous_product_price = product_in_this_transaction.price_per_unit
                        product_price = product_in_this_transaction.price_per_unit
                        change += abs(previous_product_price - product_price)
                        count += 1
            if count > 0:
                output += '["%s","%s","%s","%s"] ,' % (rank, product_name, count,
                                                       change/count)
                rank += 1
    if get_data['t'] == '3':

        print(this_month)
        day = 1
        #
        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        while day < 32:
            day_string = True
            rank = 1
            for a_product in Product.objects.all():
                count = 0
                product_price = 0
                product_name = a_product.name

                for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__year=this_year,
                                                                       DateAdded__month=this_month, DateAdded__day=day):
                    # start counting for this product

                    for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):

                        if product_in_this_transaction.product == a_product:
                            if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                                if a_product.bulk_to_retail_unit == 0:
                                    count = count + product_in_this_transaction.quantity
                                    product_price = product_price + product_in_this_transaction.price_per_unit
                                else:
                                    count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                    product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                            else:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit

                if count > 0:
                    if day_string:
                        output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
                        day_string = False
                    output += '["","%s","%s","%s","%s"] ,' % (rank, product_name,
                                                              str(count) + ' ' + a_product.retail_unit,
                                                              float(product_price / count))
                    rank += 1
            day += 1
            # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
    if get_data['t'] == '4':
        day = 1

        # output += '["%s/%s/%s","","","",""] ,' % (day, this_month, this_year)
        while day < 8:
            day_string = True
            rank = 1
            for a_product in Product.objects.all():
                count = 0
                product_price = 0
                product_name = a_product.name

                for this_day_transaction in Transaction.objects.filter(seller=shop_object, DateAdded__week_day=day):
                    # start counting for this product

                    for product_in_this_transaction in ProductsInTransaction.objects.filter(TID=this_day_transaction):

                        if product_in_this_transaction.product == a_product:
                            if product_in_this_transaction.unit == a_product.bulk_wholesale_unit:
                                if a_product.bulk_to_retail_unit == 0:
                                    count = count + product_in_this_transaction.quantity
                                    product_price = product_price + product_in_this_transaction.price_per_unit
                                else:
                                    count = count + product_in_this_transaction.quantity * a_product.bulk_to_retail_unit
                                    product_price = product_price + product_in_this_transaction.price_per_unit / a_product.bulk_to_retail_unit
                            else:
                                count = count + product_in_this_transaction.quantity
                                product_price = product_price + product_in_this_transaction.price_per_unit

                if count > 0:
                    if day_string:
                        if day == 1:
                            output += '["%s","","","",""] ,' % 'Sunday'
                        elif day == 2:
                            output += '["%s","","","",""] ,' % 'Monday'
                        elif day == 3:
                            output += '["%s","","","",""] ,' % 'Tuesday'
                        elif day == 4:
                            output += '["%s","","","",""] ,' % 'Wednesday'
                        elif day == 5:
                            output += '["%s","","","",""] ,' % 'Thursday'
                        elif day == 6:
                            output += '["%s","","","",""] ,' % 'Friday'
                        elif day == 7:
                            output += '["%s","","","",""] ,' % 'Saturday'
                        day_string = False
                    output += '["","%s","%s","%s","%s"] ,' % (rank, product_name,
                                                              str(count) + ' ' + a_product.retail_unit,
                                                              float(product_price / count))
                    rank += 1
            day += 1
    if get_data['t'] == '5':
        this_year = datetime.date.today().year
        day_string = True
        for a_product in Product.objects.all():
            count = 0
            product_profit = 0
            product_name = a_product.name
            for this_day_transaction in BuySellProfitInventoryIndividual.objects.filter(shop_id=shop_object):
                # start counting for this product
                if this_day_transaction.product == a_product:
                    product_profit += this_day_transaction.profit
                    count += 1
            output += '["%s","%s"] ,' % (product_name, product_profit)
    output = output[:-1]
    output += ']}'
    return HttpResponse(output, content_type="text/plain")


# Distributor Section

@login_required(login_url='/login/')
def add_sr_page(request):
    dr_name = request.session['user']
    dr_object = ACL.objects.get(loginID=dr_name).loginUser
    transcriber_name = dr_object.name

    all_subscriber = ACL.objects.filter(distUser=dr_object)
    # type_of_subscriber = ConsumerType.objects.all()
    add_notification = False
    # shop_consumer = ConsumerType.objects.get(type_name='Seller')
    # all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    # all_user_for_base = Consumer.objects.all()
    # transcriber_name = request.session['user']
    # shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    # all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)
    notification = ''
    if 'delete' in request.GET:
        get_data = request.GET
        add_notification = True
        delID = get_data['delete']
        if Consumer.objects.filter(id=delID).exists():
            item_for_delete = Consumer.objects.get(id=delID)
            notification = 'The Consumer : ' + item_for_delete.name + ' is deleted successfully.'
            item_for_delete.delete()
        else:
            notification = 'Item not found'

    return render(request, 'pages/Distributor/add_SR.html',
                  {'subscribers': all_subscriber,'add_notification': add_notification,
                   # 'shop_list_base': all_shop_for_base,
                   # 'all_consumer_for_base' :all_consumer_for_base,
                   'transcriber_name': transcriber_name,
                   'notification': notification})


@login_required(login_url='/login/')
def dr_monthly_report(request):
    dr_name = request.session['user']
    dr_object = ACL.objects.get(loginID=dr_name).loginUser
    transcriber_name = dr_object.name
    transcriber_id = dr_object.id
    all_subscriber = ACL.objects.filter(distUser=dr_object)
    post_data = request.POST
    print(post_data)
    if 'sr' in post_data:
        sr_object = Consumer.objects.get(id=post_data['sr'])
        allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)
        return render(request, 'pages/Distributor/report_monthly.html', {'transcriber_name': transcriber_name,
                                                                         'hasReport': True,
                                                                         'subscribers': all_subscriber,
                                                                         'transcriber_id': transcriber_id,
                                                                         'allTransaction': allTransaction})
    else:
        # allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)
        return render(request, 'pages/Distributor/report_monthly.html', {'transcriber_name': transcriber_name,
                                                                         'transcriber_id': transcriber_id,
                                                                         'subscribers': all_subscriber,
                                                                         'hasReport': False})


@login_required(login_url='/login/')
def dr_due_report(request):
    sr_name = request.session['user']
    dr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = dr_object.name
    transcriber_id = dr_object.id
    all_subscriber = ACL.objects.filter(distUser=dr_object)
    post_data = request.POST
    if 'sr' in post_data:
        sr_object = Consumer.objects.get(id=post_data['sr'])
        allBalance = BuyerSellerAccount.objects.filter(seller=sr_object)
        sell_transaction = Transaction.objects.filter(seller=sr_object)
        dueTransactions = dueTransaction.objects.filter(seller=sr_object)
        # allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)
        return render(request, 'pages/Distributor/report_due.html', {'transcriber_name': transcriber_name,
                                                                     'sell_transaction': sell_transaction,
                                                                     'dueTransactions': dueTransactions,
                                                                     'transcriber_id': transcriber_id,
                                                                     'hasReport': True,
                                                                     'subscribers': all_subscriber,
                                                                     'allBalance': allBalance})

    else:
        # allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)
        return render(request, 'pages/Distributor/report_due.html', {'transcriber_name': transcriber_name,
                                                                     'transcriber_id': transcriber_id,
                                                                     'subscribers': all_subscriber,
                                                                     'hasReport': False})



@login_required(login_url='/login/')
def dr_report_sales_analysis(request):
    dr_name = request.session['user']
    dr_object = ACL.objects.get(loginID=dr_name).loginUser
    transcriber_name = dr_object.name
    transcriber_id = dr_object.id
    post_data = request.POST
    print(post_data)
    # shop_object = sr_object
    #
    all_subscriber = ACL.objects.filter(distUser=dr_object)
    hasReport = False
    if 'sr' in post_data:
        shop_id = post_data['sr']
        shop_name = Consumer.objects.get(id=shop_id).name
        hasReport = True
        if 'month' in post_data and 'year' in post_data:
            month = post_data['month']
            year = post_data['year']
        else:
            month = datetime.date.today().month
            year = datetime.date.today().year
        return render(request, 'pages/Distributor/report_sales_analysis.html', {'shop_name': shop_name,
                                                                                'transcriber_id': transcriber_id,
                                                                                'shop_id': shop_id,
                                                                                'subscribers': all_subscriber,
                                                                                'transcriber_name': transcriber_name,
                                                                                'month': month,
                                                                                'hasReport': hasReport,
                                                                                'year': year})
    else:
        return render(request, 'pages/Distributor/report_sales_analysis.html', {'shop_name': 'Not Selected',
                                                                                'transcriber_id': transcriber_id,
                                                                                'subscribers': all_subscriber,
                                                                                'transcriber_name': transcriber_name,
                                                                                'hasReport': hasReport})


# Shop Module

@login_required(login_url='/login/')
def shop_monthly_report(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name
    allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)
    allTransactionIn = BuyerSellerAccount.objects.filter(buyer=sr_object)

    return render(request, 'pages/Shop/report_monthly.html', {'transcriber_name': transcriber_name,
                                                              'allTransactionIn': allTransactionIn,
                                                              'allTransaction': allTransaction})


@login_required(login_url='/login/')
def shop_due_report(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name
    allBalance = BuyerSellerAccount.objects.filter(seller=sr_object)
    sell_transaction = Transaction.objects.filter(seller=sr_object)
    dueTransactions = dueTransaction.objects.filter(seller=sr_object)
    allBalanceIn = BuyerSellerAccount.objects.filter(buyer=sr_object)
    sell_transactionIn = Transaction.objects.filter(buyer=sr_object)
    dueTransactionsIn = dueTransaction.objects.filter(buyer=sr_object)

    return render(request, 'pages/Shop/report_due.html', {'transcriber_name': transcriber_name,
                                                          'sell_transaction': sell_transaction,
                                                          'dueTransactions': dueTransactions,
                                                          'allBalance': allBalance,
                                                          'sell_transactionIn': sell_transactionIn,
                                                          'dueTransactionsIn': dueTransactionsIn,
                                                          'allBalanceIn': allBalanceIn})

@login_required(login_url='/login/')
def shop_report_sales_analysis(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name

    post_data = request.POST
    print(post_data)
    shop_object = sr_object
    shop_name = shop_object.name
    shop_id = shop_object.id
    if 'month' in post_data and 'year' in post_data:
        month = post_data['month']
        year = post_data['year']
    else:
        month = datetime.date.today().month
        year = datetime.date.today().year
    return render(request, 'pages/Shop/report_sales_analysis.html', {'shop_name': shop_name,
                                                                     # 'all_consumer_for_base' :all_consumer_for_base,
                                                                     'shop_id': shop_id,
                                                                     # 'bangla': bangla,
                                                                     'transcriber_name': transcriber_name,
                                                                     'month': month,
                                                                     'year': year})

# Consumer Module

@login_required(login_url='/login/')
def user_monthly_report(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name
    # allTransaction = BuyerSellerAccount.objects.filter(seller=sr_object)
    allTransactionIn = BuyerSellerAccount.objects.filter(buyer=sr_object)

    return render(request, 'pages/Consumer/report_monthly.html', {'transcriber_name': transcriber_name,
                                                                  'allTransactionIn': allTransactionIn})


@login_required(login_url='/login/')
def user_due_report(request):
    sr_name = request.session['user']
    sr_object = ACL.objects.get(loginID=sr_name).loginUser
    transcriber_name = sr_object.name
    # allBalance = BuyerSellerAccount.objects.filter(seller=sr_object)
    # sell_transaction = Transaction.objects.filter(seller=sr_object)
    # dueTransactions = dueTransaction.objects.filter(seller=sr_object)
    allBalanceIn = BuyerSellerAccount.objects.filter(buyer=sr_object)
    sell_transactionIn = Transaction.objects.filter(buyer=sr_object)
    dueTransactionsIn = dueTransaction.objects.filter(buyer=sr_object)

    return render(request, 'pages/Consumer/report_due.html', {'transcriber_name': transcriber_name,
                                                              # 'sell_transaction': sell_transaction,
                                                              # 'dueTransactions': dueTransactions,
                                                              # 'allBalance': allBalance,
                                                              'sell_transactionIn': sell_transactionIn,
                                                              'dueTransactionsIn': dueTransactionsIn,
                                                              'allBalanceIn': allBalanceIn})


@login_required(login_url='/login/')
def change_password(request):
    # user = request.session['user']
    post_data = request.POST

    user_name = request.session['user']
    user_object = ACL.objects.get(loginID=user_name).loginUser
    transcriber_name = user_object.name
    user = user_object.phone[-9:]
    wrong = False
    text = ''

    if 'csrfmiddlewaretoken' in post_data:
        if post_data['password'] == post_data['re-password']:
            if User.objects.filter(username=user).exists():
                u = User.objects.get(username=user)
                u.set_password(post_data['password'])
                u.save()

                user_ID = user_object.id
                this_user = Consumer.objects.get(id=user_ID)
                this_user.number_of_child = 'CHANGED !!!'
                this_user.save()
                wrong = True
                text = 'Password is successfully changed'
                if user_object.type.type_name == 'Distributor':
                    display = render(request, 'pages/Distributor/index.html', {'transcriber_name': transcriber_name,
                                                                               'wrong': wrong,
                                                                               'text': text})
                elif user_object.type.type_name == 'SR':
                    display = render(request, 'pages/SR/index.html', {'transcriber_name': transcriber_name,
                                                                      'wrong': wrong,
                                                                      'text': text})
                elif user_object.type.type_name == 'Seller':
                    display = render(request, 'pages/Shop/index.html', {'transcriber_name': transcriber_name,
                                                                        'wrong': wrong,
                                                                        'text': text})
                elif user_object.type.type_name == 'Buyer':
                    display = render(request, 'pages/Consumer/index.html', {'transcriber_name': transcriber_name,
                                                                            'wrong': wrong,
                                                                            'text': text})
            else:
                wrong = True
                text = 'Something Wrong'
                if user_object.type.type_name == 'Distributor':
                    display = render(request, 'pages/Distributor/change_password.html', {'transcriber_name': transcriber_name,
                                                                                         'wrong': wrong,
                                                                                         'text': text})
                elif user_object.type.type_name == 'SR':
                    display = render(request, 'pages/SR/change_password.html', {'transcriber_name': transcriber_name,
                                                                                'wrong': wrong,
                                                                                'text': text})
                elif user_object.type.type_name == 'Seller':
                    display = render(request, 'pages/Shop/change_password.html', {'transcriber_name': transcriber_name,
                                                                                  'wrong': wrong,
                                                                                  'text': text})
                elif user_object.type.type_name == 'Buyer':
                    display = render(request, 'pages/Consumer/change_password.html', {'transcriber_name': transcriber_name,
                                                                                      'wrong': wrong,
                                                                                      'text': text})
        else:
            wrong = True
            text = 'Passwords do NOT match. Please try again'
            if user_object.type.type_name == 'Distributor':
                display = render(request, 'pages/Distributor/change_password.html', {'transcriber_name': transcriber_name,
                                                                                     'wrong': wrong,
                                                                                     'text': text})
            elif user_object.type.type_name == 'SR':
                display = render(request, 'pages/SR/change_password.html', {'transcriber_name': transcriber_name,
                                                                            'wrong': wrong,
                                                                            'text': text})
            elif user_object.type.type_name == 'Seller':
                display = render(request, 'pages/Shop/change_password.html', {'transcriber_name': transcriber_name,
                                                                              'wrong': wrong,
                                                                              'text': text})
            elif user_object.type.type_name == 'Buyer':
                display = render(request, 'pages/Consumer/change_password.html', {'transcriber_name': transcriber_name,
                                                                                  'wrong': wrong,
                                                                                  'text': text})
    else:
        wrong = False
        if user_object.type.type_name == 'Distributor':
            display = render(request, 'pages/Distributor/change_password.html', {'transcriber_name': transcriber_name,
                                                                                 'wrong': wrong,
                                                                                 'text': text})
        elif user_object.type.type_name == 'SR':
            display = render(request, 'pages/SR/change_password.html', {'transcriber_name': transcriber_name,
                                                                        'wrong': wrong,
                                                                        'text': text})
        elif user_object.type.type_name == 'Seller':
            display = render(request, 'pages/Shop/change_password.html', {'transcriber_name': transcriber_name,
                                                                          'wrong': wrong,
                                                                          'text': text})
        elif user_object.type.type_name == 'Buyer':
            display = render(request, 'pages/Consumer/change_password.html', {'transcriber_name': transcriber_name,
                                                                              'wrong': wrong})

    return display
