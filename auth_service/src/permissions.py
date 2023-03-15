from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity

from db.config import db
from service.account import AccountService
from service.roles import RoleService

role_service = RoleService(db)
account_service = AccountService(db)


def role_required(role: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            is_superuser = role_service.is_superuser(user_id)
            roles_list = role_service.get_user_roles(user_id=user_id)

            roles_names = [r.name for r in roles_list]

            if (role in roles_names) or is_superuser:
                return fn(*args, **kwargs)
            return {'msg': 'You have no permission'}, HTTPStatus.FORBIDDEN

        return decorator

    return wrapper
