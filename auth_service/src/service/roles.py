from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db.config import db_session
from db.models import Role, RolesUsers, User
from service.exceptions import RoleAlreadyExists, RoleDoesntExists, RelationDoesntExists


class RoleService:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_role(
            self,
            name: str,
            description: str = "",
    ):
        role = Role(
            name=name,
            description=description,
        )
        try:
            with db_session(self.db) as session:
                session.add(role)
        except IntegrityError:
            raise RoleAlreadyExists
        return role

    def get_all_roles(self):
        return Role.query.all()

    def edit_role(
            self,
            name: str,
            new_name: str,
            new_description,
    ) -> None:
        role = Role.query.filter_by(name=name).first()
        if new_name:
            try:
                with db_session(self.db):
                    role.name = new_name
            except IntegrityError:
                raise RoleAlreadyExists

        if new_description:
            with db_session(self.db):
                role.description = new_description

    def delete_role(self, name: str):
        role = Role.query.filter_by(name=name).first()
        try:
            with db_session(self.db) as session:
                session.delete(role)
        except UnmappedInstanceError:
            raise RoleDoesntExists

    def set_user_role(self, login: str, role_name: str):
        user = User.query.filter_by(login=login).first()
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise RelationDoesntExists
        user_role = RolesUsers(user_id=user.id, role_id=role.id)

        with db_session(self.db) as session:
            session.add(user_role)

    def delete_user_role(self, login: str, role_name: str):
        role = Role.query.filter_by(name=role_name).first()
        user = User.query.filter_by(login=login).first()
        user_role = RolesUsers.query.filter_by(user_id=user.id, role_id=role.id).first()
        try:
            with db_session(self.db) as session:
                session.delete(user_role)
        except UnmappedInstanceError:
            raise RelationDoesntExists

    def get_user_roles(self, login: str = "", user_id: str = ""):
        if not user_id:
            user = User.query.filter_by(login=login).first()
            user_id = user.id
        user_role_ids = [role_user.role_id for role_user in RolesUsers.query.filter_by(user_id=user_id).all()]
        roles = Role.query.filter(Role.id.in_(user_role_ids)).all()

        return roles;

    def is_superuser(self, user_id: str):
        return User.query.filter_by(id=user_id).first().is_superuser


