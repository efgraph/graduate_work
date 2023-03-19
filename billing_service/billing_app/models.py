from uuid import UUID

import djstripe.models
import stripe
from django.db import models
from billing_app.enums import SubscriptionStatus


class BillingCustomer(models.Model):
    id = models.UUIDField(primary_key=True)
    email = models.EmailField()
    customer = models.ForeignKey(
        'djstripe.Customer',
        to_field='id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    subscription = models.ForeignKey(
        'djstripe.Subscription',
        to_field='id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    @classmethod
    def from_stripe_customer(cls, user_id: UUID, email: str, stripe_customer: stripe.Customer) -> 'BillingCustomer':
        djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(stripe_customer)
        customer = cls.objects.create(id=user_id, email=email, customer=djstripe_customer)
        customer.save()
        return customer

    @classmethod
    def update_subscription(cls, user_id: UUID, stripe_subscription: stripe.Subscription):
        subscription = djstripe.models.Subscription.sync_from_stripe_data(stripe_subscription)
        cls.objects.filter(id=user_id).update(subscription=subscription)

    def has_subscription(self) -> bool:
        return self.subscription is not None

    def has_active_subscription(self) -> bool:
        return self.has_subscription() and self.subscription.status == SubscriptionStatus.ACTIVE.value
