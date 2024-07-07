from repositories import FirestoreRepository
from entities import Response, TutorUser, StudentUser
from datetime import datetime


class UserDao():
    def __init__(self) -> None:
        self.collection = "users"
        self.repository = FirestoreRepository(self.collection)

    def read_user_by_id(self, user_id: str) -> Response:
        """
            Reads a local customer from the database.
            Args:
                user_id (str): a local user id
            Returns:
                response: a response object
                    response.response:
                    {
                        type: the user object type Student / Tutor
                        user: the user object
                    }
        """
        response = Response()

        try:
            response = self.repository.read_object_by_id(user_id)

            if (response.success):
                user_type = response.response['Type']
                parsed_user = StudentUser.model_validate(response.response) if (
                        user_type == "Student") else TutorUser.model_validate(response.response)

                response.response = {"type": user_type, "user": parsed_user}

        except Exception as e:
            response.message = str(e)

        return response

    def save_stripe_customer_id(self, user_id: str, stripe_customer_id: str) -> Response:
        """
            Inserts a new field in a customer record in the local database.
            Args:
                user_id (str): a local customer id
                stripe_customer_id (str): a stripe customer id
            Response:
                response: a response object
                    response.response: the new full customer object 
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(user_id, {
                "stripe_customer_id": stripe_customer_id
            })

        except Exception as e:
            response.message = str(e)

        return response

    def save_stripe_setup_intent_id(self, user_id: str, setup_intent_id: str) -> Response:
        """
            Saves the stripe setup intent id in the user record
            Args:
                user_id: a local customer id
                setup_intent_id: a stripe setup intent id
            Returns:
                response: a response object
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(user_id, {
                "setup_intent_id": setup_intent_id
            })
        except Exception as e:
            response.message = str(e)

        return response

    def set_has_default_payment_method(self, user_id: str, has_default_payment_method: bool) -> Response:
        """
            Set value of the field "has_default_payment_method" in the user record
            Args:
                user_id: a local user id
                has_default_payment_method: the value
            Returns:
                response: a response object
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(user_id, {
                "has_default_payment_method": has_default_payment_method
            })
        except Exception as e:
            response.message = str(e)

        return response

    def save_stripe_sub_account_id(self, user_id: str, stripe_sub_account_id: str) -> Response:
        """
            Saves a stripe sub account id for a user
            Args:
                user_id (str): a local customer id
                stripe_sub_account_id (str): a stripe sub account id
            Returns:
                response: a response object
                    response.response: the new full customer object
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(user_id, {
                "stripe_subaccount_id": stripe_sub_account_id
            })
        except Exception as e:
            response.message = str(e)

        return response

    def read_all_users_by_company_code(self, company_code: str) -> Response:
        """
            Reads all the users under a company code
            Args:
                company_code: the company code
            Returns:
                response: a response object
                    response.response_list: a list of dicts with all the users and theirs type (student, tutor)
                        {
                            "type": string, -> string with the type of user
                            "user": UserObject -> full user object
                        }
        """
        response = Response()

        try:
            response = self.repository.read_objects_with_equal("CompanyCode", company_code)

            response.response_list = [
                {
                    "type": record['Type'],
                    "user": TutorUser.model_validate(record)
                    if record['Type'] == "Tutor" else StudentUser.model_validate(record)
                }
                for record in response.response_list
            ]
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_tutors_by_company_code(self, company_code: str) -> Response:
        """
            Reads all the tutors under a company code
            Args:
                company_code: a company code
            Returns:
                response: a response object
                    response.response_list: a list of TutorUser objects
        """
        response = Response()

        try:
            users_in_company = self.read_all_users_by_company_code(company_code)

            if (users_in_company.success):
                response.response_list = [
                    record["user"]
                    for record in users_in_company.response_list if
                    (record["type"] == "Tutor")
                ]
                response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_students_by_company_code(self, company_code: str) -> Response:
        """
            Reads all the students under a company code
            Args:
                company_code: a company code
            Returns:
                response: a response object
                    response.response_list: a list of StudentUser objects
        """
        response = Response()

        try:
            users_in_company = self.read_all_users_by_company_code(company_code)

            if (users_in_company.success):
                response.response_list = [
                    record["user"]
                    for record in users_in_company.response_list if
                    (record["type"] == "Student" and not record["user"].Admin)
                ]
                response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def read_individuals_by_company_code(self, company_code: str) -> Response:
        """
            Reads all the individuals under a company code
            Args:
                company_code: a company code
            Returns:
                response: a response object
                    response.response_list: a list of StudentUser objects
        """
        response = Response()

        try:
            users_in_company = self.read_all_users_by_company_code(company_code)

            if (users_in_company.success):
                response.response_list = [
                    record["user"]
                    for record in users_in_company.response_list if
                    (record["type"] == "Individual" and not record["user"].Admin)
                ]
                response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def set_company_type(self, company_code: str, company_type: str) -> Response:
        """
            Sets the company_type for all the users under a company code
            Args:
                company_code: the company code for the users to update
                company_type: the new company type for all the users
            Returns:
                response: a response object with the result
        """
        response = Response()

        try:
            response = self.repository.massive_update_with_equal(
                "CompanyCode",
                company_code,
                "company_type",
                company_type
            )
        except Exception as e:
            response.message = str(e)

        return response

    def set_tutor_session_price(self, tutor_id: str, price: int) -> Response:
        """
            Updates the tutor cost_per_session
            Args:
                tutor_id: the tutor id to update the cost per session
                price: the new price amount in dollars
            Returns:
                response:
                    response: True/False
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(
                tutor_id,
                {
                    "cost_per_session": price
                }
            )
        except Exception as e:
            response.message = str(e)

        return response

    def set_tutor_hour_pay_amount(self, tutor_id: str, amount: int) -> Response:
        """
            Updates the tutor pay_per_hour field
            Args:
                tutor_id: the tutor id to update the cost per hour
                amount: the new price amount in dollars
            Returns:
                response:
                    response: True/False
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(
                tutor_id,
                {
                    "pay_per_hour": amount
                }
            )
        except Exception as e:
            response.message = str(e)

        return response

    def read_user_by_name(self, user_name: str) -> Response:
        """
            Reads a local user from the database by a name.
            Args:
                user_name (str): a local username
            Returns:
                response: a response object
                    response.response:
                    {
                        type: the user object type Student / Tutor
                        user: the user object
                    }
        """
        response = Response()

        try:
            users_response = self.repository.read_objects_with_equal("name", user_name)

            if (not response.success):
                raise Exception(response.response)

            response.response_list = [
                record
                for record in users_response.response_list if (not record.Admin)
            ]
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def update_admin_last_payroll_date(self, admin_id: str) -> Response:
        """
            Updates the date of the last payroll
            Args:
                admin_id:
            Returns:
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(
                admin_id,
                {
                    "last_payout_date": datetime.today()
                }
            )
        except Exception as e:
            response.message = str(e)

        return response

    def set_tutor_pay_configuration(self, tutor_id: str, pay_amount: int, price_amount: int) -> Response:
        """
            Updates the tutor cost_per_session
            Args:
                tutor_id: the tutor id to update the cost per session
                price_amount: the new price amount in cents
                pay_amount:  the new pay amount in cents
            Returns:
                response:
                    response: True/False
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(
                tutor_id,
                {
                    "cost_per_session": price_amount,
                    "pay_per_hour": pay_amount
                }
            )
        except Exception as e:
            response.message = str(e)

        return response

    def save_coupon_applied(self, user_id: str, coupon_id: str) -> Response:
        """
            Saves an applied coupon record to a user
            Args:
                user_id:
                coupon_id:
            Returns:
        """
        response = Response()

        try:
            user_response = self.read_user_by_id(user_id)
            if (not user_response.success):
                raise Exception(user_response.message)

            user: TutorUser = user_response.response["user"]
            previous_coupons = user.subscription_coupons_applied
            previous_coupons.append({
                "coupon_id": coupon_id,
                "date": datetime.now()
            })

            update_response = self.repository.update_object_by_id(user_id, {
                    "subscription_coupons_applied": previous_coupons
                }
            )

            if (not update_response.success):
                raise Exception(update_response.message)

            response.success = True
        except Exception as e:
            response.message = e

        return response

    def save_pending_invoice_coupon(self, user_id, coupon_id: str) -> Response:
        """
            Saves a coupon to be applied in the next invoice
            Args:
                user_id: a local user id
                coupon_id: a stripe coupon id
            Returns:
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(user_id, {
                "has_pending_discount_coupon": True,
                "pending_discount_coupon": coupon_id
            })
        except Exception as e:
            response.message = e

        return response

    def remove_applied_invoice_coupon(self, user_id: str) -> Response:
        """
            Removes from the db a coupon that was use in an invoice
            Args:
                user_id: a local user id
            Returns:
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(user_id, {
                "has_pending_discount_coupon": False,
                "pending_discount_coupon": ""
            })
        except Exception as e:
            response.message = e

        return response
