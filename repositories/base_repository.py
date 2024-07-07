from abc import ABC, abstractmethod
from entities import Response
from typing import Any


class BaseRepository(ABC):

    def __init__(self, collection: str):
        self.collection = collection
        """
            Base repository class
            Args:
                collection: the collection name to work with
        """

    @abstractmethod
    def create_object(self, data: dict) -> Response:
        """
            Create a new record with the data in the specified collection
            Args:
                data: (dict) the record to create
            Returns:
                response: a response object
                    response.response (dict): a dict with the object created with the database id
        """

    @abstractmethod
    def read_collection(self) -> Response:
        """
            Reads all records from a collection
            Returns:
                - response: a response object
                    response.response_list (list): a dict's list with all the record found in the specified collection
        """

    @abstractmethod
    def read_object_by_id(self, object_id: str) -> Response:
        """
            Reads one record from the collection and id
            Args:
                object_id(str): a string with the object id
            Returns:
                response: a response object
                    response.response (dict): a dict with the record found in the database
        """

    @abstractmethod
    def read_objects_with_equal(self, field: str, value: Any) -> Response:
        """
            Reads records from the specified collection when a field is equal to a value
            Args:
                field(str): a string with the field
                value(str): a string with the value to be equal
            Returns:
                response: a response object
                    response.response_list (list): a dict's list with all the records found in the specified collection
        """

    @abstractmethod
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

    @abstractmethod
    def delete_object_by_id(self, object_id: str) -> Response:
        """
            Delete a record from the specified collection and id
            Args:
                object_id(str): a string with the object id
            Returns:
                response: a response object
        """

    @abstractmethod
    def massive_update_with_equal(self, field, value, field_to_update, value_to_update) -> Response:
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
