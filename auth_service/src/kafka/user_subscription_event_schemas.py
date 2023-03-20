from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserSubscribedEventSchema:
    user_id: str = ""
    subscription: str = ""
    subscription_expire_date: Optional[datetime] = None


@dataclass(frozen=True)
class UserUnsubscribedEventSchema:
    user_id: str = ""


@dataclass(frozen=True)
class UserSubscriptionRenewalEventSchema:
    user_id: str = ""
    email: str = ""
