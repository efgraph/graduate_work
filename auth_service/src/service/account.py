import hashlib
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from db.config import db_session
from db.models import User, Password, UserSession
from service.exceptions import UserAlreadyExists, UserDoesntExists, WrongPassword, EditUserException


class AccountService:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def login(self, login: str, password: str):
        user = User.query.filter_by(login=login).first()
        if user is None:
            raise UserDoesntExists
        existing_password = Password.query.filter_by(user_id=user.id).first()
        if existing_password is None:
            raise UserDoesntExists

        existing_password_bytes = bytes.fromhex(existing_password.password)
        existing_password_salt = existing_password_bytes[:32]
        existing_password_hash = existing_password_bytes[32:]
        password_hash = self._hash(password, existing_password_salt)

        if password_hash != existing_password_hash:
            raise WrongPassword

        return user

    def register(self, login: str, password: str, email: str, is_superuser: bool = False):
        hash = self._generate_hex(password)
        user = User.create(
            login=login,
            email=email,
            is_superuser=is_superuser,
        )
        try:
            with db_session(self.db) as session:
                session.add(user)
        except IntegrityError:
            raise UserAlreadyExists

        password = Password(user_id=user.id, password=hash)
        with db_session(self.db) as session:
            session.add(password)

    def register_user_session(self, user_id: str, user_agent: str):
        user_session = UserSession(user_id=user_id, user_agent=user_agent)
        with db_session(self.db) as session:
            session.add(user_session)

    def get_user_sessions(self,
                          user_id: str,
                          page_size=10,
                          page_number=0):
        return UserSession.query.filter_by(user_id=user_id).paginate(
            int(page_number), int(page_size), error_out=False
        )

    def edit_user(self, user_id: str, login: str = "", email: str = "", password: str = ""):
        user = User.query.filter_by(id=user_id).first()
        existing_password = Password.query.filter_by(user_id=user_id).first()
        try:
            with db_session(self.db):
                if login:
                    user.login = login
                if email:
                    user.email = email
                if password:
                    existing_password.password = self._generate_hex(password)
        except IntegrityError:
            raise EditUserException

    def _generate_hex(self, password: str):
        salt = os.urandom(32)
        hash = self._hash(password, salt)
        return salt.hex() + hash.hex()

    def _hash(self, password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 10000)
