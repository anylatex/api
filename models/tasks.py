# coding: utf-8

from .model import Model


class Task(Model):

    """Task object.

    {
        "task_id": "task id",
        "status": "new" or "compiling" or "finished",
        "user_id": "user id",
        "document_id": "document's id",
        "template": "template to use",
        "args": "arguments",
        "part_args": "arguments show in editor",
        "images": "list of image names"
        "pdf_id": "compiled pdf's id"
    }

    """

    name = "tasks"
    id_key = "task_id"

    def __init__(self, task_id=None, user_id=None, document_id=None,
                 status="new", template="", args={},
                 part_args={}, body="", images=[], **other):
        """Init a task."""

        self.task_id = task_id
        self.user_id = user_id
        self.document_id = document_id
        self.status = status
        self.template = template
        self.args = args
        self.part_args = part_args
        self.body = body
        self.images = images

