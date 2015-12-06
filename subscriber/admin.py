from django.contrib import admin
from .models import Consumer, ConsumerType
# Register your models here.


class ConsumerAdmin(admin.ModelAdmin):
    class Meta:
        model = Consumer
    list_display = ('name', 'type', 'phone', 'user_level', 'total_successful_call', 'number_of_calls_with_error')
admin.site.register(Consumer, ConsumerAdmin)


class ConsumerTypeAdmin(admin.ModelAdmin):
    class Meta:
        model = ConsumerType
admin.site.register(ConsumerType, ConsumerTypeAdmin)