from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Transcriber
from subscriber.models import Consumer, ConsumerType
# Create your views here.

from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def add_transcriber(request):
    post_data = request.POST
    notification = ''
    print(post_data)
    add_notification = False
    if 'username' in post_data and 'password' in post_data and 're_password' in post_data:
        add_notification = True
        print('here')
        if Transcriber.objects.filter(name=post_data['username']).exists():
            notification = 'user already exists! Try with different name.'
        else:
            if post_data['password'] == post_data['re_password']:
                user = User.objects.create_user(post_data['username'], post_data['username']+'@sense.ai',
                                                post_data['password'])
                user.save()
                notification = 'Transcriber Successfully Added.'
                add_to_transcriber = Transcriber(name=post_data['username'])
                add_to_transcriber.save()
            else:
                notification = 'user already exists! Try with different name.'
    type_of_subscriber = ConsumerType.objects.all()
    all_subscriber = Consumer.objects.all()
    all_transcriber = Transcriber.objects.all()
    shop_consumer = ConsumerType.objects.get(type_name='Seller')
    all_shop_for_base = Consumer.objects.filter(type=shop_consumer)
    all_user_for_base = Consumer.objects.all()
    shop_consumer2 = ConsumerType.objects.get(type_name='Buyer')
    all_consumer_for_base = Consumer.objects.filter(type=shop_consumer2)

    print(add_notification)
    transcriber_name = request.session['user']
    return render(request, 'pages/add_transcriber.html',
                  {'subscribers': all_subscriber, 'types': type_of_subscriber, 'add_notification': add_notification,
                   'shop_list_base': all_shop_for_base,
                   'transcriber_name': transcriber_name,
                   'all_user_for_base': all_user_for_base,
                   'all_consumer_for_base' :all_consumer_for_base,
                   'notification': notification, 'all_transcriber': all_transcriber})
