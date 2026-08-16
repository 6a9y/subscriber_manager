from django.db import models

class Subscriber(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    package = models.CharField(max_length=50)
    amount = models.IntegerField(default=40000)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    
    # حقل تسجيل وقت آخر تجديد (ضروري لخاصية الإلغاء والفلترة)
    last_renewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.username})"

class Invoice(models.Model):
    subscriber = models.ForeignKey(
        Subscriber,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.IntegerField()
    issue_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"فاتورة {self.invoice_number} - {self.subscriber.name}"