from flask import Blueprint, request
from entities import Response
from services import CompanyService

company = Blueprint("company", __name__, url_prefix="/company")


@company.route("/read_tutors", methods=["GET"])
def read_tutors():
    """Read all the tutors under a company code
        ---
        tags:
            - Company
        parameters:
            - name: company_code
              in: query
              type: string
              required: true
              description: the company code
        responses:
            200:
                description: Returns a Response object with the list of tutors user objects
                schema:
                    $ref: '#/definitions/TutorUser'
        """
    response = Response()

    try:
        company_code = request.args.get("company_code")

        if (not company_code):
            raise Exception("company_code_is_required")

        response = CompanyService(company_code).read_tutors()
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/set_company_type", methods=["POST"])
def set_company_type():
    """Sets a company_type for all the users under a company_code
       ---
       tags:
            - Company
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the company code
            - name: company_type
              in: formData
              type: string
              enum: [tutor_group, individual_group]
              required: true
              description: the company type must be one of [tutor_group, individual_group]
       responses:
            200:
                description: Returns a Response object with the result
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()

    try:
        company_code = request.form.get("company_code")
        company_type = request.form.get("company_type")

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not company_type):
            raise Exception("company_type_is_required")

        response = CompanyService(company_code).set_company_type(company_type)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/set_tutor_pay_configuration", methods=["POST"])
def set_tutor_pay_configuration():
    """Sets the session price and session pay for a tutor
           ---
           tags:
                - Company
           parameters:
                - name: company_code
                  in: formData
                  type: string
                  required: true
                  description: the tutor's company code
                - name: tutor_id
                  in: formData
                  type: string
                  required: true
                  description: the tutor's id
                - name: price
                  in: formData
                  type: integer
                  required: true
                  description: the tutor's price per session in dollars
                - name: pay
                  in: formData
                  type: integer
                  required: true
                  description: the tutor's pay per session in dollars
           responses:
                200:
                    description: Returns a Response object with the result
                    schema:
                        $ref: '#/definitions/Response'
    """

    response = Response()

    try:

        company_code = request.form.get("company_code")
        tutor_id = request.form.get("tutor_id")
        price = int(request.form.get("price"))
        pay = int(request.form.get("pay"))

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not tutor_id):
            raise Exception("tutor_id_is_required")

        if (not pay or pay <= 0):
            raise Exception("pay_is_required")

        if (not price or price <= 0):
            raise Exception("price_is_required")

        response = CompanyService(company_code).set_tutor_payment_configuration(tutor_id, pay, price)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/set_tutor_session_price", methods=["POST"])
def set_tutor_session_price():
    """Sets the session price for a tutor
       ---
       tags:
            - Company
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the tutor's company code
            - name: tutor_id
              in: formData
              type: string
              required: true
              description: the tutor's id
            - name: price
              in: formData
              type: integer
              required: true
              description: the tutor's session price in dollars
       responses:
            200:
                description: Returns a Response object with the result
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()

    try:

        company_code = request.form.get("company_code")
        tutor_id = request.form.get("tutor_id")
        price = int(request.form.get("price"))

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not tutor_id):
            raise Exception("tutor_id_is_required")

        if (not price or price <= 0):
            raise Exception("price_is_required")

        response = CompanyService(company_code).set_tutor_session_price(tutor_id, price)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/set_tutor_pay_amount", methods=["POST"])
def set_tutor_pay_amount():
    """Sets the session pay for a tutor
       ---
       tags:
            - Company
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the tutor's company code
            - name: tutor_id
              in: formData
              type: string
              required: true
              description: the tutor's id
            - name: price
              in: formData
              type: integer
              required: true
              description: the tutor's pay per session in dollars
       responses:
            200:
                description: Returns a Response object with the result
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()

    try:
        company_code = request.form.get("company_code")
        tutor_id = request.form.get("tutor_id")
        price = int(request.form.get("price"))

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not tutor_id):
            raise Exception("tutor_id_is_required")

        if (not price or price <= 0):
            raise Exception("price_is_required")

        response = CompanyService(company_code).set_tutor_pay_amount(tutor_id, price)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/create_student_onboarding_link", methods=["POST"])
def create_student_onboarding_link():
    """Create an onboarding link for a student.
        With the onboarding the student will create his default payment method, so we can charge him later
       ---
       tags:
            - Company
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the student's company code
            - name: student_id
              in: formData
              type: string
              required: true
              description: the student_id's id
       responses:
            200:
                description: Returns a Response object with the result
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()

    try:
        company_code = request.form.get("company_code")
        student_id = request.form.get("student_id")

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not student_id):
            raise Exception("student_id_is_necessary")

        response = CompanyService(company_code).create_student_onboarding_link(student_id)
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/validate_student_onboard", methods=["POST"])
def validate_student_onboard():
    """Validates if a student onboarding payment method was successfully created.
        This is not necessary because stripe will notify us throw the webhook. But can be used if there is problems with notifications
        ---
        tags:
            - Company
        parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the student's company code
            - name: student_id
              in: formData
              type: string
              required: true
              description: the student_id's id
        responses:
            200:
                description: Returns a Response object with the result of the operation
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()

    try:
        company_code = request.form.get("company_code")
        student_id = request.form.get("student_id")

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not student_id):
            raise Exception("student_id_is_necessary")

        response = CompanyService(company_code).validate_student_onboarding(student_id)
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/create_tutor_onboarding_link", methods=["POST"])
def create_tutor_onboarding_link():
    """Create an onboarding link for a tutor.
        With the onboarding the tutor will create his default bank account to receive payouts
       ---
       tags:
            - Company
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: the student's company code
            - name: tutor_id
              in: formData
              type: string
              required: true
              description: the tutor's id
       responses:
            200:
                description: Returns a Response object with the result
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()
    try:
        company_code = request.form.get("company_code")
        tutor_id = request.form.get("tutor_id")

        if (not company_code):
            raise Exception("company_code_is_required")

        if (not tutor_id):
            raise Exception("tutor_id_is_necessary")

        response = CompanyService(company_code).create_tutor_onboarding_link(tutor_id)
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@company.route("/create_admin_onboarding_link", methods=["POST"])
def create_admin_onboarding_link():
    """Create an onboarding link for an admin.
        With the onboarding the admin will create his default bank account to receive payouts
       ---
       tags:
            - Company
       parameters:
            - name: company_code
              in: formData
              type: string
              required: true
              description: a company code
       responses:
            200:
                description: Returns a Response object with the result
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()
    try:
        company_code = request.form.get("company_code")

        if (not company_code):
            raise Exception("company_code_is_required")

        response = CompanyService(company_code).create_admin_onboarding_link()
    except Exception as e:
        response.message = str(e)

    return response.model_dump()
