from flask import Blueprint, request
from entities import Response
from services import PayrollService

payroll = Blueprint("payroll", __name__, url_prefix="/payroll")


@payroll.route("/create_company_payroll", methods=["POST"])
def create_company_payroll():
    """Creates a new payroll summary to be paid after
       ---
       tags:
            - Payroll
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the company code to create the payroll
       responses:
            200:
                description: Returns a Response object with the payroll object
                schema:
                    $ref: '#/definitions/Payroll'
    """
    response = Response()

    try:
        company_code = request.form.get("company_code")

        if (not company_code):
            raise Exception("company_code_is_required")

        response = PayrollService().prepare_payroll(company_code)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payroll.route("/charge_company_students", methods=["POST"])
def charge_company_students():
    """After we create a payroll summary we get a list of students debts
       This method charges all the users who have a payment method
       ---
       tags:
            - Payroll
       parameters:
            - name: payroll_id
              in: formData
              type: string
              required: true
              description: the payroll id
       responses:
            200:
                description: Returns a Response object with the updated payroll object
                schema:
                    $ref: '#/definitions/Payroll'
    """
    response = Response()

    try:
        payroll_id = request.form.get("payroll_id")

        if (not payroll_id):
            raise Exception("payroll_id_is_required")

        response = PayrollService().charge_students_by_payroll(payroll_id)
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payroll.route("/pay_company_tutors", methods=["POST"])
def pay_company_tutors():
    """After we create a payroll summary we get a list of tutors ready to get paid
       This method sends a payout to every tutor who has a bank account set
       ---
       tags:
            - Payroll
       parameters:
            - name: payroll_id
              in: formData
              type: string
              required: true
              description: the payroll id
       responses:
            200:
                description: Returns a Response object with the updated payroll object
                schema:
                    $ref: '#/definitions/Payroll'
    """
    response = Response()

    try:
        payroll_id = request.form.get("payroll_id")

        if (not payroll_id):
            raise Exception("payroll_id_is_required")

        response = PayrollService().pay_tutors_by_payroll(payroll_id)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payroll.route("/pay_company_admin", methods=["POST"])
def pay_company_admin():
    """After we create a payroll summary we get the admin profit
       This method sends a payout to the admin bank account set if there is some
       ---
       tags:
            - Payroll
       parameters:
            - name: payroll_id
              in: formData
              type: string
              required: true
              description: the payroll id
       responses:
            200:
                description: Returns a Response object with the updated payroll object
                schema:
                    $ref: '#/definitions/Payroll'
    """
    response = Response()

    try:
        payroll_id = request.form.get("payroll_id")

        if (not payroll_id):
            raise Exception("payroll_id_is_required")

        response = PayrollService().pay_admin_by_payroll(payroll_id)
    except Exception as e:
        response.message = str(e)

    return response.model_dump()
