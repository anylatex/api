# coding: utf-8

from .db import DB


class ModelError(Exception):

    def __init__(self, info=''):
        super().__init__(self)
        self.info = info

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.info


class ModelNotExistError(ModelError):
    pass


class Model:

    """Base model.

        All model classes should have cls.name and cls.id_key.

    """

    def to_dict(self):
        """Get dict format of this object."""
        # generate object's document
        cls_members = [
            attr for attr in vars(self)
            if not attr.startswith("_")
        ]
        document = {
            member: getattr(self, member)
            for member in cls_members
        }
        return document

    def _find_one_in_db(self, object_id):
        cls_name = self.__class__.name
        try:
            raw_object = DB.find_one(cls_name, {"_id": object_id})
            return raw_object
        except Exception as e:
            raise ModelError(str(e))

    def exists_in_db(self):
        """Check if this id in db."""
        cls = self.__class__
        object_id = getattr(self, cls.id_key)
        if not object_id:
            info = "Check if exists in db failed: no id in this {} instance."
            raise ModelError(info.format(cls.__name__))
        raw_object = self._find_one_in_db(object_id)
        if raw_object:
            return True
        else:
            return False

    def load_from_db(self):
        """Load from DB using id."""

        cls = self.__class__

        # check
        object_id = getattr(self, cls.id_key)
        if not object_id:
            info = "Load from db failed: no id({}) in this {} instance."
            raise ModelError(info.format(cls.id_key, cls.__name__))
        raw_object = self._find_one_in_db(object_id)
        if not raw_object:
            info = "Load from db failed: no {} document in db of id {}"
            raise ModelNotExistError(info.format(cls.__name__, object_id))

        # load data
        for key, value in raw_object.items():
            if key == '_id':
                setattr(self, cls.id_key, value)
            else:
                setattr(self, key, value)

    def create_in_db(self):
        """Create this document, id should be None.
            Return:
                object's dict
        """

        cls = self.__class__

        # check
        object_id = getattr(self, cls.id_key)
        if object_id:
            info = "Create in db failed: has id({}) in this {} instance."
            raise ModelError(info.format(object_id, cls.__name__))

        # generate object's document
        document = self.to_dict()
        document.pop(cls.id_key)

        # create
        # TODO: check if success
        object_id = DB.create_one(cls.name, document)
        setattr(self, cls.id_key, object_id)
        document[cls.id_key] = object_id
        return document

    def update_to_db(self):
        """Update this document, should have an id."""

        cls = self.__class__

        # check
        object_id = getattr(self, cls.id_key)
        if not object_id:
            info = "Update to db failed: no id({}) in this {} instance."
            raise ModelError(info.format(cls.id_key, cls.__name__))
        raw_object = self._find_one_in_db(object_id)
        if not raw_object:
            info = "Update to db failed: no {} document with id({}) in db."
            raise ModelNotExistError(info.format(cls.__name__, object_id))

        # generate object's document
        document = self.to_dict()
        document.pop(cls.id_key)

        # update
        # TODO: check if success
        DB.update_one(cls.name, {'_id': object_id}, document)

    def delete_in_db(self):
        """Delete this document, should have an id."""

        cls = self.__class__

        # check
        object_id = getattr(self, cls.id_key)
        if not object_id:
            info = "Delete in db failed: no id({}) in this {} instance."
            raise ModelError(info.format(cls.id_key, cls.__name__))
        raw_object = self._find_one_in_db(object_id)
        if not raw_object:
            info = "Delete in db failed: no {} document with id({}) in db."
            raise ModelNotExistError(info.format(cls.__name__, object_id))

        # generate object's document
        document = self.to_dict()
        document.pop(cls.id_key)

        # delete
        # TODO: check if success
        DB.delete_one(cls.name, {'_id': object_id})

