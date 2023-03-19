from kafka.registry import EventRegistry
from kafka.user_subscription_event import (
    UserSubscribedHandler, UserUnsubscribeHandler, UserSubscriptionRenewalHandler
)

event_registry = EventRegistry()

event_registry.register(UserSubscribedHandler)
event_registry.register(UserUnsubscribeHandler)
event_registry.register(UserSubscriptionRenewalHandler)
