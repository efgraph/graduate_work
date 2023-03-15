from http import HTTPStatus
import djstripe
import stripe
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from djstripe.models import Product
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from billing_app.api.utils import token_required
from billing_app.models import BillingCustomer


def products(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            product.name: [price.human_readable_price for price in product.prices.all()]
            for product in Product.objects.filter(active=True)
        }
    )


@method_decorator([csrf_exempt, token_required], name="dispatch")
class CheckoutSession(View):
    domain_url = 'http://localhost:8000/api/v1/'
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    def get(self, request: HttpRequest) -> JsonResponse:
        try:
            price_id = request.GET['price_id']
            checkout_session = stripe.checkout.Session.create(
                success_url=self.domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=self.domain_url + "cancel/",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}], # price_1MkDSYSDP0DyrqL5zvyGzbbK
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
class Customer(View):

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
        if not billing_customer:
            return JsonResponse(
                {
                    'message': f'user {request.user_id} does not exist'
                },
                status=HTTPStatus.FORBIDDEN
            )

        if billing_customer.has_subscription():
            return JsonResponse(
                {
                    'message': f'user {request.user_id} already has subscription'
                },
                status=HTTPStatus.FORBIDDEN
            )
        price_id = request.POST['price_id']

        stripe_subscription = stripe.Subscription.create(
            customer=billing_customer.customer.id,
            items=[{'plan': price_id}],  # price_1MkDSYSDP0DyrqL5zvyGzbbK
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
            api_key=settings.STRIPE_TEST_SECRET_KEY,
        )

        BillingCustomer.update_subscription(request.user_id, stripe_subscription)

        return JsonResponse(
            {
                'message': f'user {request.user_id} subscribed for {stripe_subscription}'
            },
            status=HTTPStatus.OK
        )

# @webhooks.handler('invoice.payment_succeeded')
# def handle_invoice_payment_succeeded(invoice: djstripe.models.Invoice):
#     kafka_producer = KafkaService.get_producer()
#     kafka_producer.produce()
#     kafka_producer.flush()


customer_view = Customer.as_view()
checkout_view = CheckoutSession.as_view()
subscription_view = SubscriptionApi.as_view()