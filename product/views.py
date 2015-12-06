from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from local_lib.v3 import is_number, is_float
from django.contrib.auth.decorators import login_required
from .models import Product
from subscriber.models import Consumer, ConsumerType


# Create your views here.


@login_required(login_url='/login/')
def add_product(request):
    post_data = request.POST
    print(post_data)
    if 'csrfmiddlewaretoken' in post_data:
        add_notification = True
        name = post_data['name'].capitalize()
        if Product.objects.filter(name=name).exists():
            notification = 'Product ' + name + ' is already in the List'
        else:
            if 'retail_unit' in post_data:
                notification = 'Product ' + name + ' was added successfully'
                retail_unit = post_data['retail_unit'].upper()
                if 'altr_name' in post_data:
                    altr_name = post_data['altr_name']
                else:
                    altr_name = ''
                if 'bangla_name' in post_data:
                    bangla_name = post_data['bangla_name']
                else:
                    bangla_name = ''
                if 'bulk_unit' in post_data:
                    bulk_unit = post_data['bulk_unit'].upper()
                else:
                    bulk_unit = post_data['bulk_unit'].upper()
                if 'bulk_price' in post_data:
                    if is_float(post_data['retail_price']) or is_number(post_data['retail_price']):
                        bulk_price = post_data['bulk_price']
                    else:
                        bulk_price = 0
                else:
                    bulk_price = 0
                if 'converter' in post_data:
                    if is_float(post_data['converter']) or is_number(post_data['converter']):
                        converter = post_data['converter']
                    else:
                        converter = 1
                else:
                    converter = 1
                if 'retail_price' in post_data:
                    if is_float(post_data['retail_price']) or is_number(post_data['retail_price']):
                        retail_price = post_data['retail_price']
                    else:
                        retail_price = 0
                else:
                    retail_price = 0
                add_notification = True
                new_product = Product(name=name,
                                      alternative_name=altr_name,
                                      bangle_name=bangla_name,
                                      retail_unit=retail_unit,
                                      bulk_wholesale_unit=bulk_unit,
                                      price_per_retail_unit=retail_price,
                                      price_per_bulk_wholesale_unit=bulk_price,
                                      bulk_to_retail_unit=converter)
                new_product.save()
            else:
                notification = 'Product Details Not Found!'
    else:
        add_notification = False
        notification = ''
    all_product = Product.objects.all()
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    transcriber_name = request.session['user']
    res = render(request, 'pages/add_product.html', {'all_product': all_product,
                                                     'notification': notification,
                                                     'transcriber_name': transcriber_name,
                                                     'all_consumer_for_base': all_consumer_for_base,
                                                     'add_notification': add_notification,
                                                     'shop_list_base': all_shop_for_base,
                                                     'all_user_for_base': all_user_for_base})

    res['Access-Control-Allow-Origin'] = "*"
    res['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    res['Access-Control-Allow-Methods'] = "PUT, GET, POST, DELETE, OPTIONS"
    return res


@csrf_exempt
def add_product_outside(request):
    post_data = request.POST
    print(post_data)
    add_notification = True
    name = post_data['name'].capitalize()
    if Product.objects.filter(name=name).exists():
        notification = 'Product ' + name + ' is already in the List'
        res = HttpResponse(notification)
    else:
        if 'retail_unit' in post_data:
            notification = 'Product ' + name + ' was added successfully'
            retail_unit = post_data['retail_unit'].upper()
            if 'altr_name' in post_data:
                altr_name = post_data['altr_name']
            else:
                altr_name = ''
            if 'bangla_name' in post_data:
                bangla_name = post_data['bangla_name']
            else:
                bangla_name = ''
            if 'bulk_unit' in post_data:
                bulk_unit = post_data['bulk_unit'].upper()
            else:
                bulk_unit = post_data['bulk_unit'].upper()
            if 'bulk_price' in post_data:
                if is_float(post_data['retail_price']) or is_number(post_data['retail_price']):
                    bulk_price = post_data['bulk_price']
                else:
                    bulk_price = 0
            else:
                bulk_price = 0
            if 'converter' in post_data:
                if is_float(post_data['converter']) or is_number(post_data['converter']):
                    converter = post_data['converter']
                else:
                    converter = 1
            else:
                converter = 1
            if 'retail_price' in post_data:
                if is_float(post_data['retail_price']) or is_number(post_data['retail_price']):
                    retail_price = post_data['retail_price']
                else:
                    retail_price = 0
            else:
                retail_price = 0
            add_notification = True
            new_product = Product(name=name,
                                  alternative_name=altr_name,
                                  bangle_name=bangla_name,
                                  retail_unit=retail_unit,
                                  bulk_wholesale_unit=bulk_unit,
                                  price_per_retail_unit=retail_price,
                                  price_per_bulk_wholesale_unit=bulk_price,
                                  bulk_to_retail_unit=converter)
            new_product.save()
            res = HttpResponse('ok')
        else:
            res = HttpResponse('not_ok')

    res['Access-Control-Allow-Origin'] = "*"
    res['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    res['Access-Control-Allow-Methods'] = "PUT, GET, POST, DELETE, OPTIONS"
    return res


@csrf_exempt
def product_subscriber_list(request):
    output = '{ "products": {'
    product_all = Product.objects.all()
    i = 1
    for products in product_all:
        output = output + '"' + str(i) + '":{"id":"%s", "name":"%s", ' \
                                         '"avg_price": "%s",' \
                                         '"retail_unit": "%s",' \
                                         '"bulk_unit": "%s"' % (products.pk, products.name,
                                                                products.price_per_retail_unit,
                                                                products.retail_unit,
                                                                products.bulk_wholesale_unit)

        output += '},'
        i += 1
    output = output[:-1]
    output += '},"subscribers": {'

    subscriber_all = Consumer.objects.all()
    j = 0
    for subscribers in subscriber_all:
        output = output + '"' + str(j) + '":{"id":"%s", ' \
                                         '"name": "%s",' \
                                         '"number": "%s",' \
                                         '"type": "%s"' % (subscribers.pk,
                                                           subscribers.name,
                                                           subscribers.phone,
                                                           subscribers.type.type_name)

        output += '},'
        j += 1
    output = output[:-1]
    output += '}}'
    return HttpResponse(output, content_type="text/plain")

