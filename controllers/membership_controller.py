from entities import Response
from services import MembershipService
from flask import Blueprint, request
from utils.example import create_example_memberships

membership = Blueprint("membership", __name__, url_prefix="/memberships")


@membership.route("/read_memberships", methods=["GET"])
def read_memberships():
    """Read all the membership that the given user can buy.
        ---
        tags:
            - Membership
        parameters:
            - name: user_id
              in: query
              type: string
              required: true
              description: the user's id to check what kind of memberships can buy
        responses:
            200:
                description: Returns a Response object with the list of active memberships
                schema:
                    $ref: '#/definitions/Membership'
        """
    response = Response()

    try:
        user_id = request.args.get("user_id")

        if (not user_id):
            raise Exception("user_id_is_required")

        response = MembershipService(user_id).read_memberships()
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@membership.route("/read_active_membership", methods=["GET"])
def read_active_membership():
    """Reads the active membership from a user
        ---
        tags:
            - Membership
        parameters:
            - name: user_id
              in: query
              type: string
              required: true
              description: the user's id to check its active memberships
        responses:
            200:
                description: Returns a Response object with a list of active memberships
                schema:
                    $ref: '#/definitions/Membership'
    """
    response = Response()

    try:
        user_id = request.args.get("user_id")

        if (not user_id):
            raise Exception("user_id_is_required")

        response = MembershipService(user_id).read_active_membership()
    except Exception as e:
        response.message = str(e)

    return response.model_dump()


@membership.route("/create_membership", methods=["POST"])
def create_membership():
    """Creates a membership
        ---
        tags:
            - Membership
        parameters:
            - name: name
              in: formData
              type: string
              required: true
              description: the name of the new membership
            - name: price
              in: formData
              type: int
              required: true
              description: the price in dollars of the new membership
            - name: type
              in: formData
              type: string
              enum: [Admin, Individual]
              required: true
              description: the user type that can buy the membership
        responses:
            200:
                description: Returns a Response object with the new membership created
                schema:
                    $ref: '#/definitions/Membership'
    """
    response = Response()

    try:
        membership_price = request.form.get("price")
        membership_name = request.form.get("name")
        membership_type = request.form.get("type")

        if (not membership_name):
            raise Exception("name_is_required")

        if (not membership_price or int(membership_price) <= 0):
            raise Exception("price_is_required")

        if (not membership_type):
            raise Exception("type_is_required")

        if (membership_type.strip().lower() != "admin" and membership_type.strip().lower() != "individual"):
            raise Exception("invalid_membership_type")

        admin_activate = True if membership_type.strip().lower() == "admin" else False
        response = create_example_memberships(membership_name, int(membership_price), admin_activate)
    except Exception as e:
        response.message = str(e)

    return response.model_dump()

