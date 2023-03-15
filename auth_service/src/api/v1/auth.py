from http import HTTPStatus
from operator import itemgetter

from flask import (
    request,
    url_for
)

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Namespace, Resource

from api.v1.swagger.models import login_model, common_model, login_history_model, login_session_model
from api.v1.swagger.parsers import register_parser, login_parser, logout_parser, login_history_parser, edit_user_parser, \
    base_parser, oauth_login_parser
from db.config import db, token_storage
from db.models import User, OAuthName
from limiter import limiter
from oauth import oauth
from service.account import AccountService
from service.exceptions import UserAlreadyExists, UserDoesntExists, WrongPassword, EditUserException
from service.oauth_provider import OAuthProviderService
from settings import settings
from util.util import user_session_to_dict

auth_api = Namespace('v1/auth', description='Role requests')
account_service = AccountService(db)
oauth_service = OAuthProviderService(db)

auth_api.models[login_model.name] = login_model
auth_api.models[common_model.name] = common_model
auth_api.models[login_history_model.name] = login_history_model
auth_api.models[login_session_model.name] = login_session_model


@auth_api.route('/register')
class Register(Resource):
    @limiter.limit('60 per minute')
    @auth_api.expect(register_parser)
    @auth_api.marshal_with(common_model)
    def post(self):
        user_name, password, email = itemgetter('login', 'password', 'email')(request.args)
        try:
            account_service.register(user_name, password, email)
        except UserAlreadyExists:
            pass
        return {'msg': 'Account created'}, HTTPStatus.OK


@auth_api.route('/login')
class Login(Resource):
    @limiter.limit('60 per minute')
    @auth_api.expect(login_parser)
    @auth_api.marshal_with(login_model, skip_none=True)
    def post(self):
        user_name, password = itemgetter('login', 'password')(request.args)
        try:
            user = account_service.login(login=user_name, password=password)
        except UserDoesntExists:
            return {'msg': 'Authorization Error'}, HTTPStatus.UNAUTHORIZED
        except WrongPassword:
            return {'msg': 'Authorization Error'}, HTTPStatus.UNAUTHORIZED
        tokens = _authorize_user(user, request.headers['User-Agent'])
        return tokens, HTTPStatus.OK


@auth_api.route('/logout')
class Logout(Resource):
    @limiter.limit('60 per minute')
    @auth_api.expect(logout_parser)
    @auth_api.marshal_with(common_model, skip_none=True)
    def get(self):
        access_token = decode_token(request.headers['Access-Token'])
        refresh_token = decode_token(request.headers['Refresh-Token'])
        token_storage.set_value(access_token['jti'], '', time_to_leave=settings.jwt.access_token_expire_time)
        token_storage.set_value(refresh_token['jti'], '', time_to_leave=settings.jwt.refresh_token_expire_time)
        return {'msg': 'Successfully logged out'}, HTTPStatus.OK


@auth_api.route('/login-history')
class LoginHistory(Resource):
    @limiter.limit('60 per minute')
    @jwt_required()
    @auth_api.expect(login_history_parser)
    @auth_api.marshal_with(login_history_model, skip_none=True)
    def get(self):
        page_size, page_number = itemgetter('page_size', 'page_number')(request.args)
        user_id = get_jwt_identity()
        paginated = account_service.get_user_sessions(user_id, page_size, page_number)

        user_sessions_dicts = [user_session_to_dict(user_session) for user_session in paginated.items]
        response_data = {
            'data': user_sessions_dicts,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'total_pages': paginated.pages,
            'page_size': paginated.per_page,
            'current_page': paginated.page,
        }
        return response_data, HTTPStatus.OK


@auth_api.route('/edit-user')
class EditUser(Resource):
    @limiter.limit('60 per minute')
    @jwt_required()
    @auth_api.expect(edit_user_parser)
    @auth_api.marshal_with(common_model, skip_none=True)
    def post(self):
        user_id = get_jwt_identity()
        user_name = request.form.get('login')
        password = request.form.get('password')
        email = request.form.get('email')
        try:
            account_service.edit_user(user_id, user_name, email, password)
        except EditUserException:
            return {'msg': 'Edit user error'}, HTTPStatus.BAD_REQUEST
        return {'msg': 'Edit user success'}, HTTPStatus.OK


@auth_api.route('/refresh-token')
class RefreshToken(Resource):
    @limiter.limit('60 per minute')
    @jwt_required(refresh=True)
    @auth_api.expect(base_parser)
    @auth_api.marshal_with(login_model, skip_none=True)
    def post(self):
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)
        refresh_token_jti = get_jwt()['jti']
        token_storage.set_value(refresh_token_jti, '', time_to_leave=settings.jwt.refresh_token_expire_time)
        return {'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.OK


@auth_api.route('/redirect-google')
class GoogleAuthorize(Resource):
    @limiter.limit('60 per minute')
    @auth_api.marshal_with(login_model, skip_none=True)
    def get(self):
        args = oauth_login_parser.parse_args()
        user_info = oauth.google.authorize_access_token()['userinfo']
        try:
            user = oauth_service.login(user_info['sub'], OAuthName.google.value)
        except UserDoesntExists:
            oauth_service.register_user(user_info['sub'], OAuthName.google.value, user_info['email'])
            user = oauth_service.login(user_info['sub'], OAuthName.google.value)
        tokens = _authorize_user(user, args['User-Agent'])
        return tokens, HTTPStatus.OK


@auth_api.route('/login-google')
class GoogleLogin(Resource):
    @limiter.limit('60 per minute')
    def get(self):
        redirect_uri = url_for('v1/auth_google_authorize', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)


@auth_api.route('/usercheck')
class UserCheck(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        return {'user_id': user_id}


def _authorize_user(user: User, user_agent: str) -> dict:
    additional_claims = {'user_email': user.email}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.id)
    account_service.register_user_session(user.id, user_agent)
    return {'access_token': access_token, 'refresh_token': refresh_token}
