# coding: utf-8

from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse

from models.users import User
from models.pdfs import PDF
from models.tasks import Task
from models.model import ModelError, ModelNotExistError


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('html', type=str)


class UserAPI(Resource):

    def get(self, user_id):
        user = User(user_id=user_id)
        try:
            user.load_from_db()
            return user.to_dict()
        except ModelError as e:
            return {'error': str(e)}, 404

    def post(self):
        user = User()
        try:
            user_dict = user.create_in_db()
            return user_dict, 201
        except ModelError as e:
            return {'error': str(e)}, 500

    def delete(self, user_id):
        user = User(user_id=user_id)
        try:
            user.delete_in_db()
            return '', 204
        except ModelError as e:
            return {'error': str(e)}, 404


class PDFAPI(Resource):

    def get(self, pdf_id):
        pdf = PDF(pdf_id=pdf_id)
        try:
            pdf.load_from_db()
            return pdf.to_dict()
        except ModelError as e:
            return {'error': str(e)}, 404


class TaskAPI(Resource):

    def get(self, task_id):
        task = Task(task_id=task_id)
        try:
            task.load_from_db()
            return task.to_dict()
        except ModelError as e:
            return {'error': str(e)}, 404

    def post(self):
        args = parser.parse_args()
        task = Task(html=args['html'])
        try:
            task_dict = task.create_in_db()
            return task_dict, 201
        except ModelError as e:
            return {'error': str(e)}, 500


api.add_resource(UserAPI, '/users', '/users/<user_id>')
api.add_resource(PDFAPI, '/pdfs/<pdf_id>')
api.add_resource(TaskAPI, '/tasks', '/tasks/<task_id>')


if __name__ == '__main__':
    app.run(debug=False)
