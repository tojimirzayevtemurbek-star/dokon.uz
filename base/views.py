import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CustomerForm, DebtForm, LoginForm, PaymentForm, RegisterForm, StoreForm
from .models import Customer, Debt, Payment, Store


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Hisobingiz muvaffaqiyatli yaratildi."
            )

            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        }
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)

                messages.success(
                    request,
                    "Tizimga muvaffaqiyatli kirdingiz."
                )

                return redirect("dashboard")
        else:
            messages.error(
                request,
                "Telefon raqam yoki parol noto'g'ri."
            )
    else:
        form = LoginForm()

    return render(
        request,
        "registration/login.html",
        {
            "form": form,
        }
    )


@login_required
def logout_view(request):
    logout(request)

    messages.success(
        request,
        "Tizimdan chiqdingiz."
    )

    return redirect("login")


@login_required
def profile_view(request):

    customers = Customer.objects.filter(user=request.user)

    debts = Debt.objects.filter(customer__user=request.user)

    payments = Payment.objects.filter(customer__user=request.user)

    stores = Store.objects.filter(user=request.user)

    total_debt = debts.aggregate(total=Sum("amount"))["total"] or 0

    total_paid = payments.aggregate(total=Sum("amount"))["total"] or 0

    context = {
        "total_customers": customers.count(),
        "total_stores": stores.count(),
        "total_debt": total_debt,
        "total_paid": total_paid,
        "remaining_debt": total_debt - total_paid,
    }

    return render(
        request,
        "base/profile.html",
        context
    )


@login_required
def dashboard(request):

    customers = Customer.objects.filter(
        user=request.user
    )

    debts = Debt.objects.filter(
        customer__user=request.user
    )

    payments = Payment.objects.filter(
        customer__user=request.user
    )

    total_debt = (
        debts.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    total_paid = (
        payments.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    remaining_debt = total_debt - total_paid

    today = timezone.localdate()

    today_payments = (
        payments.filter(
            payment_date=today
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    overdue_debts = [d for d in debts if d.is_overdue and d.remaining > 0]
    overdue_count = len(overdue_debts)

    debt_customer_ids = debts.values_list(
        "customer_id",
        flat=True
    ).distinct()

    debtor_count = customers.filter(
        id__in=debt_customer_ids
    ).count()

    recent_debts = debts.select_related(
        "customer", "store"
    ).order_by(
        "-created_at"
    )[:5]

    recent_payments = payments.select_related(
        "customer"
    ).order_by(
        "-created_at"
    )[:5]

    # Qarzlar dinamikasi - so'nggi 7 kun
    chart_labels = []
    chart_values = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        day_total = debts.filter(
            debt_date=day
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        chart_labels.append(day.strftime("%d.%m"))
        chart_values.append(float(day_total))

    # Eng ko'p qarzdor mijozlar
    top_debtors = sorted(
        customers,
        key=lambda c: c.remaining_debt,
        reverse=True
    )
    top_debtors = [c for c in top_debtors if c.remaining_debt > 0][:5]

    stores = Store.objects.filter(user=request.user).order_by("-created_at")[:5]

    context = {
        "customers": customers,

        "total_customers": customers.count(),

        "total_debt": total_debt,

        "total_paid": total_paid,

        "remaining_debt": remaining_debt,

        "today_payments": today_payments,

        "overdue_count": overdue_count,

        "debtor_count": debtor_count,

        "recent_debts": recent_debts,

        "recent_payments": recent_payments,

        "chart_labels": json.dumps(chart_labels),

        "chart_values": json.dumps(chart_values),

        "top_debtors": top_debtors,

        "stores": stores,

        "store_count": Store.objects.filter(user=request.user).count(),
    }

    return render(
        request,
        "base/dashboard.html",
        context
    )


@login_required
def customer_list(request):

    customers = Customer.objects.filter(
        user=request.user
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    )

    if search:
        customers = customers.filter(
            Q(name__icontains=search)
            |
            Q(phone__icontains=search)
        )

    if status == "debtors":
        customer_ids = Debt.objects.filter(
            customer__user=request.user
        ).values_list(
            "customer_id",
            flat=True
        ).distinct()

        customers = customers.filter(
            id__in=customer_ids
        )

    elif status == "paid":
        customers = [
            customer
            for customer in customers
            if customer.remaining_debt <= 0
        ]

    return render(
        request,
        "base/customers.html",
        {
            "customers": customers,
            "search": search,
            "status": status,
        }
    )


@login_required
def customer_create(request):

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(
                commit=False
            )

            customer.user = request.user

            customer.save()

            messages.success(
                request,
                "Mijoz muvaffaqiyatli qo'shildi."
            )

            return redirect(
                "customer_list"
            )
    else:
        form = CustomerForm()

    return render(
        request,
        "base/customer_form.html",
        {
            "form": form,
            "title": "Yangi mijoz qo'shish",
        }
    )


@login_required
def customer_detail(request, pk):

    customer = get_object_or_404(
        Customer,
        pk=pk,
        user=request.user
    )

    debts = customer.debts.select_related("store").all()

    payments = customer.payments.all()

    return render(
        request,
        "base/customer_detail.html",
        {
            "customer": customer,
            "debts": debts,
            "payments": payments,
        }
    )


@login_required
def customer_edit(request, pk):

    customer = get_object_or_404(
        Customer,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Mijoz ma'lumotlari yangilandi."
            )

            return redirect(
                "customer_detail",
                pk=customer.pk
            )

    else:

        form = CustomerForm(
            instance=customer
        )

    return render(
        request,
        "base/customer_form.html",
        {
            "form": form,
            "title": "Mijozni tahrirlash",
            "customer": customer,
        }
    )


@login_required
def customer_delete(request, pk):

    customer = get_object_or_404(
        Customer,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":

        customer.delete()

        messages.success(
            request,
            "Mijoz o'chirildi."
        )

        return redirect(
            "customer_list"
        )

    return render(
        request,
        "base/customer_delete.html",
        {
            "customer": customer,
        }
    )


@login_required
def debt_create(request):

    if request.method == "POST":

        form = DebtForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            debt = form.save(
                commit=False
            )

            if debt.customer.user != request.user:
                messages.error(
                    request,
                    "Bu mijoz sizga tegishli emas."
                )

                return redirect(
                    "dashboard"
                )

            debt.save()

            messages.success(
                request,
                "Yangi qarz muvaffaqiyatli qo'shildi."
            )

            return redirect(
                "dashboard"
            )

    else:

        form = DebtForm(user=request.user)

    return render(
        request,
        "base/debt_form.html",
        {
            "form": form,
            "title": "Yangi qarz qo'shish",
        }
    )


@login_required
def payment_create(request):

    if request.method == "POST":

        form = PaymentForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            if payment.customer.user != request.user:
                messages.error(
                    request,
                    "Bu mijoz sizga tegishli emas."
                )

                return redirect(
                    "dashboard"
                )

            payment.save()

            messages.success(
                request,
                "To'lov muvaffaqiyatli qabul qilindi."
            )

            return redirect(
                "customer_detail",
                pk=payment.customer.pk
            )

    else:

        form = PaymentForm(
            user=request.user
        )

    return render(
        request,
        "base/payment_form.html",
        {
            "form": form,
            "title": "To'lov qabul qilish",
        }
    )


@login_required
def debt_list(request):

    debts = Debt.objects.filter(
        customer__user=request.user
    ).select_related(
        "customer", "store"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    )

    if search:
        debts = debts.filter(
            Q(customer__name__icontains=search)
            |
            Q(customer__phone__icontains=search)
            |
            Q(description__icontains=search)
        )

    today = timezone.localdate()

    if status == "overdue":
        debts = [d for d in debts if d.is_overdue and d.remaining > 0]

    elif status == "active":
        debts = [d for d in debts if not d.is_overdue and d.remaining > 0]

    elif status == "paid":
        debts = [d for d in debts if d.remaining <= 0]

    return render(
        request,
        "base/debts.html",
        {
            "debts": debts,
            "search": search,
            "status": status,
        }
    )


@login_required
def payment_list(request):

    payments = Payment.objects.filter(
        customer__user=request.user
    ).select_related(
        "customer"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        payments = payments.filter(
            Q(customer__name__icontains=search)
            |
            Q(customer__phone__icontains=search)
        )

    return render(
        request,
        "base/payments.html",
        {
            "payments": payments,
            "search": search,
        }
    )


@login_required
def store_list(request):

    stores = Store.objects.filter(user=request.user).order_by("name")

    return render(
        request,
        "base/stores.html",
        {
            "stores": stores,
        }
    )


@login_required
def store_create(request):

    if not request.user.is_superuser:
        messages.error(
            request,
            "Do'kon qo'shish faqat administrator uchun ruxsat etilgan."
        )

        return redirect("store_list")

    if request.method == "POST":
        form = StoreForm(request.POST)

        if form.is_valid():
            store = form.save(commit=False)
            store.user = request.user
            store.save()

            messages.success(
                request,
                "Do'kon muvaffaqiyatli qo'shildi."
            )

            return redirect("store_list")
    else:
        form = StoreForm()

    return render(
        request,
        "base/store_form.html",
        {
            "form": form,
            "title": "Yangi do'kon qo'shish",
        }
    )


@login_required
def store_delete(request, pk):

    store = get_object_or_404(Store, pk=pk, user=request.user)

    if request.method == "POST":
        store.delete()

        messages.success(
            request,
            "Do'kon o'chirildi."
        )

        return redirect("store_list")

    return render(
        request,
        "base/store_delete.html",
        {
            "store": store,
        }
    )
