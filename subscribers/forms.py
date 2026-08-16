from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['name', 'username', 'phone', 'package', 'amount', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المشترك'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم / الاشتراك'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '077xxxxxxxx'}),
            'package': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الباقة (مثلاً: 50M)'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'المبلغ بالدينار'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'اسم المشترك',
            'username': 'اسم المستخدم / الاشتراك',
            'phone': 'رقم الهاتف',
            'package': 'الباقة',
            'amount': 'المبلغ',
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ الانتهاء',
            'is_active': 'اشتراك فعال',
        }