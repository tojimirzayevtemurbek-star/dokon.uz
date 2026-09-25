from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Store(models.Model):
    """Do'kon / bo'lim - qarzlarni guruhlash uchun (masalan: Texnika, Kiyim, Go'zallik)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stores"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Do'kon nomi"
    )

    category = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Yo'nalishi",
        help_text="Masalan: Elektronika va gadjetlar"
    )

    icon = models.CharField(
        max_length=10,
        default="🏪",
        verbose_name="Belgi"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Do'kon"
        verbose_name_plural = "Do'konlar"

    def __str__(self):
        return self.name

    @property
    def debt_count(self):
        return self.debts.count()

    @property
    def total_debt(self):
        return sum(debt.amount for debt in self.debts.all())

    @property
    def total_remaining(self):
        return sum(max(debt.remaining, 0) for debt in self.debts.all())


class Customer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customers"
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Mijoz ismi"
    )

    phone = models.CharField(
        max_length=30,
        verbose_name="Telefon"
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Manzil"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Qo'shilgan sana"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"

    def __str__(self):
        return self.name

    @property
    def total_debt(self):
        return sum(
            debt.amount for debt in self.debts.all()
        )

    @property
    def total_paid(self):
        return sum(
            payment.amount for payment in self.payments.all()
        )

    @property
    def remaining_debt(self):
        return self.total_debt - self.total_paid

    @property
    def has_overdue(self):
        return any(debt.is_overdue and debt.remaining > 0 for debt in self.debts.all())


class Debt(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="debts"
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debts",
        verbose_name="Do'kon"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Qarz summasi"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Izoh / Mahsulot"
    )

    debt_date = models.DateField(
        verbose_name="Qarz sanasi"
    )

    due_date = models.DateField(
        verbose_name="To'lov muddati"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Qarz"
        verbose_name_plural = "Qarzlar"

    def __str__(self):
        return f"{self.customer.name} - {self.amount} so'm"

    @property
    def is_overdue(self):
        from django.utils import timezone

        return (
            self.due_date < timezone.localdate()
        )

    @property
    def paid_amount(self):
        allocated = self.amount
        paid_before = Debt.objects.filter(
            customer=self.customer,
            created_at__lt=self.created_at
        ).aggregate(
            total=models.Sum("amount")
        )["total"] or 0

        total_paid = self.customer.total_paid

        available = max(total_paid - paid_before, 0)
        return min(available, allocated)

    @property
    def remaining(self):
        return self.amount - self.paid_amount

    @property
    def status(self):
        if self.remaining <= 0:
            return "paid"
        if self.is_overdue:
            return "overdue"
        return "active"


class Payment(models.Model):
    PAYMENT_TYPES = [
        ("cash", "Naqd"),
        ("card", "Karta"),
        ("transfer", "O'tkazma"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="To'lov summasi"
    )

    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        default="cash",
        verbose_name="To'lov turi"
    )

    payment_date = models.DateField(
        verbose_name="To'lov sanasi"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Izoh"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"

    def __str__(self):
        return f"{self.customer.name} - {self.amount} so'm"
