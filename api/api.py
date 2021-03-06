# coding: utf-8

import os
import io
import json
import base64

from flask import Flask, request, send_file
from flask_restful import Resource, Api
from flask_restful import reqparse

from models.users import User
from models.pdfs import PDF
from models.tasks import Task
from models.images import Image
from models.model import ModelError, ModelNotExistError


app = Flask(__name__)
api = Api(app)
script_dir = os.path.dirname(os.path.realpath(__file__))
script_dir = os.path.dirname(script_dir)


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
            pdf_content = base64.b64decode(pdf.data)
            length = len(pdf_content)
            response = send_file(
                io.BytesIO(pdf_content),
                attachment_filename=pdf.pdf_id+'.pdf',
                mimetype='application/pdf'
            )
            response.headers['Content-Length'] = str(length)
            return response
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
        parser = reqparse.RequestParser()
        parser.add_argument('body', type=str, required=True)
        parser.add_argument('args', type=str, required=True)
        parser.add_argument('template', type=str, required=True)
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('document_id', type=str, required=True)
        parser.add_argument('part_args', type=str, required=True)
        parser.add_argument('images', type=str, required=True)
        args = parser.parse_args()
        args['args'] = json.loads(args['args'])
        args['part_args'] = json.loads(args['part_args'])
        args['images'] = json.loads(args['images'])
        task = Task(**args)
        try:
            task_dict = task.create_in_db()
            return task_dict, 202
        except ModelError as e:
            return {'error': str(e)}, 500

    def delete(self, task_id):
        task = Task(task_id=task_id)
        try:
            task.delete_in_db()
            return '', 204
        except ModelError as e:
            return {'error': str(e)}, 404


class TemplatesAPI(Resource):

    def get(self):
        config_file = os.path.join(script_dir, 'config.json')
        with open(config_file, 'r') as f:
            config = json.load(f)
        templates = config.get('templates', {})
        return templates, 200


class ImagesAPI(Resource):

    def get(self, image_id):
        parser = reqparse.RequestParser()
        parser.add_argument('check', type=str, required=False)
        parser.add_argument('user_id', type=str, required=True)
        args = parser.parse_args()
        user_id = args['user_id']
        image = Image(image_id=image_id, user_id=user_id)
        try:
            user = User(user_id=user_id)
            user.load_from_db()
            image.load_from_db()
            # if image.user_id != user_id:
            #    error_info = 'User %s has no image: %s' % (user_id, image_id)
            #     raise ModelNotExistError(error_info)
            image_dict = image.to_dict()
            if args.get('check') == 'true':
                image_dict.pop('content')
            return image_dict, 200
        except ModelError as e:
            return {'error': str(e)}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        parser.add_argument('image_id', type=str, required=True)
        args = parser.parse_args()
        image = Image(image_id=args['image_id'],
                      user_id=args['user_id'], content=args['content'])
        try:
            image_dict = image.create_in_db()
            return image_dict, 201
        except ModelError as e:
            return {'error': str(e)}, 500


api.add_resource(UserAPI, '/api/users', '/api/users/<user_id>')
api.add_resource(PDFAPI, '/api/pdfs/<pdf_id>')
api.add_resource(TaskAPI, '/api/tasks', '/api/tasks/<task_id>')
api.add_resource(TemplatesAPI, '/api/templates')
api.add_resource(ImagesAPI, '/api/images', '/api/images/<image_id>')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)
