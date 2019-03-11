# coding: utf-8

from .model import Model


class Task(Model):

    """Task object.

    {
        "task_id": "task id",
        "status": "new" or "compiling" or "finished",
        "user_id": "user id",
        "latex": "latex document",
        "pdf_b64": "compiled pdf content"
    }

    """

    name = "tasks"
    id_key = "task_id"

    def __init__(self, task_id=None, user_id=None, status="new", latex="", **other):
        """Init a task."""

        self.task_id = task_id
        self.user_id = user_id
        self.status = status
        self.latex = latex
