from entities import Response, TutorUser, StudentUser, StudentDebt, TutorPayout, TutorNotFound, Payroll, AdminPayout, \
    Subscription
from dao import UserDao, PayrollDao
from services import CompanyService, StripeService, MembershipService
from datetime import datetime, timezone
from utils import calculate_hours_spent, calculate_hours_spent_by_range, find_student_debt_by_student_id, \
    find_tutor_pay_by_tutor_id, check_duplicated_tutor_hours


class PayrollService():

    def __init__(self):
        self.user_dao = UserDao()
        self.payroll_dao = PayrollDao()
        self.stripe_service = StripeService()
        self.company_service = CompanyService
        self.membership_service = MembershipService

    def prepare_payroll(self, company_code: str) -> Response:
        """
            Validate if company code can create a payroll
            Args:
                company_code:
            Returns:
        """
        response = Response()

        try:
            #check the admin
            admin_response = self.company_service(company_code).read_admin()
            if (not admin_response.success):
                raise Exception(admin_response.message)

            admin: TutorUser = admin_response.response["user"]

            #check active subscription
            admin_active_subscription = self.membership_service(admin.id).read_active_membership()
            if (not admin_active_subscription.success):
                raise Exception(admin_active_subscription.message)

            subscription: Subscription = admin_active_subscription.response_list[0]
            if (subscription.status != "active"):
                raise Exception("no_active_subscription")

            #check company type
            if (admin.company_type == "tutor_group"):
                students = self.company_service(company_code).read_students()
                if (not students.response):
                    raise Exception(students.message)

                calculate_payroll_payments = self.calculate_payroll_payments(admin, students.response_list)
                if (not calculate_payroll_payments.success):
                    raise Exception(calculate_payroll_payments.message)

                response = self.validate_payroll_payments(admin, calculate_payroll_payments.response)
            elif (admin.company_type == "individual_group"):
                individuals = self.company_service(company_code).read_individuals()
                if (not individuals.response):
                    raise Exception(individuals.message)

                calculate_payroll_payments = self.calculate_payroll_payments(admin, individuals.response_list)
                if (not calculate_payroll_payments.success):
                    raise Exception(calculate_payroll_payments.message)

                response = self.validate_payroll_payments(admin, calculate_payroll_payments.response)
            else:
                raise Exception("invalid_company_type")

        except Exception as e:
            response.message = str(e)

        return response

    def calculate_payroll_payments(self, admin: TutorUser, users: list) -> Response:
        """
            Calculates the students debt, the tutors pay and the admin profit
            Args:
                admin:
                users:
            Returns:
        """
        response = Response()

        try:
            #data to calculate
            students_to_charge = []
            tutors_payout = []
            tutors_not_found = []
            total_admin_profit = 0

            #check the payout date range
            first_payout = False

            last_payout_date = admin.last_payout_date
            today_date = datetime.now(timezone.utc)

            if (last_payout_date is None):
                first_payout = True

            #reads all the tutors to check their cost
            tutors_response = self.company_service(admin.CompanyCode).read_tutors()
            if (not tutors_response.success):
                raise Exception(tutors_response.message)

            # parsed the tutors into a big dict, so it's easy to look for them
            tutors_parsed = {tutor.name: tutor for tutor in tutors_response.response_list}

            #read the users
            for user in users:
                student: StudentUser = user
                student_tutor: TutorUser = tutors_parsed.get(student.Tutor)

                student_meeting_time_start = student.HistMeetingTimes
                student_meeting_time_end = student.HistMeetingTimesEnd

                if (len(student_meeting_time_start) > 0 and len(student_meeting_time_end) > 0):
                    student_hours = calculate_hours_spent(
                        student_meeting_time_start,
                        student_meeting_time_end
                    ) if (first_payout) else calculate_hours_spent_by_range(
                        student_meeting_time_start,
                        student_meeting_time_end,
                        last_payout_date,
                        today_date
                    )

                    #check if the tutor exist
                    if (student_tutor is None):
                        tutors_not_found.append({
                            "tutor_name": student.Tutor,
                            "students": {
                                "name": student.name,
                                "hours": student_hours
                            }
                        })
                        continue

                    #student debt
                    student_debt = student_hours * student_tutor.cost_per_session

                    #tutor payment
                    tutor_pay = student_hours * student_tutor.pay_per_hour

                    #admin profit percentage
                    admin_profit_percentage = (abs(student_tutor.cost_per_session - student_tutor.pay_per_hour) / (
                            (student_tutor.cost_per_session + student_tutor.pay_per_hour) / 2)) * 100
                    #admin profit in cents
                    admin_profit_amount = int((admin_profit_percentage / 100) * student_debt)

                    #total admin profit
                    total_admin_profit = total_admin_profit + admin_profit_amount

                    student_debt_object = StudentDebt(
                        start_hours=student_meeting_time_start,
                        end_hours=student_meeting_time_end,
                        hours=student_hours,
                        student_id=student.id,
                        student_name=student.name,
                        student_debt=student_debt,
                        tutor_id=student_tutor.id,
                        tutor_name=student_tutor.name,
                        tutor_cost=student_tutor.cost_per_session,
                        pending_onboarding=(not student.has_default_payment_method),
                        stripe_customer_id=student.stripe_customer_id,
                        admin_profit=admin_profit_amount
                    )
                    students_to_charge.append(student_debt_object)

                    student_tutor_pending_onboarding = True if (student_tutor.stripe_subaccount_id == "") else False
                    tutor_payout_object = TutorPayout(
                        tutor_id=student_tutor.id,
                        tutor_name=student_tutor.name,
                        tutor_payout=tutor_pay,
                        tutor_total_hours=student_hours,
                        pending_onboarding=student_tutor_pending_onboarding,
                        stripe_sub_account_id=student_tutor.stripe_subaccount_id
                    )
                    tutors_payout.append(tutor_payout_object)

            admin_pending_onboarding = True if (admin.stripe_subaccount_id == "") else False
            admin_payout = AdminPayout(
                admin_total_profit=total_admin_profit,
                admin_sub_account_id=admin.stripe_subaccount_id,
                pending_onboarding=admin_pending_onboarding
            )

            tutors_payout = check_duplicated_tutor_hours(tutors_payout)

            response.response = {
                "students_to_charge": students_to_charge,
                "tutors_payout": tutors_payout,
                "admin_payout": admin_payout,
                "tutors_not_found": tutors_not_found
            }
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def validate_payroll_payments(self, admin: TutorUser, payroll_data: dict) -> Response:
        """
            Validate if students are already charged, tutors already paid an
            Args:
                admin:
                payroll_data: {
                        "students_to_charge": students_to_charge,
                        "tutors_payout": tutors_payout,
                        "admin_payout": admin_payout,
                        "tutors_not_found": tutors_not_found
                    }
            Returns:
        """
        response = Response()

        try:
            tutors_not_found = []

            current_payroll = self.payroll_dao.read_not_paid_payroll_by_company_code(admin.CompanyCode)
            previous_payroll: Payroll = current_payroll.response_list[0] \
                if (current_payroll.success and len(current_payroll.response_list) > 0) else None

            payroll: Payroll
            if (previous_payroll is not None):
                admin_payout = payroll_data["admin_payout"] \
                    if (not previous_payroll.admin_paid) else previous_payroll.admin_payout

                if (not previous_payroll.students_charged):
                    students_to_charge = [
                        find_student_debt_by_student_id(payroll_data["students_to_charge"], student_debt.student_id)
                        if (not student_debt.paid) else student_debt for student_debt in previous_payroll.students_debt
                    ]
                else:
                    students_to_charge = previous_payroll.students_debt

                if (not previous_payroll.tutors_paid):
                    tutors_payout = [
                        find_tutor_pay_by_tutor_id(payroll_data["tutors_payout"], tutor_payout.tutor_id)
                        if (not tutor_payout.paid) else tutor_payout for tutor_payout in previous_payroll.tutors_payout
                    ]
                else:
                    tutors_payout = previous_payroll.tutors_payout

                payroll = Payroll(
                    company_code=previous_payroll.company_code,
                    admin_id=previous_payroll.admin_id,
                    students_charged=previous_payroll.students_charged,
                    tutors_paid=previous_payroll.tutors_paid,
                    admin_paid=previous_payroll.admin_paid,
                    admin_payout=admin_payout,
                    students_debt=students_to_charge,
                    tutors_payout=tutors_payout,
                    tutors_not_found=tutors_not_found,
                )
            else:
                payroll = Payroll(
                    company_code=admin.CompanyCode,
                    admin_id=admin.id,
                    students_debt=payroll_data["students_to_charge"],
                    tutors_payout=payroll_data["tutors_payout"],
                    tutors_not_found=payroll_data["tutors_not_found"],
                    admin_payout=payroll_data["admin_payout"]
                )

            insert_response = self.payroll_dao.update_payroll_by_id(previous_payroll.id, payroll) \
                if (previous_payroll is not None) else self.payroll_dao.create_payroll(payroll)

            if (not insert_response.success):
                raise Exception(insert_response.message)

            response.response = insert_response.response
            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def create_company_payroll(self, company_code: str) -> Response:
        """
            Tally up students, calculate hours, cross hours with tutors fee, charge students, payout to tutors
            Returns:
        """
        response = Response()

        try:
            #validate if there is a pending payroll
            current_payroll = self.payroll_dao.read_not_paid_payroll_by_company_code(company_code)
            previous_payroll = None

            if (current_payroll.success and len(current_payroll.response_list) > 0):
                previous_payroll = current_payroll.response_list[0]

            #read admin user
            company_admin_response = self.company_service(company_code).read_admin()
            if (not company_admin_response.success):
                raise Exception(company_admin_response.message)

            admin: TutorUser = company_admin_response.response["user"]

            #tally up all the students in the company
            if (admin.company_type == "tutor_group"):
                users_response = self.company_service(company_code).read_students()
                if (not users_response.success):
                    raise Exception(users_response.message)
            elif (admin.company_type == "individual_group"):
                users_response = self.company_service(company_code).read_individuals()
                if (not users_response.success):
                    raise Exception(users_response.message)
            else:
                raise Exception("invalid_company_type")

            students = users_response.response_list

            #calculate debt by student
            students_to_charge = []
            tutors_not_found = {}
            tutors_payout = {}
            with_error = []
            total_admin_profit = 0

            #read the admin information to see last payout date
            first_payout = False

            last_payout_date = admin.last_payout_date
            today_date = datetime.now()

            if (last_payout_date is None):
                first_payout = True

            #reads all the tutors to check their cost
            tutors_response = self.company_service(company_code).read_tutors()
            if (not tutors_response.success):
                raise Exception(tutors_response.message)

            tutors_parsed = {tutor.name: tutor for tutor in tutors_response.response_list}

            for (i, student) in enumerate(students):
                student: StudentUser = student

                student_meeting_time_start = student.HistMeetingTimes
                student_meeting_time_end = student.HistMeetingTimesEnd

                if (len(student_meeting_time_start) > 0 and len(student_meeting_time_end) > 0):
                    student_hours = calculate_hours_spent(
                        student_meeting_time_start,
                        student_meeting_time_end
                    ) if (first_payout) else calculate_hours_spent_by_range(
                        student_meeting_time_start,
                        student_meeting_time_end,
                        last_payout_date,
                        today_date
                    )

                    student_tutor = tutors_parsed.get(student.Tutor)
                    if (student_tutor is None):
                        if (student.Tutor in tutors_not_found):
                            tutors_not_found.get(student.Tutor)["students"].append({
                                "name": student.name,
                                "hours": student_hours
                            })
                        else:
                            tutors_not_found[student.Tutor] = {
                                "tutor_name": student.Tutor,
                                "students": [{
                                    "name": student.name,
                                    "hours": student_hours
                                }]
                            }
                        continue

                    student_tutor: TutorUser = student_tutor
                    student_debt = student_hours * student_tutor.cost_per_session
                    tutor_pay = student_hours * student_tutor.pay_per_hour
                    admin_profit_percentage = (abs(student_tutor.cost_per_session - student_tutor.pay_per_hour) / (
                            (student_tutor.cost_per_session + student_tutor.pay_per_hour) / 2)) * 100
                    admin_profit_amount = (admin_profit_percentage / 100) * student_debt
                    total_admin_profit = total_admin_profit + admin_profit_amount

                    record = StudentDebt(
                        start_hours=student_meeting_time_start,
                        end_hours=student_meeting_time_end,
                        hours=student_hours,
                        student_id=student.id,
                        student_name=student.name,
                        student_debt=student_debt,
                        tutor_id=student_tutor.id,
                        tutor_name=student_tutor.name,
                        tutor_cost=student_tutor.cost_per_session,
                        pending_onboarding=(not student.has_default_payment_method),
                        stripe_customer_id=student.stripe_customer_id,
                        admin_profit=admin_profit_amount,
                        pending_coupon=student.pending_discount_coupon if (student.has_pending_discount_coupon) else None
                    )

                    #Check if student was already billed
                    saved_record = None
                    if (previous_payroll is not None):
                        saved_record = find_student_debt_by_student_id(
                            previous_payroll.students_debt,
                            record.student_id
                        )

                    if (saved_record is None or saved_record.paid):
                        students_to_charge.append(saved_record if saved_record is not None else record)
                    else:
                        students_to_charge.append(record)

                    #Check if it's a new tutor
                    if (student_tutor.id in tutors_payout):
                        tutor_payout = tutors_payout[student_tutor.id]
                        tutor_payout["tutor_payout"] += tutor_pay
                        tutor_payout["tutor_total_hours"] += student_hours
                    else:
                        tutor_pending_onboarding = True if (student_tutor.stripe_subaccount_id is None) else False
                        tutors_payout[student_tutor.id] = {
                            "tutor_id": student_tutor.id,
                            "tutor_name": student_tutor.name,
                            "tutor_payout": tutor_pay,
                            "tutor_total_hours": student_hours,
                            "pending_onboarding": tutor_pending_onboarding,
                            "sub_account_id": student_tutor.stripe_subaccount_id
                        }

            if (previous_payroll is not None):
                tutors_payouts = [
                    (saved if (saved := find_tutor_pay_by_tutor_id(
                        previous_payroll.tutors_payout,
                        tutor_id)) is not None and saved.paid else TutorPayout(
                        tutor_id=tutor_id,
                        tutor_name=info.get("tutor_name"),
                        tutor_payout=info.get("tutor_payout"),
                        tutor_total_hours=info.get("tutor_total_hours"),
                        pending_onboarding=info.get("pending_onboarding"),
                        stripe_sub_account_id=info.get("sub_account_id")
                    ))
                    for tutor_id, info in tutors_payout.items()
                ]
            else:
                tutors_payouts = [
                    TutorPayout(
                        tutor_id=tutor_id,
                        tutor_name=info.get("tutor_name"),
                        tutor_payout=info.get("tutor_payout"),
                        tutor_total_hours=info.get("tutor_total_hours"),
                        pending_onboarding=info.get("pending_onboarding"),
                        stripe_sub_account_id=info.get("sub_account_id")
                    ) for (tutor_id, info) in tutors_payout.items()]

            tutors_lost = [
                TutorNotFound(
                    tutor_name=tutor.get("tutor_name"),
                    students=tutor.get("students")
                ) for (_id, tutor) in tutors_not_found.items()
            ]

            admin_pending_onboarding = True if (admin.stripe_subaccount_id is None) else False
            admin_payout = AdminPayout(
                admin_total_profit=total_admin_profit,
                admin_sub_account_id=admin.stripe_subaccount_id,
                pending_onboarding=admin_pending_onboarding
            )

            if (previous_payroll is not None):
                admin_payout_saved: AdminPayout = previous_payroll.admin_payout
                if (previous_payroll.admin_paid or admin_payout_saved.admin_transference_id != ""):
                    admin_payout = admin_payout_saved

            payroll = Payroll(
                company_code=admin.CompanyCode,
                admin_id=admin.id,
                students_debt=students_to_charge,
                tutors_payout=tutors_payouts,
                tutors_not_found=tutors_lost,
                students_with_error=with_error,
                admin_payout=admin_payout
            )

            insert_response: Response
            if (previous_payroll is not None):
                insert_response = self.payroll_dao.update_payroll_by_id(previous_payroll.id, payroll)
            else:
                insert_response = self.payroll_dao.create_payroll(payroll)

            if (insert_response.success):
                response.response = insert_response.response
                response.success = True

        except Exception as e:
            response.message = str(e)

        return response

    def charge_students_by_payroll(self, payroll_id: str) -> Response:
        """
            Charge all the students based on previous payroll created
            Args:
                payroll_id: The payroll id
            Returns:
                response.response =
        """
        response = Response()

        try:
            payroll_response = self.payroll_dao.read_payroll_by_id(payroll_id)

            if (not payroll_response.success):
                raise Exception(payroll_response.message)

            payroll: Payroll = payroll_response.response
            students_to_charge = payroll.students_debt

            new_students_list = []
            for student in students_to_charge:
                if (not student.pending_onboarding and not student.paid):
                    create_student_invoice = self.stripe_service.create_complete_invoice(
                        student.stripe_customer_id,
                        student.student_debt,
                        "not sure what is this... yet",
                        student.pending_coupon
                    )

                    student_invoice = create_student_invoice.response
                    student.stripe_invoice_id = student_invoice["id"]
                    charge_response = self.stripe_service.charge_invoice(student.stripe_invoice_id)

                    if (charge_response.success):
                        self.user_dao.remove_applied_invoice_coupon(student.student_id)
                        student.paid = True
                    else:
                        student.error = charge_response.message

                new_students_list.append(student)

            all_charged = all(student.paid for student in new_students_list)
            if (all_charged):
                self.payroll_dao.set_payroll_student_debt_charged(payroll.id)

            response = self.payroll_dao.update_payroll_student_debt(payroll.id, new_students_list)
        except Exception as e:
            response.message = str(e)

        return response

    def pay_tutors_by_payroll(self, payroll_id: str) -> Response:
        """
            Args:
                payroll_id:
            Returns:
        """
        response = Response()

        try:
            payroll_response = self.payroll_dao.read_payroll_by_id(payroll_id)

            if (not payroll_response.success):
                raise Exception(payroll_response.message)

            payroll: Payroll = payroll_response.response

            if (not payroll.students_charged):
                raise Exception("must_charge_students_first")
            tutors_to_pay = payroll.tutors_payout

            new_tutors_to_pay = []
            for tutor in tutors_to_pay:
                if (not tutor.pending_onboarding and not tutor.paid):
                    need_to_transfer = True if tutor.stripe_transference_id == "" else False

                    if (need_to_transfer):
                        transference_response = self.stripe_service.transfer_amount_to_sub_account(
                            tutor.stripe_sub_account_id,
                            tutor.tutor_payout
                        )
                        tutor.stripe_transference_id = transference_response.response["id"]

                        if (not transference_response.success):
                            tutor.error = transference_response.message

                    payout_response = self.stripe_service.payout_to_tutor_sub_account(
                        tutor.stripe_sub_account_id,
                        tutor.tutor_payout
                    )

                    if (payout_response.success):
                        tutor.paid = True
                        tutor.stripe_payout_id = payout_response.response["id"]
                    else:
                        tutor.error = payout_response.message

                new_tutors_to_pay.append(tutor)

            all_paid = all(tutor.paid for tutor in new_tutors_to_pay)
            if (all_paid):
                self.payroll_dao.set_payroll_tutors_payout_paid(payroll.id)

            response = self.payroll_dao.update_payroll_tutors_payout(payroll.id, new_tutors_to_pay)
        except Exception as e:
            response.message = str(e)

        return response

    def pay_admin_by_payroll(self, payroll_id: str):
        """
           Args:
               payroll_id:
           Returns:
        """
        response = Response()

        try:
            payroll_response = self.payroll_dao.read_payroll_by_id(payroll_id)

            if (not payroll_response.success):
                raise Exception(payroll_response.message)

            payroll: Payroll = payroll_response.response
            if (not payroll.tutors_paid):
                raise Exception("must_paid_tutors_first")

            admin_user_response = self.company_service(payroll.company_code).read_admin()
            if (not admin_user_response.success):
                raise Exception(admin_user_response.message)

            admin: TutorUser = admin_user_response.response["user"]

            if (admin.stripe_subaccount_id != "" and admin.stripe_subaccount_id is not None and not payroll.admin_paid):
                need_to_transfer = True if payroll.admin_payout.admin_transference_id == "" else False

                if (need_to_transfer):
                    transference_response = self.stripe_service.transfer_amount_to_sub_account(
                        admin.stripe_subaccount_id,
                        payroll.admin_payout.admin_total_profit
                    )
                    payroll.admin_payout.admin_transference_id = transference_response.response["id"]

                    if (not transference_response.success):
                        payroll.admin_payout.error = transference_response.message

                payout_response = self.stripe_service.payout_to_tutor_sub_account(
                    payroll.admin_payout.admin_sub_account_id,
                    payroll.admin_payout.admin_total_profit
                )

                if (payout_response.success):
                    payroll.admin_payout.admin_payout_id = payout_response.response["id"]
                    self.payroll_dao.set_payroll_admin_payout_paid(payroll.id)
                    self.payroll_dao.mark_payroll_completed(payroll.id)
                    self.user_dao.update_admin_last_payroll_date(admin.id)
                else:
                    payroll.admin_payout.error = payout_response.message

            response = self.payroll_dao.update_payroll_admin_payout(payroll.id, payroll.admin_payout)
        except Exception as e:
            response.message = str(e)

        return response
