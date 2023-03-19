import click
from flask import (
    Flask,
)
from flask_restx import Api

from api.v1.health_check import health_check_api
from enums import SubscriptionStatus
from oauth import oauth
from api.v1.auth import auth_api
from api.v1.role import role_api
from settings import settings
from db.config import (
    db,
    migrate,
)
from jwt_config import jwt
from service.roles import RoleService
from service.account import AccountService
from service.exceptions import UserAlreadyExists
from limiter import limiter

app = Flask(__name__)

api = Api(app, version='0.1', title='Auth service', doc='/swagger')

app.config['SQLALCHEMY_DATABASE_URI'] = settings.db.dsn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = settings.jwt.secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = settings.jwt.access_token_expire_time
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = settings.jwt.refresh_token_expire_time
app.config['JWT_TOKEN_LOCATION'] = settings.jwt.token_location

oauth.init_app(app)
jwt.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)
app.app_context().push()
api.add_namespace(auth_api)
api.add_namespace(role_api)
api.add_namespace(health_check_api)
app.secret_key = 'super secret key'


@app.cli.command('create-super-user')
@click.argument('name')
@click.argument('password')
@click.argument('email')
def create_super_user(name, password, email):
    with app.app_context():
        account_service = AccountService(db)
        try:
            account_service.register(name, password, email, True)
        except UserAlreadyExists:
            pass


@app.cli.command('create-basic-roles')
def create_super_user():
    with app.app_context():
        role_service = RoleService(db)
        try:
            for status in SubscriptionStatus:
                role_service.create_role(status.value, "basic role")
        except UserAlreadyExists:
            pass
