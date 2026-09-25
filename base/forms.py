from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Customer, Debt, Payment, Store


BASE_INPUT = (
    "w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50/60 "
    "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 "
    "text-sm text-slate-800 placeholder:text-slate-400 transition"
)


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Login yoki parol noto'g'ri kiritildi.",
        "inactive": "Bu hisob faol emas.",
    }


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": "Ikkala parol ham bir xil bo'lishi kerak.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Login"
        self.fields["username"].help_text = (
            "Talab qilinadi. 150 yoki undan kam belgi. "
            "Faqat harflar, raqamlar va @/./+/-/_ belgilaridan foydalaning."
        )
        self.fields["username"].error_messages = {
            "required": "Login kiritish shart.",
            "unique": "Bu login band, boshqasini tanlang.",
            "invalid": "Login faqat harflar, raqamlar va @/./+/-/_ belgilaridan iborat bo'lishi kerak.",
        }

        self.fields["password1"].label = "Parol"
        self.fields["password2"].label = "Parolni tasdiqlash"
        self.fields["password2"].help_text = "Tasdiqlash uchun yuqoridagi parolni yana kiriting."

        for field in self.fields.values():
            field.widget.attrs.update({"class": BASE_INPUT})


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "name",
            "phone",
            "address",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "Masalan: Aziz Karimov",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "+998 90 123 45 67",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "Toshkent shahri...",
                }
            ),
        }


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            "name",
            "category",
            "icon",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "Masalan: TEXNO",
                }
            ),
            "category": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "Masalan: Elektronika va gadjetlar",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "🏪",
                }
            ),
        }


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = [
            "customer",
            "store",
            "amount",
            "description",
            "debt_date",
            "due_date",
        ]

        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": BASE_INPUT,
                }
            ),
            "store": forms.Select(
                attrs={
                    "class": BASE_INPUT,
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "500000",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "Masalan: Telefon xarid qilindi",
                }
            ),
            "debt_date": forms.DateInput(
                attrs={
                    "class": BASE_INPUT,
                    "type": "date",
                }
            ),
            "due_date": forms.DateInput(
                attrs={
                    "class": BASE_INPUT,
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["store"].required = False

        if user:
            self.fields["customer"].queryset = Customer.objects.filter(user=user)
            self.fields["store"].queryset = Store.objects.filter(user=user)

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]

        if due_date < timezone.localdate():
            raise forms.ValidationError(
                "To'lov muddati bugundan oldin bo'lishi mumkin emas."
            )

        return due_date


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "customer",
            "amount",
            "payment_type",
            "payment_date",
            "description",
        ]

        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": BASE_INPUT,
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "200000",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "payment_type": forms.Select(
                attrs={
                    "class": BASE_INPUT,
                }
            ),
            "payment_date": forms.DateInput(
                attrs={
                    "class": BASE_INPUT,
                    "type": "date",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": BASE_INPUT,
                    "placeholder": "To'lov haqida izoh...",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.fields["customer"].queryset = Customer.objects.filter(
                user=user
            )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            raise forms.ValidationError(
                "To'lov summasi 0 dan katta bo'lishi kerak."
            )

        customer = self.cleaned_data.get("customer")

        if customer:
            remaining = customer.remaining_debt

            if amount > remaining:
                raise forms.ValidationError(
                    f"To'lov summasi qolgan qarzdan katta. "
                    f"Qolgan qarz: {remaining:,.0f} so'm"
                )

        return amount
