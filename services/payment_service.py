from dao import UserDao, MembershipDao, SubscriptionsDao, CouponsDao
from services import StripeService
from entities import TutorUser, StudentUser, Membership, Response, Subscription, Coupon
from use_cases import IndividualUseCase, AdminUseCase
from typing import Union


class PaymentService():
    def __init__(self, local_user_id: str):
        self.local_user_id = local_user_id
        self.subscription_dao = SubscriptionsDao()
        self.membership_dao = MembershipDao()
        self.coupon_dao = CouponsDao()
        self.user_dao = UserDao()

    def buy_subscription(self, local_membership_id: str, local_coupon_id: str = "") -> Response:
        """
            Validates if the customer can buy the membership.
            If customer can buy it, send it to the use case
            Args:
                local_coupon_id:
                local_membership_id: the local id from a membership
            Returns:
                response: a response object with the result
                    response.success = True/False
                    response.message = informative/error message
                    response.result = a PaymentSession object with the result
        """
        response = Response()
        try:
            customer_response = self.user_dao.read_user_by_id(self.local_user_id)
            membership_response = self.membership_dao.read_membership_by_id(local_membership_id)

            coupon_response = None
            if (local_coupon_id != ""):
                coupon_response = self.coupon_dao.read_coupon_by_id(local_coupon_id)

            if (not customer_response.success):
                raise Exception(customer_response.message)

            if (not membership_response.success):
                raise Exception(membership_response.message)

            user_object = customer_response.response["user"]
            #user_type = customer_response.response["type"]

            user: Union[StudentUser, TutorUser] = user_object
            membership: Membership = membership_response.response

            if (user.Admin and membership.active_admin):
                use_case = AdminUseCase(user)
                if (coupon_response is not None and coupon_response.success):
                    coupon: Coupon = coupon_response.response
                    use_case.set_discount_coupon(coupon)

                response = use_case.create_subscription_payment_link(membership)
            elif (user.Type in membership.type_ and not membership.active_admin):
                if (user.Type.lower() == "individual" and user.CompanyCode.lower() != "individual"):
                    raise Exception("user_under_company_cannot_buy_memberships")

                use_case = IndividualUseCase(user)
                if (coupon_response is not None and coupon_response.success):
                    coupon: Coupon = coupon_response.response
                    use_case.set_discount_coupon(coupon)

                response = use_case.create_subscription_payment_link(membership)
            else:
                raise Exception("user_type_unable_to_buy_membership")

        except Exception as e:
            response.message = str(e)

        return response

    def update_active_subscription(self, quantity: int) -> Response:
        """
            Validates if the customer can read his membership.
            If customer can, redirect it to the use case
            Args:
                quantity: the amount of licences to add/remove
            Returns:
                response: a response object with the result
                    response.success = True/False
                    response.message = informative/error message
        """
        response = Response()

        try:
            customer_response = self.user_dao.read_user_by_id(self.local_user_id)

            if (not customer_response.success):
                raise Exception(customer_response.message)

            user_object = customer_response.response["user"]
            #user_type = customer_response.response["type"]

            user: Union[StudentUser, TutorUser] = user_object
            if (not user.Admin):
                raise Exception("invalid_company_type")

            subscription_response = self.subscription_dao.read_active_subscription_by_customer_id(user.id)

            if (not subscription_response.success):
                raise Exception(subscription_response.message)

            subscription: Subscription = subscription_response.response_list[0]
            response = AdminUseCase(user).update_subscription_quantity(subscription, quantity)

        except Exception as e:
            response.message = str(e)

        return response

    def read_active_subscription(self) -> Response:
        """
            Validates if the customer can read his membership.
            If customer can, redirect it to the use case
            Returns:
                response: a response object with the result
                    response.success = True/False
                    response.message = informative/error message
                    response.result = a subscription object with the subscription

        """
        response = Response()

        try:
            customer_response = self.user_dao.read_user_by_id(self.local_user_id)

            if (not customer_response.success):
                raise Exception(customer_response.message)

            user_object = customer_response.response["user"]
            #user_type = customer_response.response["type"]

            user: Union[StudentUser, TutorUser] = user_object
            if (user.Admin):
                response = AdminUseCase(user).read_active_subscription()
            elif (user.Type == "Individual"):
                response = IndividualUseCase(user).read_active_subscription()
            else:
                raise Exception("invalid_company_type")

        except Exception as e:
            response.message = str(e)

        return response

    def cancel_active_subscription(self) -> Response:
        """
            Validates if the customer can cancel his membership.
            If customer can, redirect it to the use case
            Returns:
                response: a response object with the result
                    response.success = True/False
                    response.message = informative/error message
        """
        response = Response()

        try:
            customer_response = self.user_dao.read_user_by_id(self.local_user_id)

            if (not customer_response.success):
                raise Exception(customer_response.message)

            user_object = customer_response.response["user"]
            #user_type = customer_response.response["type"]

            user: Union[StudentUser, TutorUser] = user_object

            if (user.Admin):
                response = AdminUseCase(user).cancel_subscription()
            else:
                response = IndividualUseCase(user).cancel_subscription()

        except Exception as e:
            response.message = str(e)

        return response

    def validate_payment(self, payment_random_id: str) -> Response:
        #TODO("must delete")
        subscription_response = self.subscription_dao.read_subscription_by_payment_random_id(payment_random_id)
        subscription: Subscription = subscription_response.response_list[0]
        return StripeService().validate_stripe_payment_session(subscription)
