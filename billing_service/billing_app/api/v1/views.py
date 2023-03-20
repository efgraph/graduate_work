from datetime import datetime as dt
import json
from http import HTTPStatus
from typing import Optional, Callable

import djstripe
import stripe
from billing_app.constants import USER_UNSUBSCRIBED, USER_SUBSCRIBED, USER_SUBSCRIPTION_RENEWAL, SESSION_COMPLETED
from billing_app.services.kafka import KafkaService
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST
from djstripe.models import Product, Subscription
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from billing_app.api.utils import token_required
from billing_app.models import BillingCustomer


@csrf_exempt
def health_check(request: HttpRequest):
    return JsonResponse(
        {
            "message": "OK"
        }
    )


@csrf_exempt
def products(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            product.name: [{price.id: price.human_readable_price} for price in product.prices.all()] for product in
            Product.objects.filter(active=True)
        }
    )


@method_decorator([csrf_exempt, token_required], name="dispatch")
class CheckoutApi(View):
    domain_url = 'http://localhost/api/v1/'
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    def get(self, request: HttpRequest) -> JsonResponse:
        try:
            price_id = request.GET['price_id']
            checkout_session = stripe.checkout.Session.create(
                success_url=self.domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=self.domain_url + "cancel/",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                customer=BillingCustomer.objects.get(id=request.user_id).customer_id,
            )
            djstripe.models.Session.sync_from_stripe_data(checkout_session)
            return JsonResponse({"checkout_session_url": checkout_session.url})
        except Exception as e:
            return JsonResponse(
                {"message": str(e), "user_id": request.user_id},
                status=HTTPStatus.FORBIDDEN,
            )


def success(request: HttpRequest) -> HttpResponse:
    return render(request, 'success.html')


def cancel(request: HttpRequest) -> HttpResponse:
    return render(request, 'cancel:html')


@method_decorator([csrf_exempt, token_required], name="dispatch")
class CustomerApi(View):

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            queryset = BillingCustomer.objects.filter(id=request.user_id)
            if not queryset.exists():
                stripe_customer = stripe.Customer.create(email=request.user_email)
                customer = BillingCustomer.from_stripe_customer(
                    request.user_id, request.user_email, stripe_customer
                )
            else:
                customer = queryset.first()
            return JsonResponse(
                {
                    "message": "Ok",
                    "user_id": request.user_id,
                    "customer_id": customer.customer_id,
                }
            )
        except Exception as error:
            return JsonResponse(
                data={"message": str(error), "user_id": request.user_id},
                status=HTTPStatus.FORBIDDEN,
            )


@method_decorator([csrf_exempt, token_required], name='dispatch')
class SubscriptionApi(View):

    def post(self, request: HttpRequest) -> JsonResponse:
        billing_customer = BillingCustomer.objects.get(id=request.user_id)

        if not billing_customer.has_subscription():
            return JsonResponse(
                {
                    "message": "user does not have subscription",
                    "user_id": request.user_id,
                    "customer_id": billing_customer.customer_id,
                    "subscription_id": billing_customer.subscription_id,
                },
                status=HTTPStatus.FORBIDDEN,
            )

        if billing_customer.subscription.cancel_at_period_end:
            stripe_subscription = stripe.Subscription.modify(
                billing_customer.subscription_id, cancel_at_period_end=False
            )

            billing_customer.subscription.cancel_at_period_end = False
            billing_customer.subscription.save()

            kafka_producer = KafkaService.get_producer()
            kafka_producer.produce(
                topic=USER_SUBSCRIPTION_RENEWAL,
                key=f"{USER_SUBSCRIPTION_RENEWAL}_{billing_customer.subscription_id}_{request.user_id}",
                value=json.dumps(
                    {
                        "user_id": str(request.user_id),
                        "email": billing_customer.email
                    }
                )
            )
            kafka_producer.flush()

            return JsonResponse(
                {
                    "message": "Ok",
                    "user_id": request.user_id,
                    "customer_id": stripe_subscription.customer,
                    "subscription_id": stripe_subscription.id,
                }
            )

        return JsonResponse(
            {
                "message": "user subscription is active",
                "user_id": request.user_id,
                "customer_id": billing_customer.customer_id,
                "subscription_id": billing_customer.subscription_id,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    def delete(self, request: HttpRequest) -> JsonResponse:
        queryset = BillingCustomer.objects.filter(id=request.user_id)
        if not queryset.exists():
            return JsonResponse(
                {"message": "customer does not exist", "user_id": request.user_id},
                status=HTTPStatus.FORBIDDEN,
            )

        billing_customer = queryset.first()
        if not billing_customer.has_active_subscription():
            return JsonResponse(
                {
                    "message": "customer does not have active subscription",
                    "user_id": request.user_id,
                },
                status=HTTPStatus.FORBIDDEN,
            )

        if billing_customer.subscription.cancel_at_period_end:
            return JsonResponse(
                {
                    "message": "user has already cancelled subscription",
                    "user_id": request.user_id,
                }
            )

        try:
            deleted_subscription = stripe.Subscription.modify(
                billing_customer.subscription_id, cancel_at_period_end=True
            )
            billing_customer.subscription.cancel_at_period_end = (
                deleted_subscription.cancel_at_period_end
            )
            billing_customer.subscription.save()

            kafka_producer = KafkaService.get_producer()
            kafka_producer.produce(
                topic=USER_UNSUBSCRIBED,
                key=f"{USER_UNSUBSCRIBED}_{deleted_subscription.id}_{request.user_id}",
                value=json.dumps(
                    {
                        "user_id": str(request.user_id)
                    }
                ),
            )
            kafka_producer.flush()
            return JsonResponse({"subscription": deleted_subscription})
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=HTTPStatus.FORBIDDEN)


@method_decorator([csrf_exempt, require_POST], name="dispatch")
class StripeWebhook(View):
    http_allowed_methods = ["POST"]

    def post(self, request: HttpRequest) -> HttpResponse:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        webhook_secret = settings.DJSTRIPE_WEBHOOK_SECRET
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as _:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        data_object = event.get("data", {}).get("object", {})
        event_type = event.get("type", "")

        subscription_updater = self.subscription_updater(event_type)
        if not subscription_updater:
            return HttpResponse(status=HTTPStatus.OK)

        customer_id = data_object.get("customer", None)
        if not customer_id:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        subscription_object = data_object.get("subscription", None)
        if not subscription_object:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        stripe_subscription = stripe.Subscription.retrieve(subscription_object)
        if not stripe_subscription:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        product = stripe.Product.retrieve(stripe_subscription["plan"]["product"])

        billing_user = BillingCustomer.objects.filter(customer_id=customer_id).first()
        if not billing_user:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        subscription = subscription_updater(customer_id, stripe_subscription)
        billing_user.subscription = subscription
        billing_user.save()

        if event_type == SESSION_COMPLETED:
            kafka_producer = KafkaService.get_producer()
            kafka_producer.produce(
                topic=USER_SUBSCRIBED,
                key=f"{USER_SUBSCRIBED}_{stripe_subscription.id}_{billing_user.id}",
                value=json.dumps(
                    {
                        "user_id": str(billing_user.id),
                        "subscription": product["name"],
                        "subscription_expire_date": str(
                            subscription.current_period_end
                        ),
                    }
                ),
            )
            kafka_producer.flush()
        return HttpResponse(status=HTTPStatus.OK)

    def subscription_updater(self, event_type: str) -> Optional[Callable]:
        method_name = event_type.replace(".", "_")
        return getattr(self, method_name, None)

    def checkout_session_completed(
        self, customer_id, stripe_subscription
    ) -> Subscription:
        subscription = Subscription.objects.create(
            id=stripe_subscription.id,
            customer_id=customer_id,
            current_period_start=dt.fromtimestamp(
                stripe_subscription.current_period_start
            ),
            current_period_end=dt.fromtimestamp(
                stripe_subscription.current_period_end
            ),
            status=stripe_subscription.status,
        )
        return subscription

    def invoice_paid(self, customer_id, stripe_subscription) -> Subscription:
        subscription, _ = Subscription.objects.get_or_create(
            id=stripe_subscription.id, customer_id=customer_id
        )
        subscription.status = stripe_subscription.status
        subscription.current_period_start = dt.fromtimestamp(
            stripe_subscription.current_period_start
        )
        subscription.current_period_end = dt.fromtimestamp(
            stripe_subscription.current_period_end
        )
        subscription.save(
            update_fields=[
                "status",
                "current_period_start",
                "current_period_end",
            ]
        )
        return subscription

    def invoice_payment_failed(self, customer_id, stripe_subscription) -> Subscription:
        subscription, _ = Subscription.objects.get_or_create(
            id=stripe_subscription.id, customer_id=customer_id
        )
        subscription.status = stripe_subscription.status
        subscription.save()
        return subscription


customer_view = CustomerApi.as_view()
checkout_view = CheckoutApi.as_view()
subscription_view = SubscriptionApi.as_view()
webhook_view = StripeWebhook.as_view()
