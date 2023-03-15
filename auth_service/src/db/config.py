from contextlib import contextmanager

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from settings import settings
from db.token_storage import TokenStorage

metadata = MetaData(schema='content')

db = SQLAlchemy()
migrate = Migrate()

token_storage = TokenStorage(redis_host=settings.redis.host, redis_port=settings.redis.port)


@contextmanager
def db_session(db: SQLAlchemy):
    try:  # noqa: WPS229
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
