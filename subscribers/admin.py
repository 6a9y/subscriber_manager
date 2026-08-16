from django.contrib import admin
from .models import Subscriber, Invoice


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'username',
        'package',
        'start_date',
        'end_date',
        'amount',
        'is_active',
        'is_paid',
    )

    search_fields = ('name', 'phone', 'username')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'subscriber',
        'amount',
        'issue_date',
        'start_date',
        'end_date',
        'is_paid',
    )

    search_fields = (
        'invoice_number',
        'subscriber__name',
        'subscriber__username',
    )