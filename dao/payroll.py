from repositories import FirestoreRepository
from entities import Payroll, Response, StudentDebt, TutorPayout, AdminPayout


class PayrollDao():
    def __init__(self):
        self.collection = "payroll"
        self.repository = FirestoreRepository(self.collection)

    def create_payroll(self, payroll: Payroll) -> Response:
        """
            Creates a new payroll summary to be paid later
            Args:
                payroll: the full payroll object
            Returns:
                response
        """
        response = Response()

        try:
            create_response = self.repository.create_object(payroll.model_dump())

            if (create_response.success):
                response.response = Payroll.model_validate(create_response.response)
                response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def read_payroll_by_id(self, payroll_id: str) -> Response:
        """
            Reads a payroll by id
            Args:
                payroll_id: the payroll id to look for
            Returns:
                response:
        """
        response = Response()

        try:
            response = self.repository.read_object_by_id(payroll_id)
            if (response.success):
                response.response = Payroll.model_validate(response.response)

        except Exception as e:
            response.message = str(e)

        return response

    def read_payroll_by_company_code(self, company_code: str) -> Response:
        """
            Reads payrolls with a company code
            Args:
                company_code: the company code
            Returns:
                response:
        """

        response = Response()

        try:
            response = self.repository.read_objects_with_equal("company_code", company_code)
            if (response.success):
                response.response_list = [
                    Payroll.model_validate(payroll)
                    for payroll in response.response_list
                ]

        except Exception as e:
            response.message = str(e)

        return response

    def update_payroll_student_debt(self, payroll_id: str, students_debt: list) -> Response:
        """
            Sets a new student debt array for a payroll
            Args:
                payroll_id: the payroll id
                students_debt: the new student debt list
            Returns:
                response:
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "students_debt": [
                    StudentDebt.model_validate(student_debt).model_dump()
                    for student_debt in students_debt
                ]
            })
        except Exception as e:
            response.message = str(e)

        return response

    def update_payroll_tutors_payout(self, payroll_id: str, tutors_payout: list) -> Response:
        """
            Sets a new tutors payout array for a payroll
            Args:
                payroll_id:
                tutors_payout:
            Returns:
                response
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "tutors_payout": [
                    TutorPayout.model_validate(payout).model_dump()
                    for payout in tutors_payout
                ]
            })
        except Exception as e:
            response.message = str(e)

        return response

    def mark_payroll_charged(self, payroll_id: str) -> Response:
        """
            Marks a payroll as charged, it means we already charge all the students in the payroll
            Args:
                payroll_id:
            Returns:
                response
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "charged": True
            })
        except Exception as e:
            response.message = str(e)

        return response

    def mark_payroll_completed(self, payroll_id: str) -> Response:
        """
            Marks a payroll as completed, it means we already charge all the students in the payroll also
            we paid to all the tutors
            Args:
                payroll_id:
            Returns:
                response:
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "completed": True
            })
        except Exception as e:
            response.message = str(e)

        return response

    def read_not_paid_payroll_by_company_code(self, company_code: str) -> Response:
        """
            Reads all not completely paid payroll for a company code
            Args:
                company_code:
            Returns:
                response:
        """
        response = Response()

        try:
            payroll_response = self.repository.read_objects_with_equal("completed", False)
            if (not payroll_response.success):
                raise Exception(payroll_response.message)

            response.response_list = [
                Payroll.model_validate(payroll)
                for payroll in payroll_response.response_list if payroll["company_code"] == company_code
            ]
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def update_payroll_by_id(self, payroll_id: str, payroll: Payroll) -> Response:
        """
            Updates a complete payroll
            Args:
                payroll_id:
                payroll:
            Returns:
        """
        response = Response()

        try:
            del payroll.id
            response = self.repository.update_object_by_id(payroll_id, payroll.model_dump())
        except Exception as e:
            response.message = str(e)

        return response

    def update_payroll_admin_payout(self, payroll_id: str, admin_payout: AdminPayout) -> Response:
        """
            Sets a new admin payout object for a payroll
            Args:
                admin_payout:
                payroll_id:
            Returns:
                response
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "admin_payout": admin_payout.model_dump()
            })
        except Exception as e:
            response.message = str(e)

        return response

    def set_payroll_student_debt_charged(self, payroll_id: str) -> Response:
        """
            Marks the payroll flag "students_charged" as True.
            It means we already charge all the students in the payroll
            Args:
                payroll_id:
            Returns:
                response
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "students_charged": True
            })
        except Exception as e:
            response.message = str(e)

        return response

    def set_payroll_tutors_payout_paid(self, payroll_id: str) -> Response:
        """
            Marks the payroll flag "tutors_paid" as True.
            It means we already paid all the tutors in the payroll
            Args:
                payroll_id:
            Returns:
                response
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "tutors_paid": True
            })
        except Exception as e:
            response.message = str(e)

        return response

    def set_payroll_admin_payout_paid(self, payroll_id: str) -> Response:
        """
            Marks the payroll flag "admin_paid" as True.
            It means we already paid the admin in the payroll
            Args:
                payroll_id:
            Returns:
                response
        """
        response = Response()

        try:
            response = self.repository.update_object_by_id(payroll_id, {
                "admin_paid": True
            })
        except Exception as e:
            response.message = str(e)

        return response
