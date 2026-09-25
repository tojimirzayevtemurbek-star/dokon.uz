from django.contrib import admin

from .models import Customer, Debt, Payment, Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "icon", "user", "created_at")
    search_fields = ("name", "category")
    list_filter = ("created_at",)
    ordering = ("name",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "phone",
        "user",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "store",
        "amount",
        "debt_date",
        "due_date",
        "overdue_status",
    )

    search_fields = (
        "customer__name",
        "customer__phone",
        "description",
    )

    list_filter = (
        "debt_date",
        "due_date",
        "store",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Holat"
    )
    def overdue_status(self, obj):

        if obj.is_overdue:
            return "Muddati o'tgan"

        return "Faol"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "amount",
        "payment_type",
        "payment_date",
        "created_at",
    )

    search_fields = (
        "customer__name",
        "customer__phone",
        "description",
    )

    list_filter = (
        "payment_date",
        "payment_type",
    )

    ordering = (
        "-created_at",
    )
