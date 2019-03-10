# coding: utf-8

from .model import Model


class User(Model):

    """User object.

    {
        'user_id': 'user id',
        'compiled_pdfs'
    }

    """

    name = 'users'
    id_key = 'user_id'

    def __init__(self, user_id=None, compiled_pdfs=[]):

        """Init a user."""

        self.user_id = user_id
        self.compiled_pdfs = compiled_pdfs

