from entities import Response, Membership, StudentUser, TutorUser, Subscription, Coupon
from services import StripeService
from dao import SubscriptionsDao
from typing import Union
from abc import abstractmethod


class BaseUseCase():
    def __init__(self, user: Union[StudentUser, TutorUser]):
        """
            Base class for all the payments use cases
            Args:
                user: the user object to work with
        """
        self.user = user
        self.stripe_service = StripeService()
        self.subscription_dao = SubscriptionsDao()
        self.active_coupon = None

    @abstractmethod
    def create_subscription_payment_link(self, membership: Membership, licences: int = 1) -> Response:
        """
            Create a subscription payment link for an individual customer subscribe to a membership
            Args:
                membership: a local membership object
                licences: the number of licences to buy
            Returns:
                response: a response object
        """

    @abstractmethod
    def update_subscription_quantity(self, subscription: Subscription, quantity: int) -> Response:
        """
            Updates a user subscription in stripe
            Args:
                subscription: the local subscription object to update
                quantity: the licences amount to add/delete if is positive to add if its negative to delete
            Returns:
                response: a response object
        """

    def cancel_subscription(self) -> Response:
        """
            Cancel an active subscription so stop the recurring payments
            Returns:
                response: a response object
        """
        response = Response()

        try:
            user = self.user

            # Look for the active subscription in the database
            active_subscription = self.subscription_dao.read_active_subscription_by_customer_id(user.id)
            if (not active_subscription.success):
                raise Exception("no_active_subscription")

            subscription: Subscription = active_subscription.response_list[0]

            # Unsubscribe in stripe to stop recurring payments
            stripe_unsubscribe_response = self.stripe_service.cancel_active_product_subscription(
                subscription.stripe_active_subscription_id
            )
            if (not stripe_unsubscribe_response.success):
                raise Exception(stripe_unsubscribe_response.message)

            # Mark subscription as canceled in the database
            response = self.subscription_dao.cancel_subscription_by_id(subscription.id)

        except Exception as e:
            response.message = str(e)

        return response

    def validate_subscription_payment(self, random_subscription_id: str) -> Response:
        """
            Validates a subscription payment
            Args:
                random_subscription_id: the random if of the subscription
        """
        response = Response()

        try:
            # Look for the active subscription in the database
            active_subscription = self.subscription_dao.read_subscription_by_payment_random_id(random_subscription_id)
            if (not active_subscription.success):
                raise Exception("no_active_subscription")

            subscription: Subscription = active_subscription.response_list[0]

            # Validate the payment in stripe
            response = self.stripe_service.validate_stripe_payment_session(subscription)

        except Exception as e:
            response.message = str(e)

        return response

    def read_active_subscription(self) -> Response:
        """
            Reads an active subscription from the database
            Returns:
                response: a response object
                    response.response: dict with the active subscription information
        """
        response = Response()

        try:
            subscription_response = self.subscription_dao.read_active_subscription_by_customer_id(self.user.id)
            if (not subscription_response.success):
                raise Exception(subscription_response.message)

            response.response = subscription_response.response_list[0]
            response.success = True if (len(subscription_response.response_list) > 0) else False
        except Exception as e:
            response.message = str(e)

        return response

    def set_discount_coupon(self, coupon: Coupon):
        """
            Adds a discount coupon
            Args:
                coupon: a local coupon object
        """
        self.active_coupon = coupon

