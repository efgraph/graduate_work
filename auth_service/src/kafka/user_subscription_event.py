import json

import enums
from db.config import db
from kafka.base import BaseKafkaHandler
from kafka.user_subscription_event_schemas import UserSubscribedEventSchema, UserUnsubscribedEventSchema, \
    UserSubscriptionRenewalEventSchema
from service.subscriptions import SubscriptionService

subscription_service = SubscriptionService(db)


class UserSubscribedHandler(BaseKafkaHandler):
    topic = "billing_user_subscribed"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserSubscribedEventSchema(
            user_id=msg["user_id"],
            subscription=msg["subscription"],
            subscription_expire_date=msg.get("subscription_expire_date"),
        )
        subscription_service.update_subscription(
            user_id=event.user_id,
            status=enums.SubscriptionStatus.ACTIVE.value,
            expire_date=event.subscription_expire_date,
            subscription_name=event.subscription
        )


class UserUnsubscribeHandler(BaseKafkaHandler):
    topic = "billing_user_unsubscribed"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserUnsubscribedEventSchema(
            user_id=msg["user_id"]
        )
        subscription_service.update_subscription(
            user_id=event.user_id,
            status=enums.SubscriptionStatus.CANCELLED.value
        )


class UserSubscriptionRenewalHandler(BaseKafkaHandler):
    topic = "billing_subscription_renewal"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserSubscriptionRenewalEventSchema(
            user_id=msg["user_id"],
            email=msg["email"]
        )
        subscription_service.update_subscription(
            user_id=event.user_id,
            status=enums.SubscriptionStatus.ACTIVE.value
        )
