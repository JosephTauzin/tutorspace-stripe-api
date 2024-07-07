from use_cases import BaseUseCase
from entities import Response, Membership, StudentUser, TutorUser, PaymentSession, Subscription, Session, LineItems
from typing import Union
from services import CompanyService


class AdminUseCase(BaseUseCase):

    def __init__(self, user: Union[StudentUser, TutorUser]):
        super().__init__(user)
        self.company_service = CompanyService

    def create_subscription_payment_link(self, membership: Membership, licences: int = 1) -> Response:
        """
            Create a subscription payment link for an individual customer subscribe to a membership
            Args:
                membership: a local membership object
                licences: the number of licences to buy
            Returns:
                response: a response object
        """
        response = Response()

        try:
            user = self.user

            # Validates if customer has a stripe customer id
            if (user.stripe_customer_id == ""):
                stripe_customer_response = self.stripe_service.create_stripe_customer(user)

                if (not stripe_customer_response.success):
                    raise Exception(stripe_customer_response.message)

                user.stripe_customer_id = stripe_customer_response.response["stripe_customer_id"]

            # Check if there is an active subscription
            active_subscription = self.subscription_dao.read_active_subscription_by_customer_id(user.id)
            if (active_subscription.success):
                raise Exception("user_has_active_subscription")

            # Tally up users under the company code
            total_licences = licences
            company_service = self.company_service(user.CompanyCode)

            if (user.company_type == "individual_group"):
                total_individual_response = company_service.read_individuals()

                if (not total_individual_response.success):
                    raise Exception(total_individual_response.message)

                total_licences = total_individual_response.response["total"]

            elif (user.company_type == "tutor_group"):
                total_tutors_response = company_service.read_tutors()

                if (not total_tutors_response.success):
                    raise Exception(total_tutors_response.message)

                total_licences = total_licences + total_tutors_response.response["total"]
            else:
                raise Exception("invalid_company_type")

            if (total_licences == 0):
                raise Exception("invalid_licences_amount")

            # Creates a new subscription object in the database
            new_subscription = self.subscription_dao.create_subscription(membership, user, total_licences)

            if (not new_subscription.success):
                raise Exception(new_subscription.message)

            local_subscription: Subscription = new_subscription.response

            # Creates the stripe payment link
            discounts = [{
                "coupon": self.active_coupon.stripe_coupon_id
            }] if (self.active_coupon is not None) else []

            payment_session_response = self.stripe_service.create_stripe_payment_session(
                user,
                membership,
                local_subscription,
                total_licences,
                discounts
            )

            if (not payment_session_response.success):
                raise Exception(payment_session_response.message)

            stripe_payment_session = payment_session_response.response

            # Save the session id in the subscription record
            save_stripe_session_id_response = self.subscription_dao.save_stripe_session_id(
                local_subscription.id,
                stripe_payment_session["id"]
            )

            if (not save_stripe_session_id_response.success):
                raise Exception(save_stripe_session_id_response.message)

            response.response = PaymentSession(
                status=stripe_payment_session["status"],
                payment_url=stripe_payment_session["url"]
            ).model_dump()
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def update_subscription_quantity(self, subscription: Subscription, quantity: int) -> Response:
        """
            Updates a user subscription in stripe
            Args:
                subscription: the local subscription object to update
                quantity: the licences amount to add/delete if is positive to add if its negative to delete
            Returns:
                response: a response object
        """
        response = Response()

        try:
            current_licences = subscription.quantity
            new_total_licences = current_licences + quantity if (quantity > 0) else current_licences - abs(quantity)

            stripe_update_subscription_response = self.stripe_service.update_active_product_subscription(
                subscription,
                new_total_licences
            )

            if (not stripe_update_subscription_response.success):
                raise Exception(stripe_update_subscription_response.message)

            response = self.subscription_dao.update_subscription_by_id(subscription.id, new_total_licences)
            response.response = {}
        except Exception as e:
            response.message = str(e)

        return response

    def cancel_subscription(self) -> Response:
        """
            Cancel an active subscription so stop the recurring payments
            Returns:
                response: a response object
        """
        return super().cancel_subscription()

    def validate_subscription_payment(self, random_subscription_id: str) -> Response:
        """
            Validates a subscription payment
            Args:
                random_subscription_id: the random if of the subscription
        """
        return super().validate_subscription_payment(random_subscription_id)

    def read_active_subscription(self) -> Response:
        """
            Reads an active subscription from the database
            Returns:
                response: a response object
                    response.response: dict with the active subscription information
        """
        return super().read_active_subscription()
