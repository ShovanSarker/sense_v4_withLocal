from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from local_lib.v3 import is_japanese_number, is_bangladeshi_number, is_number, is_float, send_sms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from transcriber_management.models import Transcriber
from .models import Consumer, ConsumerType, Connectivity, ACL
from voice_records.models import VoiceReg


# Create your views here.


@login_required(login_url='/login/')
def add_subscriber(request):
    post_data = request.POST
    print(post_data)
    if 'csrfmiddlewaretoken' in post_data:
        name = post_data['name']
        phone = post_data['phone']
        add_notification = True
        if is_bangladeshi_number(phone) or is_japanese_number(phone):
            if Consumer.objects.filter(name__exact=name).exists():
                notification = 'This name ' + name + ' is already taken'
            else:
                if Consumer.objects.filter(phone__exact=phone).exists():
                    notification = 'This number ' + phone + ' is already taken'
                else:
                    child = 0
                    if 'child' in post_data:

                        child = post_data['child']
                    gender = 'None'
                    if 'gender' in post_data:
                        if not post_data['gender'] == 'Not Defined':
                            gender = post_data['gender']
                    age = 0
                    if 'age' in post_data:
                        if is_number(post_data['age']):
                            age = int(post_data['age'])
                        if is_float(post_data['age']):
                            age = float(post_data['age'])
                    married = False
                    if 'married' in post_data:
                        if post_data['married'] == 'Married':
                            married = True
                    address = ''
                    if 'address' in post_data:
                        address = post_data['address']
                    subscriber_type = ConsumerType.objects.get(type_name__exact='SR')
                    if 'type' in post_data:
                        subscriber_type = ConsumerType.objects.get(type_name__exact=post_data['type'])

                    email = ''
                    if 'email' in post_data:
                        email = post_data['email']

                    new_consumer = Consumer(name=name,
                                            type=subscriber_type,
                                            phone=phone,
                                            address=address,
                                            email=email,
                                            number_of_child=child,
                                            gender=gender,
                                            age=age,
                                            married=married)
                    new_consumer.save()
                    print(phone[-9:])
                    print(post_data['child'])
                    user = User.objects.create_user(phone[-9:], phone[-9:]+'@sense.ai',
                                                    post_data['child'])
                    user.save()
                    transcriber_name = request.session['user']
                    if ACL.objects.filter(loginID=transcriber_name).exists():
                        login_user = ACL.objects.get(loginID=transcriber_name)
                        if login_user.loginUser.type.type_name == 'Distributor':
                            add_new_subscriber = ACL(loginUser=new_consumer,
                                                     distUser=login_user.loginUser,
                                                     loginID=phone[-9:])
                            add_new_subscriber.save()
                    else:
                        add_new_subscriber = ACL(loginUser=new_consumer,
                                                 loginID=phone[-9:])
                        add_new_subscriber.save()
                    notification = 'Transcriber Successfully Added.'
                    # add_to_transcriber = Transcriber(name=post_data['username'])
                    # add_to_transcriber.save()
                    # welcome_sms = 'Thanks for connecting with hishab Limited. Use %s as username and %s as password while logging in to app.hishab.co . For more info go to www.hishab.co .' % (phone, child)
                    welcome_sms = 'Hishab-er shathe thakar jonno Dhonnobad. app.hishab.co te login korar shomoe apnar username hishebe %s ebong password hishebe %s bebohar korun . Aro tottho janar jonno visit korun www.hishab.co .' % (phone, child)
                    send_sms(welcome_sms, phone)
                    notification = 'New User ' + name + ' was added successfully'
        else:
            notification = 'Invalid Phone Number : ' + phone
    else:
        add_notification = False
        notification = ''
    all_subscriber = Consumer.objects.all()
    type_of_subscriber = ConsumerType.objects.all()
    transcriber_name = request.session['user']
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)
    res = render(request, 'pages/add_subscriber.html', {'subscribers': all_subscriber, 'types': type_of_subscriber,
                                                        'notification': notification,
                                                        'shop_list_base': all_shop_for_base,
                                                        'all_consumer_for_base' :all_consumer_for_base,
                                                        'all_user_for_base': all_user_for_base,
                                                        'transcriber_name': transcriber_name,
                                                        'add_notification': add_notification})

    res['Access-Control-Allow-Origin'] = "*"
    res['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    res['Access-Control-Allow-Methods'] = "PUT, GET, POST, DELETE, OPTIONS"

    return res


@login_required(login_url='/login/')
def add_subscriber_outside(request):
    print('here')
    post_data = request.POST
    print(post_data)
    name = post_data['name']
    phone = post_data['phone']
    if phone[0] == ' ':
        phone = phone[1:]
    # # todo error handeling in jS with error text

    add_notification = True

    if Consumer.objects.filter(name__exact=name).exists():
        notification = 'This name ' + name + ' is already taken'
        res = HttpResponse('error')
    else:
        if Consumer.objects.filter(phone__exact=phone).exists():
            notification = 'This number ' + phone + ' is already taken'
            res = HttpResponse('error')
        else:
            child = 0
            if 'child' in post_data:
               child = post_data['child']
            gender = 'None'
            if 'gender' in post_data:
                if not post_data['gender'] == 'Not Defined':
                    gender = post_data['gender']
            age = 0
            if 'age' in post_data:
                if is_number(post_data['age']):
                    age = int(post_data['age'])
                if is_float(post_data['age']):
                    age = float(post_data['age'])
            married = False
            if 'married' in post_data:
                if post_data['married'] == 'Married':
                    married = True
            address = ''
            if 'address' in post_data:
                address = post_data['address']
            subscriber_type = ConsumerType.objects.get(type_name__exact='Buyer')
            if 'type' in post_data:
                subscriber_type = ConsumerType.objects.get(type_name__exact=post_data['type'])
            email = ''
            if 'email' in post_data:
                email = post_data['email']

            new_consumer = Consumer(name=name,
                                    type=subscriber_type,
                                    phone=phone,
                                    address=address,
                                    email=email,
                                    number_of_child=child,
                                    gender=gender,
                                    age=age,
                                    married=married)
            new_consumer.save()
            print(phone[-9:])
            print(post_data['child'])
            user = User.objects.create_user(phone[-9:], phone[-9:]+'@sense.ai',
                                            post_data['child'])
            user.save()
            add_new_subscriber = ACL(loginUser=new_consumer,
                                     loginID=phone[-9:])
            add_new_subscriber.save()
            # welcome_sms = 'Thanks for connecting with hishab Limited. Use %s as username and %s as password while logging in to app.hishab.co . For more info go to www.hishab.co .' % (phone, child)
            welcome_sms = 'Hishab-er shathe thakar jonno Dhonnobad. app.hishab.co te login korar shomoe apnar username hishebe %s ebong password hishebe %s bebohar korun . Aro tottho janar jonno visit korun www.hishab.co .' % (phone, child)
            if 'record_id' in post_data:
                if not post_data['record_id'] == '':
                    call_record = VoiceReg.objects.get(pk=post_data['record_id'])
                    call_record.completed = True
                    call_record.save()
            if 'introduced_by' in post_data:
                if not post_data['introduced_by'] == '':
                    introduced_by = post_data['introduced_by']
                    introduced_by_object = Consumer.objects.get(pk=int(introduced_by))
                    new_dependency = Connectivity(user=new_consumer, introduced_by=introduced_by_object)
                    new_dependency.save()
            notification = 'New User ' + name + ' was added successfully'
            # welcome_sms = 'Thanks for connecting with Hishab Limited. For more info go to www.hishab.co .'
            send_sms(welcome_sms, phone)
            res = HttpResponse(new_consumer.id)



    all_subscriber = Consumer.objects.all()
    type_of_subscriber = ConsumerType.objects.all()
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()

    res['Access-Control-Allow-Origin'] = "*"
    res['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    res['Access-Control-Allow-Methods'] = "PUT, GET, POST, DELETE, OPTIONS"
    return res
