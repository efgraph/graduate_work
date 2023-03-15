from django.contrib import admin

from billing_app.models import BillingCustomer


@admin.register(BillingCustomer)
class BillingCustomerAdmin(admin.ModelAdmin):
    pass
