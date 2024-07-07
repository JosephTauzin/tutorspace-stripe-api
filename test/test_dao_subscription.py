import pytest
from unittest.mock import MagicMock
from dao import SubscriptionsDao
from entities import Subscription, Membership


class TestSubscriptionDao():
    @pytest.fixture(autouse=True)
    def setup_class(self, mocker):
        mocker.patch.dict("os.environ", {"STRIPE_API": "stripe_api"})
        self.mock_db = mocker.patch("firebase_admin.firestore.client")
        self.dao = SubscriptionsDao()

    #create subscription
    def test_create_subscription_success(self):
        #arrange
        mock_membership = Membership(
            name="Record 1",
            description="description",
            currency="USD",
            price=1000,
            interval="month",
            interval_count=1
        )

        mock_user = MagicMock()
        mock_user.id = "db_id"
        mock_user.Admin = False
        mock_user.stripe_customer_id = "stripe_id"
        mock_user.company_type = "individual_group"

        mock_total_licenses = 4

        mock_insert_response = MagicMock()
        mock_insert_response.update_time = 1234
        self.mock_db.return_value.collection.return_value.document.return_value.id = "new_id"
        self.mock_db.return_value.collection.return_value.document.return_value.set.return_value = mock_insert_response

        #act
        response = self.dao.create_subscription(mock_membership, mock_user, mock_total_licenses)

        #assert
        assert response.success is True
        assert isinstance(response.response, Subscription)
        self.mock_db.return_value.collection.return_value.document.return_value.set.assert_called()

    def test_create_subscription_exception(self):
        # arrange
        mock_membership = Membership(
            name="Record 1",
            description="description",
            currency="USD",
            price=1000,
            interval="month",
            interval_count=1
        )

        mock_user = MagicMock()
        mock_user.id = "db_id"
        mock_user.Admin = False
        mock_user.stripe_customer_id = "stripe_id"
        mock_user.company_type = "individual_group"

        mock_total_licenses = 4
        mock_error = "error"
        self.mock_db.return_value.collection.return_value.document.return_value.set.side_effect = Exception(mock_error)

        # act
        response = self.dao.create_subscription(mock_membership, mock_user, mock_total_licenses)

        # assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.document.return_value.set.assert_called()

    #update subscription by id
    def test_update_subscription_by_id_success(self):
        pass

    def test_update_subscription_by_id_exception(self):
        pass

    #read active subscription
    def test_read_active_subscription_success(self):
        #arrange
        mock_subscription_id = "db_id"
        mock_db_response = MagicMock()
        mock_db_response.exists = True
        mock_db_response.to_dict.return_value = {
            "id": mock_subscription_id,
            "quantity": 1,
            "payment_random_id": "----",
            "stripe_subscription_id": "",
            "stripe_customer_id": "",
            "local_subscription_id": "",
            "local_user_id": "",
            "start_date": 123456,
            "renewal_date": 123456,
            "admin": False,
            "company_type": "tutor_group"
        }
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_db_response

        #act
        response = self.dao.read_active_subscription_by_id(mock_subscription_id)

        #assert
        assert response.success is True
        assert isinstance(response.response, Subscription)
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    def test_read_active_subscription_no_records(self):
        #arrange
        mock_subscription_id = "db_id"
        mock_db_response = MagicMock()
        mock_db_response.exists = False
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_db_response

        #act
        response = self.dao.read_active_subscription_by_id(mock_subscription_id)

        #assert
        assert response.success is False
        assert response.message == "no_records_found_in_subscriptions"
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    def test_read_active_subscription_exception(self):
        #arrange
        mock_subscription_id = "db_id"
        mock_error = "error"
        self.mock_db.return_value.collection.return_value.document.return_value.get.side_effect = Exception(mock_error)

        #act
        response = self.dao.read_active_subscription_by_id(mock_subscription_id)

        #assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    #save stripe session id
    def test_save_stripe_session_id_success(self):
        #arrange
        mock_subscription_id = "db_id"
        mock_stripe_session_id = "stripe_id"
        mock_db_response = MagicMock()
        mock_db_response.update_time = 123456
        mock_db_response.to_dict.return_value = {
            "id": mock_subscription_id,
            "quantity": 1,
            "payment_random_id": "----",
            "stripe_subscription_id": "",
            "stripe_customer_id": "",
            "local_subscription_id": "",
            "local_user_id": "",
            "start_date": 123456,
            "renewal_date": 123456,
            "admin": False,
            "company_type": "tutor_group"
        }
        self.mock_db.return_value.collection.return_value.document.return_value.update.return_value = mock_db_response
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_db_response

        #act
        response = self.dao.save_stripe_session_id(mock_subscription_id, mock_stripe_session_id)

        #assert
        assert response.success is True
        assert isinstance(response.response, Subscription)
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once_with({
                "stripe_session_id": mock_stripe_session_id
            })
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()

    def test_save_stripe_session_id_exception(self):
        #arrange
        mock_error = "db_error"
        mock_subscription_id = "db_id"
        mock_stripe_session_id = "stripe_id"
        self.mock_db.return_value.collection.return_value.document.return_value.update.side_effect = Exception(mock_error)

        #act
        response = self.dao.save_stripe_session_id(mock_subscription_id, mock_stripe_session_id)

        #assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once()

    #activate subscription
    def test_activate_subscription_success(self):
        #arrange
        mock_subscription_id = ""
        mock_stripe_subscription_id = ""
        mock_stripe_subscription_item_id = ""
        mock_renewal_date = 1234

        mock_db_response = MagicMock()
        mock_db_response.update_time = 123456
        mock_db_response.to_dict.return_value = {
            "id": mock_subscription_id,
            "quantity": 1,
            "payment_random_id": "----",
            "stripe_subscription_id": "",
            "stripe_customer_id": "",
            "local_subscription_id": "",
            "local_user_id": "",
            "start_date": 123456,
            "renewal_date": 123456,
            "admin": False,
            "company_type": "tutor_group"
        }
        self.mock_db.return_value.collection.return_value.document.return_value.update.return_value = mock_db_response
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_db_response

        #act
        response = self.dao.activate_subscription(
            mock_subscription_id,
            mock_stripe_subscription_id,
            mock_stripe_subscription_item_id,
            mock_renewal_date
        )

        #assert
        assert response.success is True
        assert isinstance(response.response, Subscription)
        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once_with({
                "status": "active",
                "is_paid": True,
                "stripe_subscription_item_id": mock_stripe_subscription_item_id,
                "stripe_active_subscription_id": mock_stripe_subscription_id,
                "renewal_date": mock_renewal_date
            })

    def test_activate_subscription_exception(self):
        #arrange
        mock_subscription_id = ""
        mock_stripe_subscription_id = ""
        mock_stripe_subscription_item_id = ""
        mock_renewal_date = 1234
        mock_error = "db_error"

        self.mock_db.return_value.collection.return_value.document.return_value.update.side_effect = Exception(mock_error)

        #act
        response = self.dao.activate_subscription(
            mock_subscription_id,
            mock_stripe_subscription_id,
            mock_stripe_subscription_item_id,
            mock_renewal_date
        )

        #assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once()

    #expired payment
    def test_expired_payment_success(self):
        #arrange
        mock_subscription_id = "db_id"
        mock_db_response = MagicMock()
        mock_db_response.update_time = 123456
        mock_db_response.to_dict.return_value = {
            "id": mock_subscription_id,
            "quantity": 1,
            "payment_random_id": "----",
            "stripe_subscription_id": "",
            "stripe_customer_id": "",
            "local_subscription_id": "",
            "local_user_id": "",
            "start_date": 123456,
            "renewal_date": 123456,
            "admin": False,
            "company_type": "tutor_group"
        }

        self.mock_db.return_value.collection.return_value.document.return_value.update.return_value = mock_db_response
        self.mock_db.return_value.collection.return_value.document.return_value.get.return_value = mock_db_response

        #act
        response = self.dao.expired_payment(mock_subscription_id)

        #assert
        assert response.success is True
        assert isinstance(response.response, Subscription)

        self.mock_db.return_value.collection.return_value.document.return_value.get.assert_called_once()
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once_with({
                "status": "expired_payment"
            })

    def test_expired_payment_exception(self):
        #arrange
        mock_subscription_id = "db_id"
        mock_error = "db error"
        self.mock_db.return_value.collection.return_value.document.return_value.update.side_effect = Exception(mock_error)

        #act
        response = self.dao.expired_payment(mock_subscription_id)

        #assert
        assert response.success is False
        assert response.message == mock_error
        self.mock_db.return_value.collection.return_value.document.return_value.update.assert_called_once()

    #read subscription by payment random id
    def test_read_subscription_by_payment_random_id_success(self):
        #arrange
        mock_random_id = "12312312"
        mock_db_response = MagicMock()
        mock_db_response.to_dict.return_value = {
            "id": "",
            "quantity": 1,
            "payment_random_id": "----",
            "stripe_subscription_id": "",
            "stripe_customer_id": "",
            "local_subscription_id": "",
            "local_user_id": "",
            "start_date": 123456,
            "renewal_date": 123456,
            "admin": False,
            "company_type": "tutor_group"
        }
        self.mock_db.return_value.collection.return_value.where.return_value.stream.return_value = [mock_db_response]

        #act
        response = self.dao.read_subscription_by_payment_random_id(mock_random_id)

        #assert
        assert response.success is True
        assert isinstance(response.response, Subscription)
        assert isinstance(response.response_list[0], Subscription)
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called()

    def test_read_subscription_by_payment_random_id_no_records(self):
        #arrange
        mock_random_id = "12312312"
        self.mock_db.return_value.collection.return_value.where.return_value.stream.return_value = []

        #act
        response = self.dao.read_subscription_by_payment_random_id(mock_random_id)

        #assert
        assert response.success is False
        assert response.message == "no_records_found_in_subscriptions"
        self.mock_db.return_value.collection.return_value.where.return_value.stream.assert_called()

