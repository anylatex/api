# coding: utf-8

from .model import Model


class Task(Model):

    """Task object.

    {
        "task_id": "same to user's id",
        "status": boolean
    }

    """

    name = "tasks"
    id_key = "task_id"

    def __init__(self, task_id=None, status=False, html=""):
        """Init a task."""

        self.task_id = task_id
        self.status = status
        self.html = html

