from entities import Response, Coupon
from services import CouponService
from flask import Blueprint, request

coupon = Blueprint("coupon", __name__, url_prefix="/coupons")


@coupon.route("/create_coupon", methods=["POST"])
def create_coupon():
    """Creates a new discount coupon
        ---
        tags:
            - Coupons
        parameters:
            - name: name
              in: formData
              type: string
              required: true
              description: the new coupon's name
            - name: type
              in: formData
              type: string
              enum: [percentage, amount]
              required: true
              description: the discount type
            - name: amount_off
              in: formData
              type: integer
              required: true
              description: the amount/percent of the discount
            - name: max_redemptions
              in: formData
              type: integer
              required: true
              description: How many times can be used
            - name: duration
              in: formData
              type: string
              enum: [once, forever, repeating]
              required: true
              description: once -> Applies to the first charge from a subscription with this coupon applied forever-> Applies to all charges from a subscription with this coupon applied. repeating -> Applies to charges in the first "duration_in_months" months from a subscription with this coupon applied.
            - name: duration_in_months
              in: formData
              type: integer
              required: false
              description: required if duration=repeating
        responses:
            200:
                description: Returns a Response object with the new coupon object
    """
    response = Response()
    try:
        name = request.form.get("name")
        _type = request.form.get("type")
        amount_off = request.form.get("amount_off", type=float)
        max_redemptions = request.form.get("max_redemptions", type=int)
        duration = request.form.get("duration")
        duration_in_months = request.form.get("duration_in_months", type=int, default=0)

        if (not name):
            raise Exception("name_is_required")

        if (not _type):
            raise Exception("type_is_required")

        if (not amount_off):
            raise Exception("amount_off_is_required")

        if (not max_redemptions):
            raise Exception("max_redemptions_is_required")

        if (not duration):
            raise Exception("duration_is_required")

        if (duration == "repeating" and not duration_in_months):
            duration_in_months = int(duration_in_months)
            raise Exception("duration_in_months_is_required")

        response = CouponService().create_coupon(
            name,
            _type,
            amount_off,
            max_redemptions,
            duration,
            duration_in_months
        )
    except Exception as e:
        response.message = e
    return response.model_dump()


@coupon.route("/read_available_coupons", methods=["GET"])
def read_available_coupons():
    """Read all the available coupons
            ---
            tags:
                - Coupons
            responses:
                200:
                    description: Returns a Response object with a list with coupon objects
    """
    response = Response()

    try:
        response = CouponService().read_available_coupons()
    except Exception as e:
        response.message = e
    return response.model_dump()


@coupon.route("/activate_coupon", methods=["POST"])
def activate_coupon():
    """Applies a coupon to a user
            ---
            tags:
                - Coupons
            parameters:
                - name: user_id
                  in: formData
                  type: string
                  required: true
                  description: the new user id
                - name: coupon_id
                  in: formData
                  type: string
                  required: true
                  description: the coupon id to apply
                - name: apply_to
                  in: formData
                  type: string
                  enum: [subscription, invoice]
                  required: true
                  description: apply
            responses:
                200:
                    description: Returns a Response object with the result
    """
    response = Response()

    try:
        user_id = request.form.get("user_id")
        coupon_id = request.form.get("coupon_id")
        apply_to = request.form.get("apply_to")

        if (not user_id):
            raise Exception("user_id_is_required")

        if (not coupon_id):
            raise Exception("coupon_id_is_required")

        if (not apply_to):
            raise Exception("apply_to_is_required")

        if (apply_to == "subscription"):
            response = CouponService().apply_coupon_to_user_subscription(user_id, coupon_id)
        elif (apply_to == "invoice"):
            response = CouponService().apply_coupon_to_student_next_invoice(user_id, coupon_id)
        else:
            response.message = "invalid_apply_type"
    except Exception as e:
        response.message = e

    return response.model_dump()

