from typing import Optional
import datetime
from flask_sqlalchemy import SQLAlchemy
from db.config import db_session
from db.models import User


class SubscriptionService:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def update_subscription(
        self,
        user_id: str,
        status: str,
        expire_date: Optional[datetime.datetime] = None,
        subscription_name: Optional[str] = None,
    ):
        user = User.query.filter_by(id=user_id).first()
        with db_session(self.db) as session:
            user.subscription.name = subscription_name or user.subscription.name
            user.subscription.expires_at = expire_date or user.subscription.expires_at
            user.subscription.status = status
            session.add(user)
            session.commit()

