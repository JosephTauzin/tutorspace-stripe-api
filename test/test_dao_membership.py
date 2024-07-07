import pytest
from unittest.mock import MagicMock
from dao import MembershipDao
from entities import Membership


class TestMembershipDao:
    @pytest.fixture(autouse=True)
    def setup_class(self, mocker):
        mocker.patch.dict("os.environ", {"STRIPE_API": "stripe_api"})
        self.mock_db = mocker.patch("firebase_admin.firestore.client")
        self.dao = MembershipDao()

    #Create membership
    def test_create_membership_success(self, mocker):
        #arrange
        mock_membership = Membership(
            name="Record 1",
            description="description",
            currency="USD",
            price=1000,
            interval="month",
            interval_count=1
        )

        mock_stripe_response = {"id": "test_id", "default_price": "long_string_id"}
        mock_stripe_instance = mocker.patch("stripe.Product.create", return_value=mock_stripe_response)

        mock_insert_response = MagicMock()
        mock_insert_response.update_time = 123
        self.mock_db.return_value.collection.return_value.document.return_value.set.return_value = mock_insert_response

        #act
        response = self.dao.create_membership(mock_membership)

        #assert
        assert response.success is True
        mock_stripe_instance.assert_called_once()
        self.mock_db.return_value.collection.return_value.document.return_value.set.assert_called_once()

    def test_create_membership_exception(self, mocker):
        # arrange
        mock_membership = Membership(
            name="Record 1",
            description="description",
            currency="USD",
            price=1000,
            interval="month",
            interval_count=1
        )
        mock_error = "error"
        mock_stripe_instance = mocker.patch("stripe.Product.create", side_effect=Exception(mock_error))

        # act
        response = self.dao.create_membership(mock_membership)

        # assert
        assert response.success is False
        mock_stripe_instance.assert_called_once()

    #Read membership
    def test_read_memberships_success(self):
        #arrange
        mock_record1 = MagicMock()
        mock_record1.to_dict.return_value = {
            "name": "Record 1",
            "description": "description",
            "price": 1,
            "currency": "USD",
            "interval": "month",
            "interval_count": 1
        }
        mock_record2 = MagicMock()
        mock_record2.to_dict.return_value = {
            "name": "Record 2",
            "description": "description 2",
            "price": 1,
            "currency": "USD",
            "interval": "month",
            "interval_count": 1
        }

        self.mock_db.return_value.collection.return_value.stream.return_value = [mock_record1, mock_record2]

        #act
        response = self.dao.read_memberships()

        #assert
        assert response.success is True
        assert response.response_list == [Membership(**mock_record1.to_dict()), Membership(**mock_record2.to_dict())]
        self.mock_db.return_value.collection.return_value.stream.assert_called_once()

    def test_read_memberships_no_records(self):
        #arrange
        self.mock_db.return_value.collection.return_value.stream.return_value = []

        #act
        response = self.dao.read_memberships()

        #assert
        assert response.success is False
        assert response.response_list == []
        assert response.message == "no_records_found_in_memberships"
        self.mock_db.return_value.collection.return_value.stream.assert_called_once()

    def test_read_memberships_exception(self):
        #arrange
        mock_error = "exception"
        self.mock_db.return_value.collection.return_value.stream.side_effect = Exception(mock_error)

        #act
        response = self.dao.read_memberships()

        #assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.assert_called_once()

    #Read membership by id
    def test_read_membership_by_id_success(self):
        #arrange
        mock_record1 = MagicMock()
        mock_record1.to_dict.return_value = {
            "name": "Record 1",
            "description": "description",
            "price": 1,
            "currency": "USD",
            "interval": "month",
            "interval_count": 1
        }

        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_record1

        #act
        response = self.dao.read_membership_by_id("mock_id")

        #assert
        assert response.success is True
        assert response.response == Membership.model_validate(mock_record1.to_dict())
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    def test_read_membership_by_id_no_records(self):
        #arrange
        mock_db_response = MagicMock()
        mock_db_response.exists = False

        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_db_response

        #act
        response = self.dao.read_membership_by_id("mock_id")

        #assert
        assert response.success is False
        assert response.response == {}
        assert response.message == "no_records_found_in_memberships"
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    def test_read_membership_by_id_exception(self):
        #arrange
        mock_error = "exception"
        self.mock_db.return_value.collection.return_value.document.return_value.get.side_effect = Exception(mock_error)

        #act
        response = self.dao.read_membership_by_id("mock_id")

        #assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    #read objects with equal
    def test_read_enabled_user_memberships_success(self):
        #arrange
        mock_record1 = MagicMock()
        mock_record1.to_dict.return_value = {
            "name": "Record 1",
            "description": "description",
            "price": 1,
            "currency": "USD",
            "interval": "month",
            "interval_count": 1
        }

        self.mock_db.return_value.collection.return_value.where.return_value.stream.return_value = [mock_record1]

        mock_user = MagicMock()
        mock_user.Admin = False
        mock_user.Type = "Individual"

        #act
        response = self.dao.read_enabled_user_memberships(mock_user)

        #assert
        assert response.success is True
        assert response.response_list == [Membership.model_validate(mock_record1.to_dict())]
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called_once()

    def test_read_enabled_user_memberships_no_records(self):
        #arrange
        self.mock_db.return_value.collection.return_value.where.return_value.stream.return_value = []

        mock_user = MagicMock()
        mock_user.Admin = False
        mock_user.Type = "Individual"

        # act
        response = self.dao.read_enabled_user_memberships(mock_user)

        #assert
        assert response.success is False
        assert response.message == "no_records_found_in_memberships"
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called_once()

    def test_read_enabled_user_memberships_exception(self):
        # arrange
        mock_error = "exception"
        self.mock_db.return_value.collection.return_value.where.return_value.stream.side_effect = Exception(mock_error)

        mock_user = MagicMock()
        mock_user.Admin = False
        mock_user.Type = "Individual"

        # act
        response = self.dao.read_enabled_user_memberships(mock_user)

        # assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called_once()
