from flask import Blueprint, request
from entities import Response
from services import PaymentService

payments = Blueprint("payments", __name__, url_prefix="/payments")


@payments.route("/create_payment_session", methods=["POST"])
def create_payment_session():
    """Creates a new payment link for a client to buy a membership
       ---
       tags:
            - Payments
       parameters:
            - name: user_id
              in: formData
              type: string
              required: true
              description: the user id who wants to buy
            - name: membership_id
              in: formData
              type: string
              required: true
              description: the membership id to be bought
            - name: coupon_id
              in: formData
              type: string
              required: false
              description: the local coupon id to apply
       responses:
            200:
                description: Returns a Response object with the payment session in response
                schema:
                    $ref: '#/definitions/PaymentSession'
   """
    response = Response()

    try:
        user_id = request.form.get("user_id")
        membership_id = request.form.get("membership_id")
        coupon_id = request.form.get("coupon_id", default="")

        if (not user_id):
            raise Exception("user_id_is_required")

        if (not membership_id):
            raise Exception("membership_id_is_required")

        response = PaymentService(user_id).buy_subscription(membership_id, coupon_id)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payments.route("/read_subscription", methods=["GET"])
def read_subscription():
    """Read the user's actives subscription
        ---
        tags:
            - Payments
        parameters:
            - name: user_id
              in: query
              type: string
              required: true
              description: the user's id to check its active subscription
        responses:
            200:
                description: Returns a Response object with the list of active subscription
                schema:
                    $ref: '#/definitions/Membership'
    """
    response = Response()
    try:
        user_id = request.args.get("user_id")

        if (not user_id):
            raise Exception("user_id_is_required")

        response = PaymentService(user_id).read_active_subscription()

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payments.route("/update_subscription", methods=["POST"])
def update_subscription():
    """Updates an admin subscription, the admin can add or remove licences
        ---
        tags:
            - Payments
        parameters:
            - name: user_id
              in: formData
              type: string
              required: true
              description: the admin id
            - name: quantity
              in: formData
              type: integer
              required: true
              description: The number of licences to add or remove. This can be a positive or negative number. Ex You can add +5 licences or delete -3 licences.
        responses:
            200:
                description: Returns a Response object with the result of the operation
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()
    try:
        user_id = request.form.get("user_id")
        quantity = int(request.form.get("quantity"))

        if (not user_id):
            raise Exception("user_id_is_required")

        if (not quantity or quantity == 0):
            raise Exception("quantity_is_required")

        response = PaymentService(user_id).update_active_subscription(quantity)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payments.route("/cancel_subscription", methods=["POST"])
def cancel_subscription():
    """Cancel a subscription to stop the recurring payments
        ---
        tags:
            - Payments
        parameters:
            - name: user_id
              in: formData
              type: string
              required: true
              description: the user's id to cancel his membership
        responses:
            200:
                description: Returns a Response object with the result of the operation
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()
    try:
        user_id = request.form.get("user_id")

        if (not user_id):
            raise Exception("user_id_is_required")

        response = PaymentService(user_id).cancel_active_subscription()
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@payments.route("/validate_subscription", methods=["GET"])
def validate_subscription():
    """Validates if a payment was successfully paid
        This is not necessary because stripe will notify us throw the webhook. But can be used if there is problems with notifications
        ---
        tags:
            - Payments
        parameters:
            - name: payment_random_id
              in: query
              type: string
              required: true
              description: The payment random id of the transaction, can be found in the subscription object of the transaction
        responses:
            200:
                description: Returns a Response object with the result of the operation
                schema:
                    $ref: '#/definitions/Response'
    """
    response = Response()
    try:
        payment_id = request.args.get("payment_random_id")

        if (not payment_id):
            raise Exception("payment_random_id_is_required")

        response = PaymentService("").validate_payment(payment_id)

    except Exception as e:
        response.message = str(e)

    return response.model_dump()
