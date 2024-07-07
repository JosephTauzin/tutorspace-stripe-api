from . import BaseRepository
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from entities import Response
from typing import Any


class FirestoreRepository(BaseRepository):

    def __init__(self, collection: str) -> None:
        """
            A database helper for interact with firebase realtime database
            Param:
                collection: a string with the collection name
        """
        super().__init__(collection)
        self.db = firestore.client()

    def create_object(self, data: dict) -> Response:
        """
            Create a new record with the data in the specified collection
            Args:
                data: (dict) the record to create
            Returns:
                response: a response object
                    response.response (dict): a dict with the object created with the database id
        """
        response = Response()

        try:
            reference = self.db.collection(self.collection).document()
            data["id"] = reference.id
            result = reference.set(data)

            response.success = True if (result.update_time) else False
            if (response.success):
                response.response = data
        except Exception as e:
            response.message = str(e)

        return response

    def read_collection(self) -> Response:
        """
            Reads all records from the specified collection
            Returns:
                response: a response object
                    response.response_list (list): a dict's list with all the record found in the specified collection
        """
        response = Response()

        try:
            records = self.db.collection(self.collection).stream()
            response.response_list = [record.to_dict() for record in records]

            records_exists = True if (len(response.response_list) > 0) else False

            response.message = "" if (records_exists) else "no_records_found_in_" + self.collection
            response.success = records_exists
        except Exception as e:
            response.message = str(e)

        return response

    def read_object_by_id(self, object_id: str) -> Response:
        """
            Reads one record from the specified collection and id
            Args:
                object_id(str): a string with the object id
            Returns:
                response: a response object
                    response.response (dict): a dict with the record found in the database
        """
        response = Response()

        try:
            record = self.db.collection(self.collection).document(object_id).get()

            if (not record.exists):
                response.message = "no_records_found_in_" + self.collection
            else:
                response.response = record.to_dict()
                response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def read_objects_with_equal(self, field: str, value: Any) -> Response:
        """
            Reads records from the specified collection when a field is equal to a value
            Args:
                field(str): a string with the field
                value: a value with the value to be equal
            Returns:
                response: a response object
                    response.response_list (list): a dict's list with all the records found in the specified collection
        """
        response = Response()

        try:
            reference = self.db.collection(self.collection)
            equal_operator = "array_contains" if (field == "type_") else "=="  # type_ is an array in the database
            records = reference.where(filter=FieldFilter(field, equal_operator, value)).stream()

            response.response_list = [record.to_dict() for record in records]
            records_exists = True if (len(response.response_list) > 0) else False

            response.message = "" if (records_exists) else "no_records_found_in_" + self.collection
            response.success = records_exists
        except Exception as e:
            response.message = str(e)

        return response

    def update_object_by_id(self, object_id: str, data: dict) -> Response:
        """
            Updates an existing record from the specified collection and id
            Args:
                object_id(str): a string with the object id
                data (dict): a dictionary with the fields to update
            Returns:
                response: a response object
                    response.response (dict):  a dict with the record updated in the database
        """
        response = Response()

        try:
            result = self.db.collection(self.collection).document(object_id).update(data)
            record = self.db.collection(self.collection).document(object_id).get()

            response.success = True if (result.update_time) else False
            if (response.success):
                response.response = record.to_dict()

        except Exception as e:
            response.message = str(e)

        return response

    def delete_object_by_id(self, object_id: str) -> Response:
        """
            Delete a record from the specified collection and id
            Args:
                object_id(str): a string with the object id
            Returns:
                response: a response object
        """
        response = Response()

        try:
            result = self.db.collection(self.collection).document(object_id).delete()
            response.success = True if (len(result.transform_results) > 0) else False
        except Exception as e:
            response.message = str(e)

        return response

    def massive_update_with_equal(self, field, value, field_to_update, value_to_update):
        """
            Performs a massive update of field(field_to_update=value_to_update) with a condition(field==value)
            Args:
                field: the name of the field to look for the update
                value: the value that must be equal to compare
                field_to_update: the new field to update/insert
                value_to_update: the value for the new field
            Returns:
                - response: a response object with the result
        """
        response = Response()

        try:
            reference = self.db.collection(self.collection)
            records = reference.where(filter=FieldFilter(field, "==", value)).stream()

            batch = self.db.batch()

            for record in records:
                record = record.to_dict()
                record_ref = self.db.collection(self.collection).document(record["id"])
                batch.update(record_ref, {field_to_update: value_to_update})

            batch.commit()
            response.success = True

        except Exception as e:
            response.message = str(e)

        return response
