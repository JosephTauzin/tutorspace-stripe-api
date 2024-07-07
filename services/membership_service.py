from dao import MembershipDao, UserDao, SubscriptionsDao
from entities import TutorUser, StudentUser, Response
from typing import Union
from utils import cents_to_dollars


class MembershipService():
    def __init__(self, local_user_id: str):
        self.local_user_id = local_user_id
        self.subscription_dao = SubscriptionsDao()
        self.membership_dao = MembershipDao()
        self.user_dao = UserDao()

    def read_memberships(self) -> Response:
        """
            Reads the membership a user can buy
            Returns:
                response:
                    response.response_list: a list of membership objects
        """
        response = Response()

        try:
            user_response = self.user_dao.read_user_by_id(self.local_user_id)

            if (not user_response.success):
                raise Exception(user_response.message)

            user: Union[StudentUser, TutorUser] = user_response.response["user"]

            membership_response = self.membership_dao.read_enabled_user_memberships(user)

            if (not membership_response.success):
                raise Exception(membership_response.message)

            response.response_list = [
                membership.copy(update={"price": cents_to_dollars(membership.price)})
                for membership in membership_response.response_list
            ]
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_active_membership(self) -> Response:
        """
            Reads the membership the user bought
            Returns:
                response:
                    response.response_list: a list of subscription objects
        """
        response = Response()

        try:
            user_response = self.user_dao.read_user_by_id(self.local_user_id)

            if (not user_response.success):
                raise Exception(user_response.message)

            user: Union[StudentUser, TutorUser] = user_response.response["user"]
            subscription_response = self.subscription_dao.read_active_subscription_by_customer_id(user.id)

            if (not subscription_response.success):
                raise Exception(subscription_response.message)

            response.response_list = subscription_response.response_list
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response
