from flask import Blueprint
from flask_restful_swagger import swagger
from flask_restful import Resource, Api, reqparse, fields
from app.primers import s
from app.primers import app
import json



api_blueprint = Blueprint('api_blueprint', __name__)

api = swagger.docs(Api(api_blueprint), apiVersion='0.0', api_spec_url='/spec', description="Primers API")

@api.representation('application/json')
def output_json(data, code, headers=None):
    # todo marshal breaks swagger here - swaggermodels?
    resp = app.make_response(json.dumps(data))
    resp.headers.extend(headers or {})
    return resp

class APIVirtualPanels(Resource):
    @swagger.operation(
        notes='Gets a JSON of regions in a virtual panel - this is equivalent to the small panel',
        responseClass='x',
        nickname='small',
        parameters=[
            {
                "name": "extension",
                "paramType": "query",
                "required": False,
                "allowMultiple": False,
                "dataType": "integer"
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created. The URL of the created blueprint should be in the Location header"
            },
            {
                "code": 405,
                "message": "Invalid input"
            }
        ]
    )
    def get(self):
        resp = "hello"
        # result = get_vpanel_api(s, name, version)
        # result_json = region_result_to_json(result.result)
        # result_json["details"]["panel"] = name
        # result_json["details"]["version"] = int(result.current_version)
        # resp = output_json(result_json, 200)
        # resp.headers['content-type'] = 'application/json'
        return resp


api.add_resource(APIVirtualPanels, '/test', )