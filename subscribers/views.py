import re
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Subscriber, Invoice
from .forms import SubscriberForm


# ==========================================
# أسعار الباقات
# ==========================================

PACKAGE_PRICES = {
    'Economy': 40000,
    'Standard': 50000,
    'Turbo': 60000,
    'Game': 70000,
    'Business': 90000,
}


# ==========================================
# لوحة التحكم
# ==========================================

def dashboard(request):
    today = timezone.now().date()
    three_days_later = today + timedelta(days=3)

    total_subscribers = Subscriber.objects.count()

    active_subscribers = Subscriber.objects.filter(
        end_date__gte=today
    ).count()

    expired_subscribers = Subscriber.objects.filter(
        end_date__lt=today
    ).count()

    unpaid_subscribers = Subscriber.objects.filter(
        is_paid=False
    )

    unpaid_count = unpaid_subscribers.count()

    unpaid_money = unpaid_subscribers.aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    paid_money = Subscriber.objects.filter(
        is_paid=True
    ).aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    # المشتركين الذين ينتهي اشتراكهم خلال 3 أيام
    expiring_soon = Subscriber.objects.filter(
        end_date__gte=today,
        end_date__lte=three_days_later
    ).order_by('end_date')

    context = {
        'total_subscribers': total_subscribers,
        'active_subscribers': active_subscribers,
        'expired_subscribers': expired_subscribers,
        'expiring_soon': expiring_soon,
        'unpaid_count': unpaid_count,
        'unpaid_money': unpaid_money,
        'paid_money': paid_money,
        'today': today,
    }

    return render(
        request,
        'subscribers/dashboard.html',
        context
    )


# ==========================================
# إضافة مشترك
# ==========================================

def add_subscriber(request):

    if request.method == 'POST':

        form = SubscriberForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = SubscriberForm()

    return render(
        request,
        'subscribers/add_subscriber.html',
        {'form': form}
    )


# ==========================================
# قائمة المشتركين
# ==========================================

def subscriber_list(request):

    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')

    now = timezone.now()
    today = now.date()

    three_days_ago = now - timedelta(days=3)

    subscribers = Subscriber.objects.all().order_by('-id')

    # الفلاتر
    if filter_type == 'active':

        subscribers = subscribers.filter(
            end_date__gte=today
        )

    elif filter_type == 'expired':

        subscribers = subscribers.filter(
            end_date__lt=today
        )

    elif filter_type == 'unpaid':

        subscribers = subscribers.filter(
            is_paid=False
        )

    elif filter_type == 'paid':

        subscribers = subscribers.filter(
            is_paid=True
        )

    elif filter_type == 'renewed_recently':

        subscribers = subscribers.filter(
            last_renewed_at__gte=three_days_ago
        )

    # البحث
    if query:

        subscribers = subscribers.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(username__icontains=query)
        )

    # السماح بإلغاء التجديد خلال 3 أيام
    for sub in subscribers:

        sub.can_undo = False

        if sub.last_renewed_at:

            if (
                now - sub.last_renewed_at
            ) <= timedelta(days=3):

                sub.can_undo = True

    return render(
        request,
        'subscribers/subscriber_list.html',
        {
            'subscribers': subscribers,
            'query': query,
            'filter_type': filter_type,
            'today': today,
        }
    )


# ==========================================
# تغيير حالة الدفع
# ==========================================

def toggle_paid(request, pk):

    subscriber = get_object_or_404(
        Subscriber,
        pk=pk
    )

    subscriber.is_paid = not subscriber.is_paid

    subscriber.save()

    # تحديث آخر فاتورة مرتبطة بالمشترك
    last_invoice = subscriber.invoices.order_by('-id').first()

    if last_invoice:
        last_invoice.is_paid = subscriber.is_paid
        last_invoice.save()

    return redirect('subscriber_list')


# ==========================================
# تعديل المبلغ
# ==========================================

def update_amount(request, pk):

    if request.method == 'POST':

        subscriber = get_object_or_404(
            Subscriber,
            pk=pk
        )

        new_amount = request.POST.get('amount')

        if new_amount:

            try:

                subscriber.amount = int(new_amount)
                subscriber.save()

            except ValueError:
                pass

    return redirect('subscriber_list')


# ==========================================
# توليد رقم فاتورة
# ==========================================

def generate_invoice_number():

    last_invoice = Invoice.objects.order_by('-id').first()

    if last_invoice:

        try:

            last_number = int(
                last_invoice.invoice_number.replace(
                    'INV-',
                    ''
                )
            )

            return f"INV-{last_number + 1:05d}"

        except (ValueError, AttributeError):

            return f"INV-{Invoice.objects.count() + 1:05d}"

    return "INV-00001"


# ==========================================
# تجديد الاشتراك
# ==========================================

def renew_subscriber(request, pk):

    subscriber = get_object_or_404(
        Subscriber,
        pk=pk
    )

    today = timezone.now().date()

    # إذا الاشتراك منتهي يبدأ من اليوم
    # وإذا بعده فعال يكمل من تاريخ الانتهاء
    if subscriber.end_date < today:
        start = today
    else:
        start = subscriber.end_date

    end = start + timedelta(days=30)

    # تحديث الاشتراك
    subscriber.start_date = start
    subscriber.end_date = end
    subscriber.is_active = True

    # عند التجديد يصبح غير مدفوع
    subscriber.is_paid = False

    # تسجيل وقت التجديد
    subscriber.last_renewed_at = timezone.now()

    subscriber.save()

    # إنشاء فاتورة جديدة
    invoice_number = generate_invoice_number()

    Invoice.objects.create(
        subscriber=subscriber,
        invoice_number=invoice_number,
        amount=subscriber.amount,
        start_date=start,
        end_date=end,
        is_paid=False,
    )

    return redirect('subscriber_list')


# ==========================================
# إلغاء آخر تجديد
# ==========================================

def undo_renew_subscriber(request, pk):

    subscriber = get_object_or_404(
        Subscriber,
        pk=pk
    )

    if subscriber.last_renewed_at:

        time_since_renew = (
            timezone.now()
            - subscriber.last_renewed_at
        )

        # السماح بالإلغاء خلال 3 أيام فقط
        if time_since_renew <= timedelta(days=3):

            subscriber.end_date = (
                subscriber.end_date
                - timedelta(days=30)
            )

            subscriber.start_date = (
                subscriber.start_date
                - timedelta(days=30)
            )

            subscriber.is_active = (
                subscriber.end_date
                >= timezone.now().date()
            )

            subscriber.last_renewed_at = None

            subscriber.save()

            # حذف آخر فاتورة للمشترك
            last_invoice = (
                Invoice.objects
                .filter(subscriber=subscriber)
                .order_by('-id')
                .first()
            )

            if last_invoice:
                last_invoice.delete()

            return HttpResponse(
                """
                <script>
                    alert('↩️ تم إلغاء التجديد بنجاح وإرجاع الاشتراك لسابق عهده!');
                    window.location.href='/list/';
                </script>
                """
            )

    return HttpResponse(
        """
        <script>
            alert('❌ انتهت مهلة الـ 3 أيام المتاحة لإلغاء التجديد!');
            window.location.href='/list/';
        </script>
        """
    )


# ==========================================
# طباعة الوصل
# ==========================================

def print_receipt(request, pk):

    subscriber = get_object_or_404(
        Subscriber,
        pk=pk
    )

    # جلب آخر فاتورة
    invoice = (
        Invoice.objects
        .filter(subscriber=subscriber)
        .order_by('-id')
        .first()
    )

    return render(
        request,
        'subscribers/receipt.html',
        {
            'subscriber': subscriber,
            'invoice': invoice,
            'today': timezone.now().date(),
        }
    )


# ==========================================
# عرض فواتير المشترك
# ==========================================

def subscriber_invoices(request, pk):

    subscriber = get_object_or_404(
        Subscriber,
        pk=pk
    )

    invoices = (
        Invoice.objects
        .filter(subscriber=subscriber)
        .order_by('-id')
    )

    return render(
        request,
        'subscribers/invoices.html',
        {
            'subscriber': subscriber,
            'invoices': invoices,
        }
    )


# ==========================================
# مزامنة المشتركين من الساس
# ==========================================

@csrf_exempt
def sync_from_sas(request):

    if request.method == 'POST':

        raw_data = request.POST.get(
            'sas_data',
            ''
        )

        today = timezone.now().date()

        added_count = 0

        lines = raw_data.strip().split('\n')

        for line in lines:

            line_clean = (
                line
                .replace('██', '')
                .strip()
            )

            match = re.search(
                r'([a-zA-Z0-9\.\@\_]+)([\u0600-\u06FF\s]+)(\d{4}-\d{2}-\d{2})',
                line_clean
            )

            if match:

                u_name = match.group(1).strip()

                name = match.group(2).strip()

                date_str = match.group(3).strip()

                # الباقة الافتراضية
                pkg = 'Economy'

                line_lower = line_clean.lower()

                if 'business' in line_lower:

                    pkg = 'Business'

                elif (
                    'game' in line_lower
                    or 'gaming' in line_lower
                    or 'كيم' in line_lower
                ):

                    pkg = 'Game'

                elif (
                    'turbo' in line_lower
                    or 'تيربو' in line_lower
                ):

                    pkg = 'Turbo'

                elif 'standard' in line_lower:

                    pkg = 'Standard'

                amount = PACKAGE_PRICES.get(
                    pkg,
                    40000
                )

                try:

                    end_d = datetime.strptime(
                        date_str,
                        '%Y-%m-%d'
                    ).date()

                except ValueError:

                    end_d = (
                        today
                        + timedelta(days=30)
                    )

                subscriber, created = (
                    Subscriber.objects.get_or_create(
                        username=u_name,
                        defaults={
                            'name': name or u_name,
                            'phone': '0000',
                            'package': pkg,
                            'amount': amount,
                            'start_date': today,
                            'end_date': end_d,
                            'is_active': end_d >= today,
                            'is_paid': False,
                        }
                    )
                )

                if not created:

                    subscriber.name = (
                        name or subscriber.name
                    )

                    subscriber.package = pkg

                    subscriber.amount = amount

                    subscriber.end_date = end_d

                    subscriber.is_active = (
                        end_d >= today
                    )

                    subscriber.save()

                added_count += 1

        return HttpResponse(
            f"""
            <script>
                alert('✅ تم تحديث {added_count} مشترك مع الأسعار الجديدة!');
                window.location.href='/list/';
            </script>
            """
        )

    # صفحة إدخال بيانات الساس
    html_form = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>تحديث من الساس</title>
    </head>

    <body style="
        background:#f4f6f9;
        margin:0;
        padding:20px;
        font-family:system-ui,sans-serif;
        direction:rtl;
    ">

        <div style="
            max-width:650px;
            margin:40px auto;
            background:#fff;
            padding:25px;
            border-radius:10px;
            box-shadow:0 4px 15px rgba(0,0,0,0.1);
        ">

            <h2 style="color:#2c3e50;">
                تحديث المشتركين من لوحة الساس
            </h2>

            <p style="
                color:#7f8c8d;
                font-size:14px;
            ">
                الصق النص المنسوخ من لوحة الساس واضغط معالجة:
            </p>

            <form method="POST">

                <textarea
                    name="sas_data"
                    rows="14"
                    style="
                        width:100%;
                        padding:12px;
                        border-radius:6px;
                        border:1px solid #bdc3c7;
                        font-family:monospace;
                        font-size:13px;
                        box-sizing:border-box;
                    "
                    placeholder="الصق النص هنا..."
                ></textarea>

                <br><br>

                <button
                    type="submit"
                    style="
                        background:#27ae60;
                        color:white;
                        padding:12px 25px;
                        border:none;
                        border-radius:6px;
                        cursor:pointer;
                        font-size:16px;
                        font-weight:bold;
                        width:100%;
                    "
                >
                    🚀 معالجة وحفظ البيانات
                </button>

            </form>

        </div>

    </body>
    </html>
    """

    return HttpResponse(html_form)