from flask_restx import Namespace, Resource

health_check_api = Namespace('v1/health_check', description='Health check')


@health_check_api.route('')
class HealthCheck(Resource):

    def get(self):
        return {"message": "OK"}
