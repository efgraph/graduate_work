from http import HTTPStatus

from flask import (
    request,
)

from flask_jwt_extended import (
    jwt_required,
)
from flask_restx import Namespace, Resource

from api.v1.swagger.models import common_model, role_model
from api.v1.swagger.parsers import base_parser, role_edit_parser, role_create_parser, role_delete_parser, \
    user_role_get_parser, user_role_edit_parser
from db.config import db
from limiter import limiter
from permissions import role_required
from service.exceptions import RoleAlreadyExists, RoleDoesntExists, RelationDoesntExists
from service.roles import RoleService

role_api = Namespace('v1/role', description='Role requests')
role_service = RoleService(db)

role_api.models[role_model.name] = role_model
role_api.models[common_model.name] = common_model


@role_api.route('')
class Role(Resource):
    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(base_parser)
    @role_api.marshal_with(role_model)
    def get(self):
        roles = [r.name for r in role_service.get_all_roles()]
        return {'roles': str(roles)}, HTTPStatus.OK

    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(role_edit_parser)
    @role_api.marshal_with(common_model)
    def put(self):
        try:
            role_service.edit_role(request.form.get('name'), request.form.get('new_name'),
                                   request.form.get('new_description'))
        except RoleAlreadyExists:
            return {'msg': 'Role already exists'}, HTTPStatus.CONFLICT
        return {'msg': 'Role edited'}, HTTPStatus.OK

    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(role_create_parser)
    @role_api.marshal_with(common_model)
    def post(self):
        try:
            role_service.create_role(
                name=request.form.get('name'),
                description=request.form.get('description'),
            )
        except RoleAlreadyExists:
            return {'msg': 'Role already exists'}, HTTPStatus.CONFLICT
        return {'msg': 'Role created'}, HTTPStatus.OK

    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(role_delete_parser)
    @role_api.marshal_with(common_model)
    def delete(self):
        try:
            role_service.delete_role(request.args['name'])
        except RoleDoesntExists:
            return {'msg': 'Role not found'}, HTTPStatus.NOT_FOUND
        return {'msg': 'Role deleted'}, HTTPStatus.OK


@role_api.route('/user')
class UserRole(Resource):

    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(user_role_get_parser)
    @role_api.marshal_with(role_model)
    def get(self):
        name = request.args['login']
        roles = role_service.get_user_roles(login=name)
        return {'roles': str([role.name for role in roles])}, HTTPStatus.OK

    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(user_role_edit_parser)
    @role_api.marshal_with(common_model)
    def post(self):
        try:
            role_service.set_user_role(request.form.get('login'), request.form.get('role_name'))
        except RelationDoesntExists:
            return {'msg': 'Role not found'}, HTTPStatus.NOT_FOUND
        return {'msg': 'Role set'}, HTTPStatus.OK

    @limiter.limit('60 per minute')
    @jwt_required()
    @role_required('admin')
    @role_api.expect(user_role_edit_parser)
    @role_api.marshal_with(common_model)
    def delete(self):
        try:
            role_service.delete_user_role(request.form.get('login'), request.form.get('role_name'))
        except RelationDoesntExists:
            return {'msg': 'Role not found'}, HTTPStatus.NOT_FOUND
        return {'msg': 'Role removed'}, HTTPStatus.OK
