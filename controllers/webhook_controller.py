from flask import Blueprint, request
from entities import Response
from services import StripeService
import json, stripe

webhook = Blueprint("webhook", __name__)


@webhook.route("/webhook_callbacks", methods=["POST"])
def webhook_callbacks():
    response = Response()
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), sig_header, stripe.api_key
        )
        StripeService().manage_webhook(event)
        response.success = True
    except Exception as e:
        response.message = str(e)

    return response.model_dump()
