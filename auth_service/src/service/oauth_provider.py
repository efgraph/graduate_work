from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from db.config import db_session
from db.models import OAuthAccount, User
from service.exceptions import UserDoesntExists, UserAlreadyExists


class OAuthProviderService:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def login(self, oauth_id: str, oauth_provider: str):
        oauth_account = OAuthAccount.query.filter_by(oauth_id=oauth_id, oauth_provider=oauth_provider).first()
        if oauth_account is None:
            raise UserDoesntExists
        return User.query.filter_by(id=oauth_account.user_id).first()

    def register_user(self, oauth_id: str, oauth_provider: str, email: str):
        user = User.create(login=email, email=email)
        try:
            with db_session(self.db) as session:
                session.add(user)
        except IntegrityError:
            raise UserAlreadyExists

        oauth_account = OAuthAccount(user_id=user.id, oauth_id=oauth_id, oauth_provider=oauth_provider)
        with db_session(self.db) as session:
            session.add(oauth_account)
