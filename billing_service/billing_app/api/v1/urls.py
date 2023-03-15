from django.urls import path

from . import views

urlpatterns = [
    path('products', views.products),
    path('customer', views.customer_view),
    path('checkout', views.checkout_view),
    path('success', views.success),
    path('cancel', views.cancel),
    path('subscribe', views.subscription_view),
]
