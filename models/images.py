# coding: utf-8

import time
from .users import User
from .model import Model, ModelError


class Image(Model):

    """PDF object.

    {
        'image_id': 'image id',
        'user_id': 'user id',
        'uploaded_time': 'timestamp',
        'content': 'bytes',
        'hash': 'hash string'
    }

    """

    name = 'images'
    id_key = 'image_id'
    custom_id = True

    def __init__(self, image_id=None, user_id=None,
                 content=None, uploaded_time=None):

        """Init an Image object."""
        self.image_id = image_id
        self.user_id = user_id
        self.uploaded_time = uploaded_time
        if not self.uploaded_time:
            self.uploaded_time = str(int(time.time()))
        self.content = content

    def load_from_db(self):
        if not self.user_id:
            raise ModelError('No user id provided')
        user = User(user_id=self.user_id)
        user.load_from_db()
        return super().load_from_db()

    def create_in_db(self):
        if not self.user_id:
            raise ModelError('No user id provided')
        user = User(user_id=self.user_id)
        user.load_from_db()
        return super().create_in_db()

