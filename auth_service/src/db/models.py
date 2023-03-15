import enum
import re
import uuid
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    func, Enum,
)
from sqlalchemy.exc import IntegrityError

from sqlalchemy.dialects.postgresql import UUID

from db.config import db, db_session
from service.exceptions import UserAlreadyExists


class OAuthName(enum.Enum):
    google = 'google'


class UserEmailType(enum.Enum):
    yandex = 'yandex'
    google = 'google'
    other = 'other'


def create_users_partition(target, connection, **kw):
    connection.execute(
        f"""
            CREATE TABLE IF NOT EXISTS "users_yandex" PARTITION OF "users" FOR VALUES IN ('{UserEmailType.yandex}')
        """,
    )
    connection.execute(
        f"""
            CREATE TABLE IF NOT EXISTS "users_google" PARTITION OF "users" FOR VALUES IN ('{UserEmailType.google}')
        """,
    )
    connection.execute(
        f"""
            CREATE TABLE IF NOT EXISTS "users_other" PARTITION OF "users" FOR VALUES IN ('{UserEmailType.other}')
        """,
    )


class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


class Role(db.Model, TimestampMixin):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(20), unique=True)
    description = Column(String(255))


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'

    id = Column(BigInteger(), primary_key=True)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'))
    role_id = Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'))


class User(db.Model, TimestampMixin):
    __tablename__ = 'users'
    __table_args__ = {
        "postgresql_partition_by": 'LIST (email_type)',
        'listeners': [('after_create', create_users_partition)],
    }

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    email_type = Column(Enum(UserEmailType), nullable=False, default=UserEmailType.other)
    login = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_superuser = Column(Boolean(), default=False)

    @classmethod
    def create(cls, **kw):
        def extract_email_type():
            if re.fullmatch('(.*@(yandex|ya)\.(ru|com))', kw['email']):
                return UserEmailType.yandex.value
            elif re.fullmatch('(.*@gmail\.com)', kw['email']):
                return UserEmailType.google.value
            else:
                return UserEmailType.other.value

        kw = dict(kw, email_type=extract_email_type())
        user = cls(**kw)
        try:
            with db_session(db) as session:
                session.add(user)
        except IntegrityError:
            raise UserAlreadyExists
        return user


class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'))
    user_agent = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())


class Password(db.Model):
    __tablename__ = 'passwords'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'))
    password = Column(String(512), nullable=False)


class OAuthAccount(db.Model):
    __tablename__ = 'oauth_account'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'))
    oauth_id = Column(String(255), nullable=False, unique=True)
    oauth_provider = Column(Enum(OAuthName), nullable=False)
