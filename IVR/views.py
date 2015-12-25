from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from subscriber.models import Consumer
import math
# Create your views here.


@csrf_exempt
def incoming_call(request):
    get_data = request.GET
    print(get_data)
    if 'session.callerid' in get_data:
        phone = get_data['session.callerid'][-6:]
        if Consumer.objects.filter(phone__endswith=phone).exists():
            """caller level id being done here"""
            caller = Consumer.objects.get(phone__endswith=phone)
            number_of_success = caller.total_successful_call
            number_of_errors = caller.number_of_calls_with_error
            user_level = int(math.floor(float(number_of_success)/3.0 - float(number_of_errors)/2.0) + 1)
            if user_level < 1:
                user_level = 1
            elif user_level > 3:
                user_level = 3
            caller.user_level = user_level
            caller.save()
            '''caller level updated here '''

            if user_level == 1:
                if caller.type.type_name == 'Seller':
                    if 'purpose' in get_data:
                        call_purpose = get_data['purpose']
                    else:
                        call_purpose = 'sell'

                    if call_purpose == 'sell':
                        return render(request, 'IVR/seller_level1_part1.xml',
                                      {'caller': get_data['session.callerid'], 'purpose': call_purpose, 'sell': True},
                                      content_type='application/xml')
                    elif call_purpose == 'buy':
                        return render(request, 'IVR/seller_level1_part1.xml',
                                      {'caller': get_data['session.callerid'], 'purpose': call_purpose, 'sell': False},
                                      content_type='application/xml')
                elif caller.type.type_name == 'Buyer':
                    return render(request, 'IVR/buyer_level1_part1.xml',
                                  {'caller': get_data['session.callerid'], 'purpose': 'buy', 'sell': True},
                                  content_type='application/xml')
                else:
                    return render(request, 'IVR/buyer_level1_part1.xml',
                                  {'caller': get_data['session.callerid'], 'purpose': 'sell', 'sell': True},
                                  content_type='application/xml')
            elif user_level == 2:
                if caller.type.type_name == 'Buyer':
                    sell = False
                    call_purpose = 'buy'
                else:
                    sell = True
                    call_purpose = 'sell'

                return render(request, 'IVR/level2p1.xml',
                              {'caller': get_data['session.callerid'], 'purpose': call_purpose, 'sell': sell},
                              content_type='application/xml')

            elif user_level == 3:
                if caller.type.type_name == 'Seller':
                    sell = False
                    call_purpose = 'buy'
                else:
                    sell = True
                    call_purpose = 'sell'

                return render(request, 'IVR/level3.xml',
                              {'caller': get_data['session.callerid'], 'purpose': call_purpose, 'sell': sell},
                              content_type='application/xml')
        else:
            return render(request, 'IVR/registration.xml', {'caller': get_data['session.callerid'],
                                                            'calledid': get_data['session.calledid']}, content_type='application/xml')
    else:
        return render(request, 'IVR/base.xml', content_type='application/xml')


@csrf_exempt
def incoming_call2(request):
    get_data = request.GET
    print(get_data)
    if 'session.callerid' in get_data:
        phone = get_data['session.callerid'][3:]
        return render(request, 'IVR/testivr.xml', {'caller': get_data['session.callerid']}, content_type='application/xml')
    else:
        return render(request, 'IVR/base.xml', content_type='application/xml')

