# coding: utf-8

from .model import Model


class PDF(Model):

    """PDF object.

    {
        'pdf_id': 'pdf id',
        'compiled_time': 'timestamp',
        'data': 'binary data'
    }

    """

    name = 'pdfs'
    id_key = 'pdf_id'

    def __init__(self, pdf_id=None, data=None):

        """Init a PDF object."""

        self.pdf_id = pdf_id
        self.compiled_time = None
        self.data = data

