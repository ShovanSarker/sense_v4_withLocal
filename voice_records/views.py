from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
from local_lib.v3 import is_bangladeshi_number, is_japanese_number
from .models import VoiceRecord, VoiceReg
from subscriber.models import Consumer
from transcriber_management.models import FailedTranscription, Transcriber
from transaction.models import Transaction
import os, shutil
# Create your views here.


@csrf_exempt
def save_record_voice(request):
    file_data = request.FILES
    get_data = request.GET
    print request.GET
    print request.FILES
    if 'session.callerid' in get_data:
        phone = get_data['session.callerid'][3:]
    else:
        phone = 'unknown'
    if 'tid' in get_data:
        tracking_id = get_data['tid']
    else:
        tracking_id = '0000'
    tempname=''

    if get_data['level'] == '1':
        if get_data['part'] == '1':
            tracking_id = phone[-4:]

            now = ''.join(x for x in str(datetime.datetime.now()) if x.isdigit())
            tracking_id += now[2:14]
            caller_object = Consumer.objects.get(phone__endswith=phone)
            # save_record = None
            save_record = VoiceRecord(caller=caller_object,
                                      level1_voice_part1=file_data['rec1'],
                                      call_tracking_id=tracking_id,
                                      purpose=get_data['purpose'],
                                      level=get_data['level'])
            save_record.save()
            tempname = str(save_record.level1_voice_part1)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            print(filename)
            print(filenamenew)
            if get_data['purpose'] == 'Sell':
                sell = True
            else:
                sell = False
            return render(request, 'IVR/level1_part2.xml',
                          {'caller': phone, 'purpose': get_data['purpose'], 'sell': sell, 'tid': tracking_id},
                          content_type='application/xml')

        elif get_data['part'] == '2':
            save_record = VoiceRecord.objects.get(call_tracking_id__exact=tracking_id)
            save_record.level1_voice_part2 = file_data['rec2']
            save_record.save()
            tempname = str(save_record.level1_voice_part2)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            if get_data['purpose'] == 'Sell':
                sell = True
            else:
                sell = False
            return render(request, 'IVR/level1_part3.xml',
                          {'caller': phone, 'purpose': get_data['purpose'], 'sell': sell, 'tid': tracking_id},
                          content_type='application/xml')
        elif get_data['part'] == '3':
            save_record = VoiceRecord.objects.get(call_tracking_id__exact=tracking_id)
            save_record.level1_voice_part3 = file_data['rec3']
            save_record.save()
            tempname = str(save_record.level1_voice_part3)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            return render(request, 'IVR/end.xml', content_type='application/xml')
    elif get_data['level'] == '2':
        if get_data['part'] == '1':

            tracking_id = phone[-4:]
            now = ''.join(x for x in str(datetime.datetime.now()) if x.isdigit())
            tracking_id += now[2:14]
            caller_object = Consumer.objects.get(phone__endswith=phone)
            save_record = VoiceRecord(caller=caller_object,
                                      level1_voice_part1=file_data['rec41'],
                                      call_tracking_id=tracking_id,
                                      purpose=get_data['purpose'],
                                      level=get_data['level'])
            save_record.save()
            tempname = str(save_record.level1_voice_part1)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            if get_data['purpose'] == 'Sell':
                sell = True
            else:
                sell = False
            return render(request, 'IVR/level2p2.xml',
                          {'caller': phone, 'purpose': get_data['purpose'], 'sell': sell, 'tid': tracking_id},
                          content_type='application/xml')

        elif get_data['part'] == '2':
            save_record = VoiceRecord.objects.get(call_tracking_id__exact=tracking_id)
            save_record.level1_voice_part2 = file_data['rec42']
            save_record.save()
            tempname = str(save_record.level1_voice_part2)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            if get_data['purpose'] == 'Sell':
                sell = True
            else:
                sell = False
            return render(request, 'IVR/level2p3.xml',
                          {'caller': phone, 'purpose': get_data['purpose'], 'sell': sell, 'tid': tracking_id},
                          content_type='application/xml')
        elif get_data['part'] == '3':
            save_record = VoiceRecord.objects.get(call_tracking_id__exact=tracking_id)
            save_record.level1_voice_part3 = file_data['rec43']
            save_record.save()
            tempname = str(save_record.level1_voice_part3)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            return render(request, 'IVR/end.xml', content_type='application/xml')
    elif get_data['level'] == '3':
        tracking_id = phone[-4:]
        now = ''.join(x for x in str(datetime.datetime.now()) if x.isdigit())
        tracking_id += now[2:14]
        caller_object = Consumer.objects.get(phone__endswith=phone)
        save_record = VoiceRecord(caller=caller_object,
                                  level3=file_data['rec5'],
                                  call_tracking_id=tracking_id,
                                  purpose=get_data['purpose'],
                                  level=get_data['level'])
        save_record.save()
        tempname = str(save_record.level3)
        filename = '/home/exor/static/media/' + tempname
        filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
        shutil.copy2(filename, filenamenew)
        return render(request, 'IVR/end.xml', content_type='application/xml')
    else:
        return render(request, 'IVR/base.xml', content_type='application/xml')


@csrf_exempt
def save_registration_voice(request):
    file_data = request.FILES
    get_data = request.GET
    print(get_data)
    print(file_data)
    if 'level' in get_data:
        if get_data['level'] == '1':
            phone = get_data['session.callerid']
            caller_type = get_data['caller_type']
            # print('upto here')
            # print(get_data)
            if 'session.calledid' in get_data:
                calledNumber = get_data['session.calledid']
                # print(calledNumber[-4:])
                if calledNumber[-4:] == '0010':
                    phone = '880' + phone[-10:]
                    # print('bangladesh')
                elif calledNumber[-4:] == '4436':
                    # print('singapore')
                    phone = '65' + phone[-8:]
            tracking_id = phone[-4:]
            # print(phone)
            now = ''.join(x for x in str(datetime.datetime.now()) if x.isdigit())
            tracking_id += now[2:14]
            new_voice_reg = VoiceReg(caller=phone,
                                     caller_type=caller_type,
                                     tracking_id=tracking_id)
            new_voice_reg.save()
            if get_data['caller_type'] == 'Shop' or get_data['caller_type'] == 'Distributor':
                shop = True
            else:
                shop = False
            print(tracking_id)
            return render(request, 'IVR/registration_2.xml', {'shop': shop, 'tracking_id': tracking_id},  content_type='application/xml')
        elif get_data['level'] == '2':
            print("here")
            tracking_id = get_data['tracking_id']
            new_voice_reg = VoiceReg.objects.get(tracking_id=tracking_id)
            new_voice_reg.registration_voice_name = file_data['rec2']
            new_voice_reg.save()
            # new_voice_regname = new_voice_reg.registration_voice_name
            # print(new_voice_regname)
            tempname = str(new_voice_reg.registration_voice_name)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            if new_voice_reg.caller_type == 'Shop' or new_voice_reg.caller_type == 'Distributor':
                shop = True
            else:
                shop = False

            return render(request, 'IVR/registration_3.xml', {'tracking_id': tracking_id, 'shop': shop},  content_type='application/xml')
        elif get_data['level'] == '3':
            tracking_id = get_data['tracking_id']
            new_voice_reg = VoiceReg.objects.get(tracking_id=tracking_id)
            new_voice_reg.registration_voice_address = file_data['rec3']
            new_voice_reg.save()
            tempname = str(new_voice_reg.registration_voice_address)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            if new_voice_reg.caller_type == 'Shop' or new_voice_reg.caller_type == 'Distributor':
                return render(request, 'IVR/registration_5.xml', {'tracking_id': tracking_id},  content_type='application/xml')
            else:
                return render(request, 'IVR/registration_4.xml', {'tracking_id': tracking_id},  content_type='application/xml')
        elif get_data['level'] == '4':
            tracking_id = get_data['tracking_id']
            new_voice_reg = VoiceReg.objects.get(tracking_id=tracking_id)
            new_voice_reg.registration_voice_age = file_data['rec4']
            new_voice_reg.save()
            tempname = str(new_voice_reg.registration_voice_age)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            return render(request, 'IVR/registration_5.xml', {'tracking_id': tracking_id},  content_type='application/xml')
        elif get_data['level'] == '5':
            tracking_id = get_data['tracking_id']
            new_voice_reg = VoiceReg.objects.get(tracking_id=tracking_id)
            new_voice_reg.registration_voice_intro = file_data['rec5']
            new_voice_reg.save()
            tempname = str(new_voice_reg.registration_voice_intro)
            filename = '/home/exor/static/media/' + tempname
            filenamenew = '/home/exor/static/media/' + tempname[:-3] + 'wav'
            shutil.copy2(filename, filenamenew)
            return render(request, 'IVR/end.xml', content_type='application/xml')
    else:
        return render(request, 'IVR/end.xml', content_type='application/xml')


@csrf_exempt
def voice_record_list(request):
    output = '{ "calls": { '
    pending_calls = VoiceRecord.objects.filter(transcribed=False)
    i = 1
    for call in pending_calls:
        output = output + ' "' + str(i) + '":{"callid":"%s", "caller":"%s", "caller_id":"%s", ' \
                                          '"caller_level": "%s",' \
                                          '"caller_number": "%s",' \
                                          '"call_timestamps": "%s",' % (call.pk, call.caller.name, call.caller.id,
                                                                        call.level,
                                                                        call.caller.phone,
                                                                        str(call.DateAdded))
        audio = '%s,%s,%s,%s,%s,' % (str(call.level1_voice_part1)[:-3]+'wav', str(call.level1_voice_part2)[:-3]+'wav',
                                     str(call.level1_voice_part3)[:-3]+'wav', str(call.level2)[:-3]+'wav',
                                     str(call.level3)[:-3]+'wav')
        audio = audio.strip(',')
        output += '"audiofiles": "%s"},' % audio
        i += 1
    output = output[:-1]
    output += '},"registration": { '
    pending_registration_calls = VoiceReg.objects.filter(completed=False)
    i = 1
    for call in pending_registration_calls:
        output = output + ' "' + str(i) + '":{"callid":"%s", ' \
                                          '"caller_number": "%s",' \
                                          '"caller_type": "%s",' \
                                          '"call_timestamps": "%s",' % (call.pk,
                                                                        call.caller, call.caller_type,
                                                                        call.caller_type +' -> '+str(call.DateAdded))
        audio = '%s,%s,%s,%s,' % (str(call.registration_voice_name)[:-3]+'wav',
                                  str(call.registration_voice_address)[:-3]+'wav',
                                  str(call.registration_voice_age)[:-3]+'wav',
                                  str(call.registration_voice_intro)[:-3]+'wav')
        audio = audio.strip(',')
        output += '"audiofiles": "%s"},' % audio
        i += 1
    output = output[:-1]
    output += '}}'
    return HttpResponse(output, content_type="text/plain")


@csrf_exempt
def failed_voice_record_list(request):
    output = '{ "calls": { '

    pending_calls_error = VoiceRecord.objects.filter(with_error=True)
    i = 1
    for call in pending_calls_error:
        transcriber_name = FailedTranscription.objects.get(callID=call).name.name
        fail_reason = FailedTranscription.objects.get(callID=call).remarks
        print(transcriber_name, fail_reason)
        output = output + ' "' + str(i) + '":{"callid":"%s", "caller":"%s", "caller_id":"%s", ' \
                                          '"caller_level": "%s",' \
                                          '"caller_number": "%s",' \
                                          '"reason": "%s",' \
                                          '"tried_by_name": "%s",' \
                                          '"call_timestamps": "%s",' % (call.pk, call.caller.name, call.caller.id,
                                                                        call.level,
                                                                        call.caller.phone, fail_reason, transcriber_name,
                                                                        str(call.DateAdded))
        audio = '%s,%s,%s,%s,%s,' % (call.level1_voice_part1, call.level1_voice_part2,
                                     call.level1_voice_part3, call.level2, call.level3)
        audio = audio.strip(',')
        output += '"audiofiles": "%s"},' % audio
        i += 1
    output = output[:-1]
    output += '}}'
    return HttpResponse(output, content_type="text/plain")


@csrf_exempt
def completed_voice_record_list(request):
    output = '{ "calls": { '

    pending_calls_error = VoiceRecord.objects.filter(with_error=False, transcribed=True)
    i = 1
    for call in pending_calls_error:

        output = output + ' "' + str(i) + '":{"callid":"%s", "caller":"%s", "caller_id":"%s", ' \
                                          '"caller_level": "%s",' \
                                          '"caller_number": "%s",' \
                                          '"call_timestamps": "%s",' % (call.pk, call.caller.name, call.caller.id,
                                                                        call.level,
                                                                        call.caller.phone,
                                                                        str(call.DateAdded))
        audio = '%s,%s,%s,%s,%s,' % (str(call.level1_voice_part1)[:-3]+'wav', str(call.level1_voice_part2)[:-3]+'wav',
                                     str(call.level1_voice_part3)[:-3]+'wav', str(call.level2)[:-3]+'wav',
                                     str(call.level3)[:-3]+'wav')
        audio = audio.strip(',')
        output += '"audiofiles": "%s"},' % audio
        i += 1
    output = output[:-1]
    output += '}}'
    return HttpResponse(output, content_type="text/plain")


@csrf_exempt
def completed_voice_record_list_transaction_id(request):
    output = '{ "calls": { '

    pending_calls_error = VoiceRecord.objects.filter(with_error=False, transcribed=True)
    i = 1
    for call in pending_calls_error:
        transaction = Transaction.objects.filter(callID=call)[0]
        transaction_id = transaction.id
        output = output + ' "' + str(i) + '":{"callid":"%s", "caller":"%s", "caller_id":"%s", ' \
                                          '"caller_level": "%s",' \
                                          '"caller_number": "%s",' \
                                          '"transaction_id": "%s",' \
                                          '"transaction_by": "%s",' \
                                          '"call_timestamps": "%s",' % (call.pk, call.caller.name, call.caller.id,
                                                                        call.level,
                                                                        call.caller.phone, transaction_id,
                                                                        transaction.transcriber,
                                                                        str(call.DateAdded))
        audio = '%s,%s,%s,%s,%s,' % (call.level1_voice_part1, call.level1_voice_part2,
                                     call.level1_voice_part3, call.level2, call.level3)
        audio = audio.strip(',')
        output += '"audiofiles": "%s"},' % audio
        i += 1
    output = output[:-1]
    output += '}}'
    return HttpResponse(output, content_type="text/plain")


@csrf_exempt
def transcribed_voice_record_list(request):
    output = '{ "calls": { '

    pending_calls_error = VoiceRecord.objects.filter(transcribed=True)
    i = 1
    for call in pending_calls_error:
        transcriber_name = FailedTranscription.objects.get(callID=call).name.name
        call_object = Transaction.objects.get(callID=call)
        call_id = call_object.id
        output = output + ' "' + str(i) + '":{"callid":"%s", "caller":"%s", "caller_id":"%s", ' \
                                          '"caller_level": "%s",' \
                                          '"caller_number": "%s",' \
                                          '"translate_by_name": "%s",' \
                                          '"transaction_id": "%s",' \
                                          '"call_timestamps": "%s",' % (call.pk, call.caller.name, call.caller.id,
                                                                        call.level,
                                                                        call.caller.phone, transcriber_name, call_id,
                                                                        str(call.DateAdded))
        audio = '%s,%s,%s,%s,%s,' % (call.level1_voice_part1, call.level1_voice_part2,
                                     call.level1_voice_part3, call.level2, call.level3)
        audio = audio.strip(',')
        output += '"audiofiles": "%s"},' % audio
        i += 1
    output = output[:-1]
    output += '}}'
    return HttpResponse(output, content_type="text/plain")
