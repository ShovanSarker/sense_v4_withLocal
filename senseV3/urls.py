from django.conf.urls import patterns, include, url

from django.contrib import admin
from IVR.views import incoming_call
from voice_records.views import save_record_voice, save_registration_voice, \
    voice_record_list, failed_voice_record_list, transcribed_voice_record_list,\
    completed_voice_record_list, completed_voice_record_list_transaction_id
from sms.views import get_sms
from transaction.views import add_transaction, failed_transaction, detailed_transaction
from product.views import product_subscriber_list, add_product, add_product_outside
from subscriber.views import add_subscriber, add_subscriber_outside
from template_manager.views import login_page,\
    login_auth,\
    home,\
    logout_now,\
    translator_page,\
    add_subscriber_page,\
    report_callduration,\
    report_calltranscription,\
    report_product, \
    report_due, \
    report_monthly_shop, \
    report_payment, \
    report_analytical, \
    report_recharge,\
    report_transaction,\
    report_sales_analysis,\
    report_usercall,\
    report_profit,\
    transcription_page,\
    add_product_page,\
    report_product_json,\
    report_profit_json, \
    report_sales_analysis_json, \
    report_monthly_shop_json, \
    report_analytical_json, \
    report_transcriber_performance, \
    report_monthly_shop_print,\
    report_due_print,\
    report_payment_print,\
    report_product_print,\
    report_profit_print,\
    report_sales_analysis_print,\
    report_transcriber_performance_print,\
    report_transcriber_performance_json, user_balance_recharge
from transcriber_management.views import add_transcriber
from django.conf.urls.static import static
from sms.views import send_sms_for_dues
from django.conf import settings
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'senseV3.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    url(r'^admin/', include(admin.site.urls)),
    url(r'^IVR/', view=incoming_call, name='home'),
    url(r'^saverecord/', view=save_record_voice, name='home'),
    url(r'^reg/', view=save_registration_voice, name='home'),
    url(r'^getsms/', view=get_sms, name='home'),
    url(r'^login/', view=login_page, name='home'),
    url(r'^logout/', view=logout_now, name='home'),
    url(r'^login_info/', view=login_auth, name='home'),
    url(r'^translator/', view=translator_page, name='home'),
    url(r'^addsubscriber/', view=add_subscriber_page, name='home'),
    url(r'^addsubscriber_info/', view=add_subscriber, name='home'),
    url(r'^addsubscriber_info_outside/', view=add_subscriber_outside, name='home'),
    url(r'^completed_voice_record_list/', view=completed_voice_record_list, name='home'),
    url(r'^completed_voice_record_list_transaction_id/',  view=completed_voice_record_list_transaction_id, name='home'),
    url(r'^addproduct_info/', view=add_product, name='home'),
    url(r'^detailed_transaction/', view=detailed_transaction, name='home'),
    url(r'^add_product_outside/', view=add_product_outside, name='home'),
    url(r'^products/', view=add_product_page, name='home'),
    url(r'^voice_record_list/', view=voice_record_list, name='home'),
    url(r'^product_subscriber_list/', view=product_subscriber_list, name='home'),
    url(r'^failed_transaction/', view=failed_transaction, name='home'),
    url(r'^failed_voice_record_list/', view=failed_voice_record_list, name='home'),
    url(r'^transcribed_voice_record_list/', view=transcribed_voice_record_list, name='home'),
    url(r'^send_sms_for_dues/', view=send_sms_for_dues, name='home'),
    url(r'^$', view=home, name='home'),
    # urls for reports
    # url(r'^product_reports/', view=report_product, name='home'),
    url(r'^report_product_json/', view=report_product_json, name='home'),
    url(r'^recharge_reports/', view=report_recharge, name='home'),
    url(r'^transaction_reports/', view=report_transaction, name='home'),
    url(r'^calltranscription_reports/', view=report_calltranscription, name='home'),
    url(r'^callduration_reports/', view=report_callduration, name='home'),
    url(r'^usercall_report/', view=report_usercall, name='home'),
    url(r'^transcription_page/', view=transcription_page, name='home'),
    url(r'^add_transaction/', view=add_transaction, name='home'),
    url(r'^add_transcriber/', view=add_transcriber, name='home'),

    # reports from list
    url(r'^product_reports/', view=report_product, name='home'),
    url(r'^due_reports/', view=report_due, name='home'),
    url(r'^payment_reports/', view=report_payment, name='home'),
    url(r'^monthly_shop_reports/', view=report_monthly_shop, name='home'),
    url(r'^analytical_reports/', view=report_analytical, name='home'),
    url(r'^report_analytical_json/', view=report_analytical_json, name='home'),
    url(r'^profit_reports/', view=report_profit, name='home'),
    url(r'^report_profit_json/', view=report_profit_json, name='home'),
    url(r'^sales_analysis_report/', view=report_sales_analysis, name='home'),
    url(r'^report_sales_analysis_json/', view=report_sales_analysis_json, name='home'),
    url(r'^report_monthly_shop_json/', view=report_monthly_shop_json, name='home'),
    url(r'^report_transcriber_performance/', view=report_transcriber_performance, name='home'),
    url(r'^report_transcriber_performance_json/', view=report_transcriber_performance_json, name='home'),
    url(r'^user_balance_recharge/', view=user_balance_recharge, name='home'),
    # report urls ends

    # reports for printing
    url(r'^monthly_shop_reports_print/', view=report_monthly_shop_print, name='home'),
    url(r'^due_reports_print/', view=report_due_print, name='home'),
    url(r'^payment_reports_print/', view=report_payment_print, name='home'),
    url(r'^product_reports_print/', view=report_product_print, name='home'),
    url(r'^sales_analysis_report_print/', view=report_sales_analysis_print, name='home'),
    url(r'^profit_reports_print/', view=report_profit_print, name='home'),
    url(r'^report_transcriber_performance_print/', view=report_transcriber_performance_print, name='home'),
    # json urls for reports
    # url(r'^report_monthly_shop_json_print/', view=report_monthly_shop_json, name='home'),
    # url(r'^report_product_json_print/', view=report_product_json, name='home'),
    # url(r'^report_profit_json_print/', view=report_profit_json, name='home'),
    # url(r'^report_sales_analysis_json_print/', view=report_sales_analysis_json, name='home'),
    # url(r'^report_transcriber_performance_json_print/', view=report_transcriber_performance_json, name='home'),
    # printing url ends


)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

