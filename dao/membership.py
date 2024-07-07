from repositories import FirestoreRepository
from interfaces import StripeInterface
from entities import Response, Membership, Product, PriceData, Recurring, StudentUser, TutorUser
from typing import Union


class MembershipDao():
    def __init__(self) -> None:
        self.collection = "memberships"
        self.stripe = StripeInterface()
        self.repository = FirestoreRepository(self.collection)

    def create_membership(self, membership: Membership) -> Response:
        """
            Creates a product in stripe then a membership in the database and associate it
            Args:
                membership: a membership object
            Returns:
                response: a response object
                   response.response: a Membership object
        """
        response = Response()

        try:
            stripe_product = Product(
                name=membership.name,
                description=membership.description,
                default_price_data=PriceData(
                    currency=membership.currency,
                    unit_amount=membership.price,  # Stripe needs the amount in cents
                    recurring=Recurring(
                        interval=membership.interval,
                        interval_count=membership.interval_count
                    )
                )
            )

            # creates a product in stripe
            stripe_create_response = self.stripe.create_product(stripe_product)

            if (not stripe_create_response.success):
                raise Exception(stripe_create_response.message)

            membership.stripe_id = stripe_create_response.response["id"]
            membership.stripe_price_id = stripe_create_response.response["default_price"]

            # insert the new product in the database
            insert_response = self.repository.create_object(
                membership.model_dump())

            if (not insert_response.success):
                raise Exception("unable_to_create_database_membership_record")

            response.success = True
            response.response = Membership.model_validate(insert_response.response)

        except Exception as e:
            response.message = str(e)

        return response

    def read_memberships(self) -> Response:
        """
            Reads all the memberships records from the database
            Returns:
                response: a response object
                    response.response_list = a list of Membership objects
        """
        response = Response()

        try:
            response = self.repository.read_collection()
            if (not response.success):
                raise Exception(response.message)

            response.response_list = [Membership.model_validate(item) for item in response.response_list]
        except Exception as e:
            response.message = str(e)

        return response

    def read_membership_by_id(self, membership_id: str) -> Response:
        """
            Reads a membership record from the database with an id
            Args:
                membership_id(str): a local membership id
            Returns:
                response: a response object
                    response.response: a Membership object
        """
        response = Response()

        try:
            response = self.repository.read_object_by_id(membership_id)

            if (not response.success):
                raise Exception(response.message)

            response.response = Membership.model_validate(response.response)

        except Exception as e:
            response.message = str(e)

        return response

    def read_enabled_user_memberships(self, user: Union[StudentUser, TutorUser]) -> Response:
        """
            Reads all the memberships enabled to be bought for a user
            Args:
                user: the user object
            Returns:
                response: a response object
                    response.response_list: a list of the enabled memberships objects
        """
        response = Response()

        try:
            if (user.Admin):
                response = self.repository.read_objects_with_equal("active_admin", True)
            else:
                response = self.repository.read_objects_with_equal("type_", user.Type)

            if (not response.success):
                raise Exception(response.message)

            response.response_list = [
                Membership.model_validate(item)
                for item in response.response_list
            ]
        except Exception as e:
            response.message = str(e)

        return response
