import pytest
from pytest_mock import mocker
from unittest.mock import MagicMock
from interfaces import StripeInterface
from utils.utils import dollars_to_cents


class TestStripeInterface:

    @pytest.fixture(autouse=True)
    def setup_class(self, mocker):
        mocker.patch.dict("os.environ", {"STRIPE_API": "stripe_api"})

        self.mocker = mocker
        self.mock_response = MagicMock()
        self.stripe_instance = StripeInterface()

    #create_product
    def test_create_product_success(self):
        #arrange
        product_mock = self.mock_response
        product_mock.name = "Product Name"
        product_mock.description = "Description"
        product_mock.default_price_data.model_dump.return_value = {"currency": "USD", "unit_amount": 1000}

        stripe_response_mock = {"id": "prod_231", "object": "product"}
        stripe_mock = self.mocker.patch("stripe.Product.create", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.create_product(product_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock
        stripe_mock.assert_called_once_with(
            name="Product Name",
            description="Description",
            default_price_data={"currency": "USD", "unit_amount": 1000}
        )

    def test_create_product_exception(self):
        #arrange
        product_mock = self.mock_response
        product_mock.name = "Product Name"
        product_mock.description = "Description"
        product_mock.default_price_data.model_dump.return_value = {"currency": "USD", "unit_amount": 1000}
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Product.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_product(product_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(
            name="Product Name",
            description="Description",
            default_price_data={"currency": "USD", "unit_amount": 1000}
        )

    #create_customer
    def test_create_customer_success(self):
        #arrange
        customer_mock = self.mock_response
        customer_mock.name = "name"
        customer_mock.email = "mail@mail.com"

        stripe_response_mock = {"id": "prod_231", "object": "customer"}
        stripe_mock = self.mocker.patch("stripe.Customer.create", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.create_customer(customer_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock
        stripe_mock.assert_called_once_with(
            name="name",
            email="mail@mail.com"
        )

    def test_create_customer_exception(self):
        #arrange
        customer_mock = self.mock_response
        customer_mock.name = "name"
        customer_mock.email = "mail@mail.com"

        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Customer.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_customer(customer_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(
            name="name",
            email="mail@mail.com"
        )

    #update_customer_default_payment_method
    def test_update_customer_default_payment_method_success(self):
        #arrange
        customer_id_mock = "id_dsdsd"
        payment_method_id_mock = "pw_sdsds"

        stripe_response_mock = {"id": "id"}
        stripe_mock = self.mocker.patch("stripe.Customer.modify", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.update_customer_default_payment_method(customer_id_mock, payment_method_id_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock
        stripe_mock.assert_called_once_with(customer_id_mock, invoice_settings={
            "default_payment_method": payment_method_id_mock
        })

    def test_update_customer_default_payment_method_exception(self):
        #arrange
        customer_id_mock = "id_dsdsd"
        payment_method_id_mock = "pw_sdsds"

        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Customer.modify", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.update_customer_default_payment_method(customer_id_mock, payment_method_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(customer_id_mock, invoice_settings={
            "default_payment_method": payment_method_id_mock
        })

    #read_customer_by_id
    def test_read_customer_by_id_success(self):
        #arrange
        customer_id_mock = "id"
        stripe_response_mock = {"id": customer_id_mock}
        stripe_mock = self.mocker.patch("stripe.Customer.retrieve", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.read_customer_by_id(customer_id_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock
        stripe_mock.assert_called_once_with(customer_id_mock)

    def test_read_customer_by_id_exception(self):
        #arrange
        customer_id_mock = "id"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Customer.retrieve", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.read_customer_by_id(customer_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        assert response.response == {}
        stripe_mock.assert_called()

    #read_customer_by_email
    def test_read_customer_by_email_success(self):
        #arrange
        customer_email_mock = "example@mail.com"
        data_mock = [{"id": "id", "name": "example"}, {"id": "id2", "name": "example2"}]
        stripe_response_mock = {"data": data_mock}
        stripe_mock = self.mocker.patch("stripe.Customer.search", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.read_customer_by_email(customer_email_mock)

        #assert
        assert response.success is True
        assert response.response_list == data_mock
        stripe_mock.assert_called_once_with(query="email: '" + customer_email_mock + "'")

    def test_read_customer_by_email_no_records(self):
        #arrange
        error_message = "no_customer_found"
        customer_email_mock = "example@mail.com"
        stripe_response_mock = {"data": []}
        stripe_mock = self.mocker.patch("stripe.Customer.search", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.read_customer_by_email(customer_email_mock)

        #assert
        assert response.success is True
        assert response.message == error_message
        assert response.response_list == []
        stripe_mock.assert_called_once_with(query="email: '" + customer_email_mock + "'")

    def test_read_customer_by_email_exception(self):
        #arrange
        exception = "stripe error"
        customer_email_mock = "example@mail.com"
        stripe_mock = self.mocker.patch("stripe.Customer.search", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.read_customer_by_email(customer_email_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(query="email: '" + customer_email_mock + "'")

    #create_payment_session
    def test_create_payment_session_success(self):
        #arrange
        self.mocker.patch.dict("os.environ", {"BASE_URL": "http://www.example.com/"})

        payment_mock = self.mock_response
        payment_mock.client_reference_id = "client_id"
        payment_mock.customer = "customer_id"
        payment_mock.mode = "payment_mode"
        payment_mock.model_dump.return_value = {"line_items": []}

        callback_id_mock = "123456789"
        stripe_response_mock = {"id": "id", "url": "url"}
        stripe_mock = self.mocker.patch("stripe.checkout.Session.create", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.create_payment_session(payment_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock

        stripe_mock.assert_called_once_with(
            success_url="http://www.example.com/success.html",
            client_reference_id=payment_mock.client_reference_id,
            customer=payment_mock.customer,
            mode=payment_mock.mode,
            line_items=payment_mock.model_dump()["line_items"]
        )

    def test_create_payment_session_exception(self):
        #arrange
        self.mocker.patch.dict("os.environ", {"BASE_URL": "http://www.example.com/"})

        exception = "stripe error"
        payment_mock = self.mock_response
        payment_mock.client_reference_id = "client_id"
        payment_mock.customer = "customer_id"
        payment_mock.mode = "payment_mode"
        callback_id_mock = "123456789"

        stripe_mock = self.mocker.patch("stripe.checkout.Session.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_payment_session(payment_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(
            success_url="http://www.example.com/success.html",
            client_reference_id=payment_mock.client_reference_id,
            customer=payment_mock.customer,
            mode=payment_mock.mode,
            line_items=payment_mock.model_dump()["line_items"]
        )

    #create_payment_session_without_pay
    def test_create_payment_session_without_pay_success(self):
        #arrange
        self.mocker.patch.dict("os.environ", {"BASE_URL": "http://www.example.com/"})

        payment_mock = self.mock_response
        payment_mock.client_reference_id = "client_id"
        payment_mock.customer = "customer_id"
        payment_mock.mode = "payment_mode"
        payment_mock.payment_method_types = ["card", "bank"]

        stripe_response_mock = {"id": "id", "url": "url"}
        stripe_mock = self.mocker.patch("stripe.checkout.Session.create", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.create_payment_session_without_pay(payment_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock
        stripe_mock.assert_called_once_with(
            success_url="http://www.example.com/success.html",
            client_reference_id=payment_mock.client_reference_id,
            customer=payment_mock.customer,
            mode=payment_mock.mode,
            payment_method_types=payment_mock.payment_method_types
        )

    def test_create_payment_session_without_pay_exception(self):
        #arrange
        self.mocker.patch.dict("os.environ", {"BASE_URL": "http://www.example.com/"})

        exception = "stripe error"
        payment_mock = self.mock_response
        payment_mock.client_reference_id = "client_id"
        payment_mock.customer = "customer_id"
        payment_mock.mode = "payment_mode"
        payment_mock.payment_method_types = ["card", "bank"]

        stripe_mock = self.mocker.patch("stripe.checkout.Session.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_payment_session_without_pay(payment_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called()

    #read_payment_session_by_id
    def test_read_payment_session_by_id_success(self):
        #arrange
        session_id_mock = "session_id_sdsds"
        stripe_session_response = {"id": "id"}
        stripe_mock = self.mocker.patch("stripe.checkout.Session.retrieve", return_value=stripe_session_response)

        #act
        response = self.stripe_instance.read_payment_session_by_id(session_id_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_session_response
        stripe_mock.assert_called_once_with(session_id_mock)

    def test_read_payment_session_by_id_exception(self):
        #arrange
        exception = "stripe error"
        session_id_mock = "session_id"
        stripe_mock = self.mocker.patch("stripe.checkout.Session.retrieve", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.read_payment_session_by_id(session_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(session_id_mock)

    #read_subscriptions_by_customer
    def test_read_subscriptions_by_customer_success(self):
        #arrange
        customer_id_mock = "id"
        data_mock = [{"id": "sub_id1"}, {"id": "sub_id2"}]
        stripe_response_mock = {"id": customer_id_mock, "data": data_mock}
        stripe_mock = self.mocker.patch("stripe.Subscription.list", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.read_subscriptions_by_customer(customer_id_mock)

        #assert
        assert response.success is True
        assert response.response_list == data_mock
        stripe_mock.assert_called_once_with(customer=customer_id_mock)

    def test_read_subscription_by_customer_exception(self):
        #arrange
        customer_id_mock = "id"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Subscription.list", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.read_subscriptions_by_customer(customer_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(customer=customer_id_mock)

    #read_subscription_by_id
    def test_read_subscription_by_id_success(self):
        #arrange
        subscription_id_mock = "sub_id"
        stripe_response_mock = {"id": subscription_id_mock}
        stripe_mock = self.mocker.patch("stripe.Subscription.retrieve", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.read_subscription_by_id(subscription_id_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response_mock
        stripe_mock.assert_called_once_with(subscription_id_mock)

    def test_read_subscription_by_id_exception(self):
        #arrange
        subscription_id_mock = "sub_id"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Subscription.retrieve", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.read_subscription_by_id(subscription_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        assert response.response == {}
        stripe_mock.assert_called_once_with(subscription_id_mock)

    #unsusbcribe
    def test_unsubscribe_success(self):
        #arrange
        subscription_id_mock = "subs_id"
        stripe_response_mock = {"id": subscription_id_mock}
        stripe_mock = self.mocker.patch("stripe.Subscription.cancel", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.unsubscribe(subscription_id_mock)

        #assert
        assert response.success is True
        stripe_mock.assert_called_once_with(subscription_id_mock)

    def test_unsubscribe_exception(self):
        #arrange
        exception = "stripe error"
        subscription_id_mock = "sub_id"
        stripe_mock = self.mocker.patch("stripe.Subscription.cancel", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.unsubscribe(subscription_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(subscription_id_mock)

    #update_subscription
    def test_update_subscription_success(self):
        #arrange
        subscription_id_mock = "sub_id"
        subscription_item_id_mock = "subitem_id"
        new_quantity_mock = 3
        stripe_response_mock = {"id": subscription_id_mock}
        stripe_mock = self.mocker.patch("stripe.Subscription.modify", return_value=stripe_response_mock)

        #act
        response = self.stripe_instance.update_subscription_quantity(subscription_id_mock, subscription_item_id_mock,
                                                                     new_quantity_mock)

        #assert
        assert response.success is True
        stripe_mock.assert_called_once_with(
            subscription_id_mock,
            items=[
                {"id": subscription_item_id_mock, "quantity": new_quantity_mock}
            ]
        )

    def test_update_subscription_exception(self):
        #arrange
        subscription_id_mock = "sub_id"
        subscription_item_id_mock = "subitem_id"
        new_quantity_mock = 3
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Subscription.modify", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.update_subscription_quantity(subscription_id_mock, subscription_item_id_mock,
                                                                     new_quantity_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called()

    #read_setupintent
    def test_read_setupintent_success(self):
        #arrange
        setupintent_id_mock = "id"
        stripe_response = {"id": setupintent_id_mock}
        stripe_mock = self.mocker.patch("stripe.SetupIntent.retrieve", return_value=stripe_response)

        #act
        response = self.stripe_instance.read_setupintent(setupintent_id_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response
        stripe_mock.assert_called_once_with(setupintent_id_mock)

    def test_read_setupintent_exception(self):
        #arrange
        setupintent_id_mock = "id"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.SetupIntent.retrieve", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.read_setupintent(setupintent_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called_once_with(setupintent_id_mock)

    #create_sub_account
    def test_create_sub_account_success(self):
        #arrange
        subaccount_mock = self.mock_response
        subaccount_mock.email = "test@mail.com"
        subaccount_mock.country = "US"
        subaccount_mock.business_type = "individual"
        subaccount_mock.type = "tutor"
        stripe_response = {"id": "subaccount_id"}
        stripe_mock = self.mocker.patch("stripe.Account.create", return_value=stripe_response)

        #act
        response = self.stripe_instance.create_sub_account(subaccount_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response
        stripe_mock.assert_called_once_with(
            email=subaccount_mock.email,
            country=subaccount_mock.country,
            business_type=subaccount_mock.business_type,
            type=subaccount_mock.type
        )

    def test_create_sub_account_exception(self):
        #arrange
        subaccount_mock = self.mock_response
        subaccount_mock.email = "test@mail.com"
        subaccount_mock.country = "US"
        subaccount_mock.business_type = "individual"
        subaccount_mock.type = "tutor"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Account.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_sub_account(subaccount_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called()

    #create_subaccount_onboarding_link
    def test_create_subaccount_onboarding_link_success(self):
        #arrange
        self.mocker.patch.dict("os.environ", {"BASE_URL": "http://www.example.com/"})

        subaccount_id_mock = "acc_id"
        stripe_response = {"created": 123456}
        stripe_mock = self.mocker.patch("stripe.AccountLink.create", return_value=stripe_response)

        #act
        response = self.stripe_instance.create_subaccount_onboarding_link(subaccount_id_mock)

        #assert
        assert response.success is True
        assert response.response == stripe_response
        stripe_mock.assert_called_once_with(
            account=subaccount_id_mock,
            type="account_onboarding",
            refresh_url="http://www.example.com/",
            return_url="http://www.example.com/"
        )

    def test_create_subaccount_onboarding_link_exception(self):
        #arrange
        self.mocker.patch.dict("os.environ", {"BASE_URL": "http://www.example.com/"})
        subaccount_id_mock = "acc_id"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.AccountLink.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_subaccount_onboarding_link(subaccount_id_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called()

    #intern_transfer_to_subaccount
    def test_intern_transfer_to_subaccount_success(self):
        #arrange
        subaccount_id_mock = "acc_id"
        amount_mock = 5000
        currency_mock = "USD"
        stripe_response = {"id": "transfer_id"}
        stripe_mock = self.mocker.patch("stripe.Transfer.create", return_value=stripe_response)

        #act
        response = self.stripe_instance.intern_transfer_to_subaccount(subaccount_id_mock, amount_mock, currency_mock)

        #assert
        assert response.success is True
        stripe_mock.assert_called_once_with(
            amount=amount_mock,
            currency=currency_mock,
            destination=subaccount_id_mock
        )

    def test_intern_transfer_to_subaccount_exception(self):
        #arrange
        subaccount_id_mock = "acc_id"
        amount_mock = 5000
        currency_mock = "USD"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Transfer.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.intern_transfer_to_subaccount(subaccount_id_mock, amount_mock, currency_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called()

    #create_payout
    def test_create_payout_success(self):
        #arrange
        account_id_mock = "acc_id"
        amount_mock = 200
        currency_mock = "US"
        stripe_response = {"id": "payout_id"}
        stripe_mock = self.mocker.patch("stripe.Payout.create", return_value=stripe_response)

        #act
        response = self.stripe_instance.create_payout(account_id_mock, amount_mock, currency_mock)

        #assert
        assert response.success is True
        stripe_mock.assert_called_once_with(
            amount=amount_mock,
            currency=currency_mock,
            stripe_account=account_id_mock
        )

    def test_create_payout_exception(self):
        #arrange
        account_id_mock = "acc_id"
        amount_mock = 200
        currency_mock = "US"
        exception = "stripe error"
        stripe_mock = self.mocker.patch("stripe.Payout.create", side_effect=Exception(exception))

        #act
        response = self.stripe_instance.create_payout(account_id_mock, amount_mock, currency_mock)

        #assert
        assert response.success is False
        assert response.message == exception
        stripe_mock.assert_called()
