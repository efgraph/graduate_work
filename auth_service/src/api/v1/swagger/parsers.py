from flask_restx import reqparse

base_parser = reqparse.RequestParser()
base_parser.add_argument('jwt', type=str, required=True, location='args')

login_parser = reqparse.RequestParser()
login_parser.add_argument('login', type=str, required=True, location='args')
login_parser.add_argument('password', type=str, required=True, location='args')

register_parser = reqparse.RequestParser()
register_parser.add_argument('login', type=str, required=True, location='args')
register_parser.add_argument('password', type=str, required=True, location='agrs')
register_parser.add_argument('email', type=str, required=True, location='args')

edit_user_parser = base_parser.copy()
edit_user_parser.add_argument('login', type=str, required=True, location='form')
edit_user_parser.add_argument('password', type=str, required=True, location='form')
edit_user_parser.add_argument('email', type=str, required=True, location='form')

logout_parser = reqparse.RequestParser()
logout_parser.add_argument('Access-Token', type=str, required=True, location='headers')
logout_parser.add_argument('Refresh-Token', type=str, required=True, location='headers')

login_history_parser = base_parser.copy()
login_history_parser.add_argument('page_size', type=int, default=10, location='args')
login_history_parser.add_argument('page_number', type=int, default=1, location='args')

user_role_get_parser = base_parser.copy()
user_role_get_parser.add_argument('login', type=str, required=True, location='args')

user_role_edit_parser = base_parser.copy()
user_role_edit_parser.add_argument('login', type=str, required=True, location='form')
user_role_edit_parser.add_argument('role_name', type=str, required=True, location='form')

role_create_parser = base_parser.copy()
role_create_parser.add_argument('name', type=str, required=True, location='form')
role_create_parser.add_argument('description', type=str, required=False, location='form')

role_edit_parser = base_parser.copy()
role_edit_parser.add_argument('name', type=str, required=True, location='form')
role_edit_parser.add_argument('new_name', type=str, required=False, location='form')
role_edit_parser.add_argument('new_description', type=str, required=False, location='form')

role_delete_parser = base_parser.copy()
role_delete_parser.add_argument('name', type=str, required=True, location='args')

oauth_login_parser = reqparse.RequestParser()
oauth_login_parser.add_argument('User-Agent', location='headers')
