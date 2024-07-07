from entities import Response, Subscription, Membership, TutorUser, StudentUser
from repositories import FirestoreRepository
from datetime import datetime, timedelta
from secrets import token_hex
from typing import Union


class SubscriptionsDao():
    def __init__(self) -> None:
        self.collection = "subscriptions"
        self.repository = FirestoreRepository(self.collection)

    def create_subscription(self,
                            membership: Membership,
                            user: Union[StudentUser, TutorUser],
                            total_licences: int) -> Response:
        """
            Creates a new record in the database
            Args:
                membership: a local membership object
                user: a local user object
                total_licences: number of licences to buy
            Returns:
                response: a response Object
                    response.response (Subscription): a local subscription object
        """
        response = Response()

        try:
            random_transaction_validation_id = token_hex(16)

            new_active_subscription = Subscription(
                quantity=total_licences,
                payment_random_id=random_transaction_validation_id,
                local_user_id=user.id,
                local_subscription_id=membership.id,
                stripe_customer_id=user.stripe_customer_id,
                stripe_subscription_id=membership.stripe_id,
                start_date=int(datetime.now().timestamp()),
                renewal_date=int((datetime.now() + timedelta(days=30)).timestamp()),
                admin=user.Admin,
                company_type=user.company_type
            )

            response = self.repository.create_object(new_active_subscription.model_dump())

            if (response.success):
                response.response = Subscription.model_validate(response.response)

        except Exception as e:
            response.message = str(e)

        return response

    def update_subscription_by_id(self, subscription_id: str, quantity: int) -> Response:
        """
            Update the subscription quantity
            Args:
                subscription_id (str): a local subscription id
                quantity (int): the new total amount of licences
            Returns:
                response: a response object
        """
        response = Response()

        try:
            current_subscription_response = self.read_active_subscription_by_id(subscription_id)
            if (not current_subscription_response.success):
                raise Exception(current_subscription_response.message)

            current_subscription: Subscription = current_subscription_response.response
            prorate_data = current_subscription.prorate_data
            prorate_data.append({
                "before": current_subscription.quantity,
                "after": quantity
            })
            response = self.repository.update_object_by_id(subscription_id, {
                "quantity": quantity,
                "prorate_data": prorate_data
            })
        except Exception as e:
            response.message = str(e)

        return response

    def read_active_subscription_by_id(self, subscription_id: str) -> Response:
        """
            Reads an active subscription from a subscription id
            Args:
                subscription_id: a local subscription id
            Returns:
                response: a response object
                    response.response: a Subscription object
        """
        response = Response()

        try:
            subscription_response = self.repository.read_object_by_id(subscription_id)
            if (not subscription_response.success):
                raise Exception(subscription_response.message)

            response.success = True if (subscription_response.response != {}) else False
            if (response.success):
                response.response = Subscription.model_validate(subscription_response.response)

        except Exception as e:
            response.message = str(e)

        return response

    def save_stripe_session_id(self, subscription_id: str, stripe_session_id: str) -> Response:
        """
            Saves the stripe session id in an active_session
            Args:
                subscription_id(str): active subscription id
                stripe_session_id(str): stripe session id
            Returns:
                response: a response object
        """
        response = Response()

        try:
            response_update = self.repository.update_object_by_id(subscription_id, {
                "stripe_session_id": stripe_session_id
            })

            if (not response_update.success):
                raise Exception(response_update.message)

            response.response = Subscription.model_validate(response_update.response)
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def activate_subscription(self, subscription_id: str, stripe_subscription_id: str, stripe_subscription_item_id: str,
                              renewal_date: int) -> Response:
        """
            Marks the subscription as paid and saves the stripe subscription id and renewal date
            Args:
                subscription_id(str): a local subscription id
                stripe_subscription_id(str): a stripe subscription id
                stripe_subscription_item_id(str): a stripe active subscription id
                renewal_date(int): timestamp with the next payment date
            Returns:
                response: a response object
        """
        response = Response()

        try:
            response_update = self.repository.update_object_by_id(subscription_id, {
                "status": "active",
                "is_paid": True,
                "stripe_subscription_item_id": stripe_subscription_item_id,
                "stripe_active_subscription_id": stripe_subscription_id,
                "renewal_date": renewal_date
            })
            if (not response_update.success):
                raise Exception(response_update.message)

            response.response = Subscription.model_validate(response_update.response)
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def expired_payment(self, subscription_id: str) -> Response:
        """
            Marks a payment session as expired
            Args:
                subscription_id(str): active subscription id
            Returns:
                response: a response object
        """
        response = Response()

        try:
            response_update = self.repository.update_object_by_id(subscription_id, {
                "status": "expired_payment"
            })

            if (not response_update.success):
                raise Exception(response_update.message)

            response.response = Subscription.model_validate(response_update.response)
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_subscription_by_payment_random_id(self, payment_random_id: str) -> Response:
        """
            Reads a record from active_subscription with a payment_random_id
            Args:
                payment_random_id(str): a payment random id
            Returns:
                response: a response object
                    response.response_list: a list with Subscription objects
        """
        response = Response()

        try:
            response_read = self.repository.read_objects_with_equal(
                "payment_random_id",
                payment_random_id
            )

            if (not response_read.success):
                raise Exception(response_read.message)

            response.response_list = [Subscription.model_validate(item) for item in response_read.response_list]
            response.response = Subscription.model_validate(response_read.response_list[0])
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_active_subscription_by_customer_id(self, user_id: str) -> Response:
        """
            Reads an active subscription from a customer id
            Args:
                user_id(str): a local customer id
            Returns:
                response: a response object
                    response.response_list: a list with Subscription objects
        """
        response = Response()

        try:
            response = self.repository.read_objects_with_equal("local_user_id", user_id)
            response.response_list = [Subscription.model_validate(item) for item in response.response_list if
                                      item['status'] == "active"]
            response.success = True if (len(response.response_list) > 0) else False
            response.message = "" if (response.success) else "no_active_subscription"
        except Exception as e:
            response.message = str(e)

        return response

    def cancel_subscription_by_id(self, subscription_id: str) -> Response:
        """
            Marks the subscription as canceled
            Args:
                subscription_id (str): a local subscription id
            Returns:
                response: a response object
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(subscription_id, {
                "pending_cancel": True
            })
        except Exception as e:
            response.message = str(e)

        return response
