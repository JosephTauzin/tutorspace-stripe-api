from entities import Response, TutorUser, StudentUser
from dao import UserDao, PayrollDao
from services import StripeService
from utils import dollars_to_cents


class CompanyService():
    def __init__(self, company_code: str):
        self.company_code = company_code
        self.user_dao = UserDao()
        self.payroll_dao = PayrollDao()
        self.stripe_service = StripeService()

    def read_tutors(self) -> Response:
        """
            Reads all the tutors under company code
            Returns:
                response: a response object
                    response.response: a dict with the total number of tutors
                        { "total": 10 }
                    response.response_list: a list of TutorUser objects
        """
        response = Response()

        try:
            tutors_response = self.user_dao.read_tutors_by_company_code(self.company_code)
            if (not tutors_response.success):
                raise Exception(tutors_response.message)

            response.response = {
                "total": len(tutors_response.response_list)
            }
            response.response_list = tutors_response.response_list
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_students(self) -> Response:
        """
            Reads all the students under company code
            Returns:
                response: a response object
                    response.response: a dict with the total number of students
                        { "total": 10 }
                    response.response_list: a list of StudentUser objects
        """
        response = Response()

        try:
            students_response = self.user_dao.read_students_by_company_code(self.company_code)
            if (not students_response.success):
                raise Exception(students_response.message)

            response.response = {
                "total": len(students_response.response_list)
            }
            response.response_list = students_response.response_list
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def read_individuals(self) -> Response:
        """
            Reads all the individuals under company code
            Returns:
                response: a response object
                    response.response: a dict with the total number of individuals
                        { "total": 10 }
                    response.response_list: a list of StudentUser objects
        """
        response = Response()

        try:
            individuals_response = self.user_dao.read_individuals_by_company_code(self.company_code)
            if (not individuals_response.success):
                raise Exception(individuals_response.message)

            response.response = {
                "total": len(individuals_response.response_list)
            }
            response.response_list = individuals_response.response_list
            response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def read_admin(self) -> Response:
        """
            Reads the admin under company code
            Returns:
                response: a response object
                    response.response: admin user object
        """
        response = Response()

        try:
            admin_response = self.user_dao.read_all_users_by_company_code(self.company_code)
            if (not admin_response.success):
                raise Exception(admin_response.message)

            response.response_list = [record for record in admin_response.response_list if (record["user"].Admin)]
            if (len(response.response_list) > 0):
                response.response = response.response_list[0]
                response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def set_company_type(self, company_type: str):
        """
            Updates the company type for all users under a company code
            Args:
                company_type:
            Returns:
        """
        response = Response()

        try:
            enabled_types = ["tutor_group", "individual_group"]
            if (not (company_type in enabled_types)):
                raise Exception("invalid_company_type")

            response = self.user_dao.set_company_type(self.company_code, company_type)
        except Exception as e:
            response.message = str(e)

        return response

    def read_tutor_by_name(self, tutor_name: str) -> Response:
        """
            Reads a tutor by a name
            Args:
                tutor_name: a string with the tutor's name
            Returns:
                response:
        """
        response = Response()

        try:
            tutor_response = self.user_dao.read_all_users_by_company_code(tutor_name)
            if (not tutor_response.success):
                raise Exception(tutor_response.message)

            if (tutor_response["type"] != "Tutor"):
                raise Exception("user_is_not_a_tutor")

            response.response = tutor_response["user"]
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def set_tutor_payment_configuration(self, tutor_id: str, pay_amount: int, price_amount: int) -> Response:
        """
            Set the tutor session price and pay amount
            Args:
                tutor_id: the tutor id to change the session price
                price_amount: the new price amount in dollars
                pay_amount: the new pay amount in dollars
            Returns:
        """
        response = Response()

        try:
            tutor_response = self.user_dao.read_user_by_id(tutor_id)
            if (not tutor_response.success):
                raise Exception(tutor_response.message)

            tutor: TutorUser = tutor_response.response["user"]

            if (tutor.Type != "Tutor"):
                raise Exception("user_is_not_tutor")

            if (tutor.CompanyCode != self.company_code):
                raise Exception("tutor_doesnt_belong_to_the_company")

            if (pay_amount > price_amount):
                raise Exception("pay_amount_cannot_be_higher_that_price_amount")

            response = self.user_dao.set_tutor_pay_configuration(
                tutor.id,
                dollars_to_cents(pay_amount),
                dollars_to_cents(price_amount)
            )
        except Exception as e:
            response.message = str(e)

        return response

    def set_tutor_session_price(self, tutor_id: str, price: int) -> Response:
        """
            Set the tutor session price in dollars
            Args:
                tutor_id: the tutor id to change the session price
                price: the new amount price in dollars
            Returns:
        """
        response = Response()

        try:
            tutor_response = self.user_dao.read_user_by_id(tutor_id)
            if (not tutor_response.success):
                raise Exception(tutor_response.message)

            tutor: TutorUser = tutor_response.response["user"]

            if (tutor.Type != "Tutor"):
                raise Exception("user_is_not_tutor")

            if (tutor.CompanyCode != self.company_code):
                raise Exception("tutor_doesnt_belong_to_the_company")

            response = self.user_dao.set_tutor_session_price(tutor_id, dollars_to_cents(price))
        except Exception as e:
            response.message = str(e)

        return response

    def set_tutor_pay_amount(self, tutor_id: str, amount: int) -> Response:
        """
            Set the tutor hour price in dollars
            Args:
                tutor_id: the tutor id to change the pay amount
                amount: the new amount price in dollars
            Returns:
        """
        response = Response()

        try:
            tutor_response = self.user_dao.read_user_by_id(tutor_id)
            if (not tutor_response.success):
                raise Exception(tutor_response.message)

            tutor: TutorUser = tutor_response.response["user"]

            if (tutor.Type != "Tutor"):
                raise Exception("user_is_not_tutor")

            if (tutor.CompanyCode != self.company_code):
                raise Exception("tutor_doesnt_belong_to_the_company")

            response = self.user_dao.set_tutor_hour_pay_amount(tutor_id, dollars_to_cents(amount))
        except Exception as e:
            response.message = str(e)

        return response

    def create_tutor_sub_account(self, tutor: TutorUser) -> Response:
        """
            Create a stripe sub account for a tutor
            Args:
                tutor: the tutor object to associate the sub account
            Returns:
                response
        """
        response = Response()

        try:
            if (tutor.Type != "Tutor"):
                raise Exception("user_is_not_a_tutor")

            new_sub_account_response = self.stripe_service.create_customer_sub_account(tutor)

            if (not new_sub_account_response.success):
                raise Exception(new_sub_account_response.message)

            response = new_sub_account_response
        except Exception as e:
            response.message = e

        return response

    def create_tutor_onboarding_link(self, tutor_id: str) -> Response:
        """
            Creates an onboarding link so a tutor can save his payout information
            Args:
                tutor_id: tutor id to create the payout information
            Returns:
                response
        """
        response = Response()

        try:
            tutor_user_response = self.user_dao.read_user_by_id(tutor_id)
            if (not tutor_user_response.success):
                raise Exception(tutor_user_response.message)

            if (tutor_user_response.response["type"] != "Tutor"):
                raise Exception("user_is_not_a_tutor")

            tutor: TutorUser = tutor_user_response.response["user"]

            if (tutor.CompanyCode != self.company_code):
                raise Exception("tutor_doesnt_belong_to_the_company")

            if (tutor.stripe_subaccount_id != ""):
                raise Exception("tutor_has_his_onboarding_already")

            if (tutor.stripe_subaccount_id == "" or tutor.stripe_subaccount_id is None):
                sub_account_response = self.create_tutor_sub_account(tutor)

                if (not sub_account_response.success):
                    raise Exception(sub_account_response.message)

                new_sub_account = sub_account_response.response
                self.user_dao.save_stripe_sub_account_id(tutor.id, new_sub_account["id"])
                tutor.stripe_subaccount_id = new_sub_account["id"]

            onboarding_link_response = self.stripe_service.create_sub_account_onboarding_link(
                tutor.stripe_subaccount_id)

            if (not onboarding_link_response.success):
                raise Exception(onboarding_link_response.message)

            response = onboarding_link_response
        except Exception as e:
            response.message = str(e)

        return response

    def create_student_onboarding_link(self, student_id: str) -> Response:
        """
            Create a stripe session to save a student payment information to charge customer later
            Args:
                student_id: student id
            Returns:
                response:
        """
        response = Response()

        try:
            student_user_response = self.user_dao.read_user_by_id(student_id)
            if (not student_user_response.success):
                raise Exception(student_user_response.message)

            if (student_user_response.response["type"] == "Tutor"):
                raise Exception("invalid_user_type")

            student: StudentUser = student_user_response.response["user"]

            if (student.CompanyCode != self.company_code):
                raise Exception("student_doesnt_belong_to_the_company")

            if (student.has_default_payment_method):
                raise Exception("student_has_his_onboarding_already")

            if (student.stripe_customer_id == ""):
                create_stripe_customer_response = self.stripe_service.create_stripe_customer(student)
                if (not create_stripe_customer_response.success):
                    raise Exception(create_stripe_customer_response.message)

                student.stripe_customer_id = create_stripe_customer_response.response["stripe_customer_id"]

            onboarding_link_response = self.stripe_service.create_payment_information_onboarding_link(student)

            if (not onboarding_link_response.success):
                raise Exception(onboarding_link_response.message)

            response = onboarding_link_response
        except Exception as e:
            response.message = str(e)

        return response

    def validate_student_onboarding(self, student_id: str) -> Response:
        """
            Validates a student onboarding by validating the payment method saved and marked it as
            the default payment method for the student
            Args:
                student_id: the student's id to validate
            Returns:
        """
        response = Response()

        try:
            student_user_response = self.user_dao.read_user_by_id(student_id)
            if (not student_user_response.success):
                raise Exception(student_user_response.message)

            if (student_user_response.response["type"] != "Student"):
                raise Exception("user_is_not_a_student")

            student: StudentUser = student_user_response.response["user"]

            response = self.stripe_service.activate_customer_payment_method(student)
        except Exception as e:
            response.message = str(e)

        return response

    def create_admin_onboarding_link(self):
        """
            Creates the admin onboarding link
            Returns:
                response
        """
        response = Response()

        try:
            admin_user_response = self.read_admin()
            if (not admin_user_response.success):
                raise Exception(admin_user_response.message)

            admin: TutorUser = admin_user_response.response["user"]

            if (admin.stripe_subaccount_id != ""):
                raise Exception("admin_has_his_onboarding_already")
            else:
                sub_account_response = self.stripe_service.create_customer_sub_account(admin)

                if (not sub_account_response.success):
                    raise Exception(sub_account_response.message)

                new_sub_account = sub_account_response.response

                self.user_dao.save_stripe_sub_account_id(admin.id, new_sub_account["id"])
                admin.stripe_subaccount_id = new_sub_account["id"]

            onboarding_link_response = self.stripe_service.create_sub_account_onboarding_link(
                admin.stripe_subaccount_id)

            if (not onboarding_link_response.success):
                raise Exception(onboarding_link_response.message)

            response = onboarding_link_response
        except Exception as e:
            response.message = str(e)

        return response
