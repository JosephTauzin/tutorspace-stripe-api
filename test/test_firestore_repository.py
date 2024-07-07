import pytest
from unittest.mock import MagicMock
from repositories import FirestoreRepository


class TestFirestoreRepository:
    @pytest.fixture(autouse=True)
    def setup_class(self, mocker):
        self.collection = "test_collection"
        self.mock_db = mocker.patch("firebase_admin.firestore.client")
        self.db_instance = FirestoreRepository(self.collection)

    #create_object

    def test_create_object_success(self):
        #arrange
        new_object_id = "new_id"
        data = {"name": "test_record", "id": new_object_id}

        mock_response = MagicMock()
        mock_response.update_time = 123456789

        mock_response_id = MagicMock()
        mock_response_id.id = new_object_id

        self.mock_db.return_value.collection.return_value.document.return_value = mock_response_id
        self.mock_db.return_value.collection.return_value.document.return_value.set.return_value = mock_response

        #act
        response = self.db_instance.create_object(data)

        #assert
        assert response.success is True
        assert response.response["id"] == data["id"]
        assert response.response["name"] == data["name"]

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.return_value.set.assert_called_once_with(data)

    def test_create_object_exception(self):
        #arrange
        exception = "Database Error"
        self.mock_db.return_value.collection.return_value.document.side_effect = Exception(exception)

        #act
        response = self.db_instance.create_object({})

        #assert
        assert response.success is False
        assert response.message == exception

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)

    #read_collection
    def test_read_collection_success(self):
        #arrange
        mock_record1 = MagicMock()
        mock_record1.to_dict.return_value = {"id": "1", "name": "Record 1"}
        mock_record2 = MagicMock()
        mock_record2.to_dict.return_value = {"id": "2", "name": "Record 2"}

        self.mock_db.return_value.collection.return_value.stream.return_value = [mock_record1, mock_record2]

        #act
        response = self.db_instance.read_collection()

        #assert
        assert response.success is True
        assert response.response_list == [{"id": "1", "name": "Record 1"}, {"id": "2", "name": "Record 2"}]

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.stream.assert_called()

    def test_read_collection_no_records(self):
        #arrange
        self.mock_db.return_value.collection.return_value.stream.return_value = []

        #act
        response = self.db_instance.read_collection()

        #assert
        assert response.success is False
        assert response.response_list == []

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.stream.assert_called()

    def test_read_collection_exception(self):
        #arrange
        exception = "Database error"
        self.mock_db.return_value.collection.return_value.stream.side_effect = Exception(exception)

        #act
        response = self.db_instance.read_collection()

        #assert
        assert response.success is False
        assert response.message == exception
        assert response.response_list == []

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)

    #read_object_by_id
    def test_read_object_by_id_success(self):
        #arrange
        _id = "new_id"
        mock_record_dict = {"id": _id}
        mock_record = MagicMock()
        mock_record.to_dict.return_value = mock_record_dict
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_record

        #act
        response = self.db_instance.read_object_by_id(_id)

        #assert
        assert response.success is True
        assert response.response == mock_record_dict

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_once_with(_id)
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called()

    def test_read_object_by_id_no_records(self):
        #arrange
        _id = "id"
        no_records_error = "no_records_found_in_" + self.collection
        mock_response = MagicMock()
        mock_response.exists = False

        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_response

        #act
        response = self.db_instance.read_object_by_id(_id)

        #assert
        assert response.success is False
        assert response.message == no_records_error

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_once_with(_id)
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called()

    def test_read_object_by_id_exception(self):
        #arrange
        _id = "id"
        exception = "Database error"
        self.mock_db.return_value.collection.return_value.document.return_value.get.side_effect = Exception(exception)

        #act
        response = self.db_instance.read_object_by_id(_id)

        #assert
        assert response.success is False
        assert response.message == exception
        assert response.response == {}
        assert response.response_list == []

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_once_with(_id)
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called()

    #read_objects_with_equal
    def test_read_objects_with_equal_success(self):
        #arrange
        mock_field = "test_field"
        mock_value = "value"

        mock_record1 = MagicMock()
        mock_record1.to_dict.return_value = {"id": "1", "name": "Record 1"}
        mock_record2 = MagicMock()
        mock_record2.to_dict.return_value = {"id": "2", "name": "Record 2"}

        self.mock_db.return_value.collection.return_value.where.return_value.stream.return_value = [mock_record1, mock_record2]

        #act
        response = self.db_instance.read_objects_with_equal(mock_field, mock_value)

        #assert
        assert response.success is True
        assert response.response_list == [{"id": "1", "name": "Record 1"}, {"id": "2", "name": "Record 2"}]

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.where.assert_called()
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called()

    def test_read_objects_with_equal_no_records(self):
        #arrange
        mock_field = "test_field"
        mock_value = "value"
        self.mock_db.return_value.collection.return_value.where.return_value.stream.return_value = ()

        #act
        response = self.db_instance.read_objects_with_equal(mock_field, mock_value)

        #assert
        assert response.success is False
        assert response.response_list == []

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.where.assert_called()
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called()

    def test_read_objects_with_equal_exception(self):
        #arrange
        exception = "Database Error"
        mock_field = "test_field"
        mock_value = "value"

        self.mock_db.return_value.collection.return_value.where.return_value.stream.side_effect = Exception(exception)

        #act
        response = self.db_instance.read_objects_with_equal(mock_field, mock_value)

        #assert
        assert response.success is False
        assert response.response_list == []
        assert response.message == exception
        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.where.assert_called()
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called()

    #update_object_by_id
    def test_update_object_by_id_success(self):
        #arrange
        mock_object_id = "id1"
        mock_data_to_update = {"name": "new_name"}

        mock_data = {"id": "id1", "name": "new_name"}
        mock_response = MagicMock()
        mock_response.to_dict.return_value = mock_data

        mock_result = MagicMock()
        mock_result.update_time = 1234567890

        self.mock_db.return_value.collection.return_value.document.return_value.update.return_value = mock_result
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_response

        #act
        response = self.db_instance.update_object_by_id(mock_object_id, mock_data_to_update)

        #assert
        assert response.success is True
        assert response.response == mock_data
        self.mock_db.return_value.collection.assert_called_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_with(mock_object_id)
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once_with(mock_data_to_update)
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called()

    def test_update_object_by_id_exception(self):
        #arrange
        exception = "Database error"
        mock_object_id = "id1"
        mock_data_to_update = {"name": "new_name"}
        self.mock_db.return_value.collection.return_value.document.return_value.update.side_effect = Exception(exception)

        #act
        response = self.db_instance.update_object_by_id(mock_object_id, mock_data_to_update)

        #assert
        assert response.success is False
        assert response.response == {}
        assert response.message == exception
        self.mock_db.return_value.collection.assert_called_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_with(mock_object_id)
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once_with(mock_data_to_update)

    #delete_object
    def test_delete_object_by_id_success(self):
        #arrange
        mock_object_id = "new_id"

        mock_result = MagicMock()
        mock_result.transform_results = [{"id": mock_object_id}]
        self.mock_db.return_value.collection.return_value.document.return_value.delete.return_value = mock_result

        #act
        response = self.db_instance.delete_object_by_id(mock_object_id)

        #assert
        assert response.success is True
        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_once_with(mock_object_id)
        self.mock_db.return_value.collection.return_value.document.return_value.delete.assert_called()

    def test_delete_object_by_id_exception(self):
        #arrange
        mock_object_id = "new_id"
        exception = "DB error"
        self.mock_db.return_value.collection.return_value.document.return_value.delete.side_effect = Exception(exception)

        #act
        response = self.db_instance.delete_object_by_id(mock_object_id)

        #assert
        assert response.success is False
        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.document.assert_called_once_with(mock_object_id)
        self.mock_db.return_value.collection.return_value.document.return_value.delete.assert_called()

    #massive_update_with_equal
    def test_massive_update_with_equal_success(self):
        #arrange
        mock_field = "example_field"
        mock_value = "example_value"
        mock_field_to_update = "field_to_update"
        mock_value_to_update = "value_to_update"

        record1 = MagicMock()
        record1.to_dict.return_value = {"id": "1", "name": "Record 1"}
        record2 = MagicMock()
        record2.to_dict.return_value = {"id": "2", "name": "Record 2"}

        self.mock_db.return_value.collection.where.return_value.stream.return_value = [record1, record2]

        #act
        response = (self.db_instance
                    .massive_update_with_equal(mock_field, mock_value, mock_field_to_update, mock_value_to_update))

        #assert
        assert response.success is True
        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
        self.mock_db.return_value.collection.return_value.where.assert_called()
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called_once()

        self.mock_db.return_value.batch.return_value.commit.assert_called_once()

    def test_massive_update_with_equal_exception(self):
        #arrange
        exception = "Database error"
        mock_field = "example_field"
        mock_value = "example_value"
        mock_field_to_update = "field_to_update"
        mock_value_to_update = "value_to_update"

        self.mock_db.return_value.collection.side_effect = Exception(exception)

        #act
        response = (self.db_instance
                    .massive_update_with_equal(mock_field, mock_value, mock_field_to_update, mock_value_to_update))

        #assert
        assert response.success is False
        assert response.message == exception

        self.mock_db.return_value.collection.assert_called_once_with(self.collection)
