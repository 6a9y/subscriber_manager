from django.urls import path
from . import views


urlpatterns = [

    # لوحة التحكم
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # إضافة مشترك
    path(
        'add/',
        views.add_subscriber,
        name='add_subscriber'
    ),

    # قائمة المشتركين
    path(
        'list/',
        views.subscriber_list,
        name='subscriber_list'
    ),

    # تغيير حالة الدفع
    path(
        'toggle-paid/<int:pk>/',
        views.toggle_paid,
        name='toggle_paid'
    ),

    # تعديل المبلغ
    path(
        'update-amount/<int:pk>/',
        views.update_amount,
        name='update_amount'
    ),

    # تجديد الاشتراك
    path(
        'renew/<int:pk>/',
        views.renew_subscriber,
        name='renew_subscriber'
    ),

    # إلغاء التجديد
    path(
        'undo-renew/<int:pk>/',
        views.undo_renew_subscriber,
        name='undo_renew_subscriber'
    ),

    # طباعة الوصل
    path(
        'receipt/<int:pk>/',
        views.print_receipt,
        name='print_receipt'
    ),

    # فواتير المشترك
    path(
        'invoices/<int:pk>/',
        views.subscriber_invoices,
        name='subscriber_invoices'
    ),

    # سحب البيانات من الساس
    path(
        'sync/',
        views.sync_from_sas,
        name='sync_from_sas'
    ),
]