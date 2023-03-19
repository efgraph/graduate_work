from django.urls import path

from . import views

urlpatterns = [
    path('health_check', views.health_check),
    path('products', views.products),
    path('customer', views.customer_view),
    path('checkout', views.checkout_view),
    path('success', views.success),
    path('cancel', views.cancel),
    path('subscription', views.subscription_view),
    path('webhook', views.webhook_view)
]
