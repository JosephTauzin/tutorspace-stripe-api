from entities import Response, Product, StripeCustomer, SubAccount, Session, Coupon
from utils.utils import dollars_to_cents
from os import environ
import stripe


class StripeInterface():
    """
        @StripeService
        A helper class for handling payments using the stripe API.
    """

    def __init__(self) -> None:
        try:
            stripe.api_key = environ["STRIPE_API"]
        except Exception as e:
            raise Exception("invalid_stripe_apikey")

    def create_product(self, product: Product) -> Response:
        """
            A function to create a product in stripe.
            Products can be bought just once or recurrently.
            Args:
                product: A product object to be created
            Returns:
                response: A response object
                    response.response(dict): a stripe dict object with the response:
                        {
                            "id": "prod_NWjs8kKbJWmuuc",
                            "object": "product",
                            "active": true,
                            "created": 1678833149,
                            "default_price": null,
                            "description": null,
                            "images": [],
                            "features": [],
                            "livemode": false,
                            "metadata": {},
                            "name": "Gold Plan",
                            "package_dimensions": null,
                            "shippable": null,
                            "statement_descriptor": null,
                            "tax_code": null,
                            "unit_label": null,
                            "updated": 1678833149,
                            "url": null
                        }
        """
        response = Response()
        try:
            stripe_response = stripe.Product.create(
                name=product.name,
                description=product.description,
                default_price_data=product.default_price_data.model_dump()
            )
            response.success = True if ("id" in stripe_response) else False
            response.response = stripe_response
        except Exception as e:
            response.message = str(e)

        return response

    def create_customer(self, customer: StripeCustomer) -> Response:
        """
            A function for create a customer in stripe.
            Before every buy it is necessary a customer, so we can associate the buy in stripe.
            Args:
                customer: A stripe customer object to be created
            Returns:
                response: A response object
                    response.response (dict): a stripe dict object with the response: 
                    {
                        "id": "cus_NffrFeUfNV2Hib",
                        "object": "customer",
                        "address": null,
                        "balance": 0,
                        "created": 1680893993,
                        "currency": null,
                        "default_source": null,
                        "delinquent": false,
                        "description": null,
                        "discount": null,
                        "email": "jennyrosen@example.com",
                        "invoice_prefix": "0759376C",
                        "invoice_settings": {
                            "custom_fields": null,
                            "default_payment_method": null,
                            "footer": null,
                            "rendering_options": null
                        },
                        "livemode": false,
                        "metadata": {},
                        "name": "Jenny Rosen",
                        "next_invoice_sequence": 1,
                        "phone": null,
                        "preferred_locales": [],
                        "shipping": null,
                        "tax_exempt": "none",
                        "test_clock": null
                    }
        """
        response = Response()

        try:
            create_customer_response = stripe.Customer.create(
                name=customer.name,
                email=customer.email
            )

            response.success = True if ("id" in create_customer_response) else False
            response.response = create_customer_response
        except Exception as e:
            response.message = str(e)

        return response

    def update_customer_default_payment_method(self, customer_id: str, payment_method_id: str) -> Response:
        """
            Updates the default stripe payment method for a customer
            Args:
                customer_id: a stripe customer id
                payment_method_id: a stripe payment method id associated to the customer id
            Returns:
                response: a response object
                    response.response (dict):  a stripe dict object with the response:
                    {
                          "address": null,
                          "balance": 0,
                          "created": 1715982205,
                          "currency": "usd",
                          "default_source": null,
                          "delinquent": false,
                          "description": null,
                          "discount": null,
                          "email": "admin@mail.com",
                          "id": "cus_Q7oB3B1StmpKzG",
                          "invoice_prefix": "30039FA9",
                          "invoice_settings": {
                            "custom_fields": null,
                            "default_payment_method": "pm_1PIZd0EMUa1BUwGIMUMzYd36",
                            "footer": null,
                            "rendering_options": null
                          },
                          "livemode": false,
                          "metadata": {},
                          "name": null,
                          "next_invoice_sequence": 3,
                          "object": "customer",
                          "phone": null,
                          "preferred_locales": [],
                          "shipping": null,
                          "tax_exempt": "none",
                          "test_clock": null
                        }
        """
        response = Response()

        try:
            update_customer_response = stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )

            response.success = True if ("id" in update_customer_response) else False
            response.response = update_customer_response
        except Exception as e:
            response.message = str(e)

        return response

    def read_customer_by_id(self, stripe_customer_id: str) -> Response:
        """
            Reads a stripe customer information with a stripe customer id.
            Args:
                stripe_customer_id: A stripe customer id
            Returns:
                response: A response object
                    response.response (dict): a stripe dict object with the response:
                        {
                            "id": "cus_NffrFeUfNV2Hib",
                            "object": "customer",
                            "address": null,
                            "balance": 0,
                            "created": 1680893993,
                            "currency": null,
                            "default_source": null,
                            "delinquent": false,
                            "description": null,
                            "discount": null,
                            "email": "jennyrosen@example.com",
                            "invoice_prefix": "0759376C",
                            "invoice_settings": {
                                "custom_fields": null,
                                "default_payment_method": null,
                                "footer": null,
                                "rendering_options": null
                            },
                            "livemode": false,
                            "metadata": {},
                            "name": "Jenny Rosen",
                            "next_invoice_sequence": 1,
                            "phone": null,
                            "preferred_locales": [],
                            "shipping": null,
                            "tax_exempt": "none",
                            "test_clock": null
                        }
        """
        response = Response()

        try:
            customer_response = stripe.Customer.retrieve(stripe_customer_id)
            response.success = True if ("id" in customer_response) else False
            response.response = customer_response
        except Exception as e:
            response.message = str(e)

        return response

    def read_customer_by_email(self, customer_email: str) -> Response:
        """
            A function for read stripe customer information with an email
            Args:
                customer_email(str): A customer email
            Returns:
                response: A response object
                    response.response_list (list): a list of dicts with all the records found
                    {
                        "object": "list",
                        "url": "/v1/customers",
                        "has_more": false,
                        "data": [
                            {
                            "id": "cus_NffrFeUfNV2Hib",
                            "object": "customer",
                            "address": null,
                            "balance": 0,
                            "created": 1680893993,
                            "currency": null,
                            "default_source": null,
                            "delinquent": false,
                            "description": null,
                            "discount": null,
                            "email": "jennyrosen@example.com",
                            "invoice_prefix": "0759376C",
                            "invoice_settings": {
                                "custom_fields": null,
                                "default_payment_method": null,
                                "footer": null,
                                "rendering_options": null
                            },
                            "livemode": false,
                            "metadata": {},
                            "name": "Jenny Rosen",
                            "next_invoice_sequence": 1,
                            "phone": null,
                            "preferred_locales": [],
                            "shipping": null,
                            "tax_exempt": "none",
                            "test_clock": null
                            } 
                        ] 
                    }
        """
        response = Response()

        try:
            customer_response = stripe.Customer.search(query="email: '%s'" % customer_email)

            if ("data" in customer_response):
                response.success = True

                if (len(customer_response["data"]) > 0):
                    response.response_list = customer_response["data"]
                else:
                    response.message = "no_customer_found"
            else:
                response.message = "stripe_error"

        except Exception as e:
            response.message = str(e)

        return response

    def create_payment_session(self, payment: Session) -> Response:
        """
            Creates a payment subscription.
            Before a client can subscribe, it's necessary to add him as a customer in stripe, it's also
            necessary to have a product created. This product will have all the amount, currency and payment interval details.
            Args:
                payment: A session object
                callback_id (str): a callback unique id to validate the payment
            Returns:
                response: A response object
                    response.response (dict): a dict object with the stripe session object
                        {
                            "id": "cs_test_a11YYufWQzNY63zpQ6QSNRQhkUpVph4WRmzW0zWJO2znZKdVujZ0N0S22u",
                            "object": "checkout.session",
                            "after_expiration": null,
                            "allow_promotion_codes": null,
                            "amount_subtotal": 2198,
                            "amount_total": 2198,
                            "automatic_tax": {
                                "enabled": false,
                                "liability": null,
                                "status": null
                            },
                            "billing_address_collection": null,
                            "cancel_url": null,
                            "client_reference_id": null,
                            "consent": null,
                            "consent_collection": null,
                            "created": 1679600215,
                            "currency": "usd",
                            "custom_fields": [],
                            "custom_text": {
                                "shipping_address": null,
                                "submit": null
                            },
                            "customer": null,
                            "customer_creation": "if_required",
                            "customer_details": null,
                            "customer_email": null,
                            "expires_at": 1679686615,
                            "invoice": null,
                            "invoice_creation": {
                                "enabled": false,
                                "invoice_data": {
                                "account_tax_ids": null,
                                "custom_fields": null,
                                "description": null,
                                "footer": null,
                                "issuer": null,
                                "metadata": {},
                                "rendering_options": null
                                }
                            },
                            "livemode": false,
                            "locale": null,
                            "metadata": {},
                            "mode": "payment",
                            "payment_intent": null,
                            "payment_link": null,
                            "payment_method_collection": "always",
                            "payment_method_options": {},
                            "payment_method_types": [
                                "card"
                            ],
                            "payment_status": "unpaid",
                            "phone_number_collection": {
                                "enabled": false
                            },
                            "recovered_from": null,
                            "setup_intent": null,
                            "shipping_address_collection": null,
                            "shipping_cost": null,
                            "shipping_details": null,
                            "shipping_options": [],
                            "status": "open",
                            "submit_type": null,
                            "subscription": null,
                            "success_url": "https://example.com/success",
                            "total_details": {
                                "amount_discount": 0,
                                "amount_shipping": 0,
                                "amount_tax": 0
                            },
                            "url": "https://checkout.stripe.com/c/pay/cs_test_a11YYufWQzNY63zpQ6QSNRQhkUpVph4WRmzW0zWJO2znZKdVujZ0N0S22u#fidkdWxOYHwnPyd1blpxYHZxWjA0SDdPUW5JbmFMck1wMmx9N2BLZjFEfGRUNWhqTmJ%2FM2F8bUA2SDRySkFdUV81T1BSV0YxcWJcTUJcYW5rSzN3dzBLPUE0TzRKTTxzNFBjPWZEX1NKSkxpNTVjRjN8VHE0YicpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"
                        } 
        """
        response = Response()

        try:
            create_payment_response = stripe.checkout.Session.create(
                success_url="%ssuccess.html" % (environ["BASE_URL"]),
                client_reference_id=payment.client_reference_id,
                customer=payment.customer,
                mode=payment.mode,
                discounts=payment.discounts,
                line_items=payment.model_dump()["line_items"]
            )

            response.success = True if ("id" in create_payment_response) else False
            response.response = create_payment_response
        except Exception as e:
            response.message = str(e)

        return response

    def create_payment_session_without_pay(self, payment: Session) -> Response:
        """
            Creates a payment session link for get the customer payment information without any charge
            Args:
                payment: a payment session object with mode="setup" and a list of payment methods = ["card"]
            Returns:
                response: a response object
                    response.response (dict): a dict object with the stripe session object
        """
        response = Response()

        try:
            create_payment_response = stripe.checkout.Session.create(
                success_url="%ssuccess.html" % (environ["BASE_URL"]),
                client_reference_id=payment.client_reference_id,
                customer=payment.customer,
                mode=payment.mode,
                payment_method_types=payment.payment_method_types
            )

            response.success = True if ("id" in create_payment_response) else False
            response.response = create_payment_response
        except Exception as e:
            response.message = str(e)

        return response

    def read_payment_session_by_id(self, session_id: str) -> Response:
        """
            Reads a stripe payment session from stripe with an id
            Args:
                session_id(str): a stripe session id
            Returns:
                response: a response object
                    response.response (dict): a dict with the stripe session object
                        {
                            "id": "cs_test_a11YYufWQzNY63zpQ6QSNRQhkUpVph4WRmzW0zWJO2znZKdVujZ0N0S22u",
                            "object": "checkout.session",
                            "after_expiration": null,
                            "allow_promotion_codes": null,
                            "amount_subtotal": 2198,
                            "amount_total": 2198,
                            "automatic_tax": {
                                "enabled": false,
                                "liability": null,
                                "status": null
                            },
                            "billing_address_collection": null,
                            "cancel_url": null,
                            "client_reference_id": null,
                            "consent": null,
                            "consent_collection": null,
                            "created": 1679600215,
                            "currency": "usd",
                            "custom_fields": [],
                            "custom_text": {
                                "shipping_address": null,
                                "submit": null
                            },
                            "customer": null,
                            "customer_creation": "if_required",
                            "customer_details": null,
                            "customer_email": null,
                            "expires_at": 1679686615,
                            "invoice": null,
                            "invoice_creation": {
                                "enabled": false,
                                "invoice_data": {
                                "account_tax_ids": null,
                                "custom_fields": null,
                                "description": null,
                                "footer": null,
                                "issuer": null,
                                "metadata": {},
                                "rendering_options": null
                                }
                            },
                            "livemode": false,
                            "locale": null,
                            "metadata": {},
                            "mode": "payment",
                            "payment_intent": null,
                            "payment_link": null,
                            "payment_method_collection": "always",
                            "payment_method_options": {},
                            "payment_method_types": [
                                "card"
                            ],
                            "payment_status": "unpaid",
                            "phone_number_collection": {
                                "enabled": false
                            },
                            "recovered_from": null,
                            "setup_intent": null,
                            "shipping_address_collection": null,
                            "shipping_cost": null,
                            "shipping_details": null,
                            "shipping_options": [],
                            "status": "open",
                            "submit_type": null,
                            "subscription": null,
                            "success_url": "https://example.com/success",
                            "total_details": {
                                "amount_discount": 0,
                                "amount_shipping": 0,
                                "amount_tax": 0
                            },
                            "url": "https://checkout.stripe.com/c/pay/cs_test_a11YYufWQzNY63zpQ6QSNRQhkUpVph4WRmzW0zWJO2znZKdVujZ0N0S22u#fidkdWxOYHwnPyd1blpxYHZxWjA0SDdPUW5JbmFMck1wMmx9N2BLZjFEfGRUNWhqTmJ%2FM2F8bUA2SDRySkFdUV81T1BSV0YxcWJcTUJcYW5rSzN3dzBLPUE0TzRKTTxzNFBjPWZEX1NKSkxpNTVjRjN8VHE0YicpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl"
                        } 
        """
        response = Response()

        try:
            session_response = stripe.checkout.Session.retrieve(session_id)
            response.success = True if ("id" in session_response) else False
            response.response = session_response
        except Exception as e:
            response.message = str(e)

        return response

    def read_subscriptions_by_customer(self, customer_id: str) -> Response:
        """
            Reads every active subscription from a customer.
            Args:
                customer_id: A stripe customer id
            Returns:
                response: A response object
                    response.response_list (list): a list of dict objects with every subscription
                        {
                            "object": "list",
                            "url": "/v1/subscriptions",
                            "has_more": false,
                            "data": [
                                {
                                "id": "sub_1MowQVLkdIwHu7ixeRlqHVzs",
                                "object": "subscription",
                                "application": null,
                                "application_fee_percent": null,
                                "automatic_tax": {
                                    "enabled": false,
                                    "liability": null
                                },
                                "billing_cycle_anchor": 1679609767,
                                "billing_thresholds": null,
                                "cancel_at": null,
                                "cancel_at_period_end": false,
                                "canceled_at": null,
                                "cancellation_details": {
                                    "comment": null,
                                    "feedback": null,
                                    "reason": null
                                },
                                "collection_method": "charge_automatically",
                                "created": 1679609767,
                                "currency": "usd",
                                "current_period_end": 1682288167,
                                "current_period_start": 1679609767,
                                "customer": "cus_Na6dX7aXxi11N4",
                                "days_until_due": null,
                                "default_payment_method": null,
                                "default_source": null,
                                "default_tax_rates": [],
                                "description": null,
                                "discount": null,
                                "ended_at": null,
                                "invoice_settings": {
                                    "issuer": {
                                    "type": "self"
                                    }
                                },
                                "items": {
                                    "object": "list",
                                    "data": [
                                    {
                                        "id": "si_Na6dzxczY5fwHx",
                                        "object": "subscription_item",
                                        "billing_thresholds": null,
                                        "created": 1679609768,
                                        "metadata": {},
                                        "plan": {
                                        "id": "price_1MowQULkdIwHu7ixraBm864M",
                                        "object": "plan",
                                        "active": true,
                                        "aggregate_usage": null,
                                        "amount": 1000,
                                        "amount_decimal": "1000",
                                        "billing_scheme": "per_unit",
                                        "created": 1679609766,
                                        "currency": "usd",
                                        "interval": "month",
                                        "interval_count": 1,
                                        "livemode": false,
                                        "metadata": {},
                                        "nickname": null,
                                        "product": "prod_Na6dGcTsmU0I4R",
                                        "tiers_mode": null,
                                        "transform_usage": null,
                                        "trial_period_days": null,
                                        "usage_type": "licensed"
                                        },
                                        "price": {
                                        "id": "price_1MowQULkdIwHu7ixraBm864M",
                                        "object": "price",
                                        "active": true,
                                        "billing_scheme": "per_unit",
                                        "created": 1679609766,
                                        "currency": "usd",
                                        "custom_unit_amount": null,
                                        "livemode": false,
                                        "lookup_key": null,
                                        "metadata": {},
                                        "nickname": null,
                                        "product": "prod_Na6dGcTsmU0I4R",
                                        "recurring": {
                                            "aggregate_usage": null,
                                            "interval": "month",
                                            "interval_count": 1,
                                            "trial_period_days": null,
                                            "usage_type": "licensed"
                                        },
                                        "tax_behavior": "unspecified",
                                        "tiers_mode": null,
                                        "transform_quantity": null,
                                        "type": "recurring",
                                        "unit_amount": 1000,
                                        "unit_amount_decimal": "1000"
                                        },
                                        "quantity": 1,
                                        "subscription": "sub_1MowQVLkdIwHu7ixeRlqHVzs",
                                        "tax_rates": []
                                    }
                                    ],
                                    "has_more": false,
                                    "total_count": 1,
                                    "url": "/v1/subscription_items?subscription=sub_1MowQVLkdIwHu7ixeRlqHVzs"
                                },
                                "latest_invoice": "in_1MowQWLkdIwHu7ixuzkSPfKd",
                                "livemode": false,
                                "metadata": {},
                                "next_pending_invoice_item_invoice": null,
                                "on_behalf_of": null,
                                "pause_collection": null,
                                "payment_settings": {
                                    "payment_method_options": null,
                                    "payment_method_types": null,
                                    "save_default_payment_method": "off"
                                },
                                "pending_invoice_item_interval": null,
                                "pending_setup_intent": null,
                                "pending_update": null,
                                "schedule": null,
                                "start_date": 1679609767,
                                "status": "active",
                                "test_clock": null,
                                "transfer_data": null,
                                "trial_end": null,
                                "trial_settings": {
                                    "end_behavior": {
                                    "missing_payment_method": "create_invoice"
                                    }
                                },
                                "trial_start": null
                                }
                                {...}
                        ]
        """
        response = Response()

        try:
            subscription_response = stripe.Subscription.list(
                customer=customer_id
            )

            if ("data" in subscription_response):
                response.success = True

                if (len(subscription_response["data"]) > 0):
                    response.response_list = subscription_response["data"]
                else:
                    response.message = "no_subscription_found"
            else:
                response.message = "stripe_error"

        except Exception as e:
            response.message = str(e)

        return response

    def read_subscription_by_id(self, subscription_id: str) -> Response:
        """
            Reads a stripe subscription with an id
            Args:
                subscription_id: a stripe subscription id
            Returns:
                response: a response object
                    response.response (dict): a dict object with the stripe subscription
                        {
                            "id": "sub_1MowQVLkdIwHu7ixeRlqHVzs",
                            "object": "subscription",
                            "application": null,
                            "application_fee_percent": null,
                            "automatic_tax": {
                                "enabled": false,
                                "liability": null
                            },
                            "billing_cycle_anchor": 1679609767,
                            "billing_thresholds": null,
                            "cancel_at": null,
                            "cancel_at_period_end": false,
                            "canceled_at": null,
                            "cancellation_details": {
                                "comment": null,
                                "feedback": null,
                                "reason": null
                            },
                            "collection_method": "charge_automatically",
                            "created": 1679609767,
                            "currency": "usd",
                            "current_period_end": 1682288167,
                            "current_period_start": 1679609767,
                            "customer": "cus_Na6dX7aXxi11N4",
                            "days_until_due": null,
                            "default_payment_method": null,
                            "default_source": null,
                            "default_tax_rates": [],
                            "description": null,
                            "discount": null,
                            "ended_at": null,
                            "invoice_settings": {
                                "issuer": {
                                "type": "self"
                                }
                            },
                            "items": {
                                "object": "list",
                                "data": [
                                {
                                    "id": "si_Na6dzxczY5fwHx",
                                    "object": "subscription_item",
                                    "billing_thresholds": null,
                                    "created": 1679609768,
                                    "metadata": {},
                                    "plan": {
                                    "id": "price_1MowQULkdIwHu7ixraBm864M",
                                    "object": "plan",
                                    "active": true,
                                    "aggregate_usage": null,
                                    "amount": 1000,
                                    "amount_decimal": "1000",
                                    "billing_scheme": "per_unit",
                                    "created": 1679609766,
                                    "currency": "usd",
                                    "interval": "month",
                                    "interval_count": 1,
                                    "livemode": false,
                                    "metadata": {},
                                    "nickname": null,
                                    "product": "prod_Na6dGcTsmU0I4R",
                                    "tiers_mode": null,
                                    "transform_usage": null,
                                    "trial_period_days": null,
                                    "usage_type": "licensed"
                                    },
                                    "price": {
                                    "id": "price_1MowQULkdIwHu7ixraBm864M",
                                    "object": "price",
                                    "active": true,
                                    "billing_scheme": "per_unit",
                                    "created": 1679609766,
                                    "currency": "usd",
                                    "custom_unit_amount": null,
                                    "livemode": false,
                                    "lookup_key": null,
                                    "metadata": {},
                                    "nickname": null,
                                    "product": "prod_Na6dGcTsmU0I4R",
                                    "recurring": {
                                        "aggregate_usage": null,
                                        "interval": "month",
                                        "interval_count": 1,
                                        "trial_period_days": null,
                                        "usage_type": "licensed"
                                    },
                                    "tax_behavior": "unspecified",
                                    "tiers_mode": null,
                                    "transform_quantity": null,
                                    "type": "recurring",
                                    "unit_amount": 1000,
                                    "unit_amount_decimal": "1000"
                                    },
                                    "quantity": 1,
                                    "subscription": "sub_1MowQVLkdIwHu7ixeRlqHVzs",
                                    "tax_rates": []
                                }
                                ],
                                "has_more": false,
                                "total_count": 1,
                                "url": "/v1/subscription_items?subscription=sub_1MowQVLkdIwHu7ixeRlqHVzs"
                            },
                            "latest_invoice": "in_1MowQWLkdIwHu7ixuzkSPfKd",
                            "livemode": false,
                            "metadata": {},
                            "next_pending_invoice_item_invoice": null,
                            "on_behalf_of": null,
                            "pause_collection": null,
                            "payment_settings": {
                                "payment_method_options": null,
                                "payment_method_types": null,
                                "save_default_payment_method": "off"
                            },
                            "pending_invoice_item_interval": null,
                            "pending_setup_intent": null,
                            "pending_update": null,
                            "schedule": null,
                            "start_date": 1679609767,
                            "status": "active",
                            "test_clock": null,
                            "transfer_data": null,
                            "trial_end": null,
                            "trial_settings": {
                                "end_behavior": {
                                "missing_payment_method": "create_invoice"
                                }
                            },
                            "trial_start": null
                            }
        """
        response = Response()

        try:
            subscription_response = stripe.Subscription.retrieve(subscription_id)
            response.success = True if ("id" in subscription_response) else False
            response.response = subscription_response
        except Exception as e:
            response.message = str(e)

        return response

    def unsubscribe(self, subscription_id: str) -> Response:
        """
            Cancels a subscription to stop recurring payments.
            Every time a customer buy a product with recurring payments it generates a unique subscription id.
            Args:
                subscription_id: The stripe subscription id.
            Returns:
                response: A response object
        """
        response = Response()

        try:
            subscription_response = stripe.Subscription.cancel(subscription_id)
            response.success = True if ("id" in subscription_response) else False
        except Exception as e:
            response.message = str(e)

        return response

    def update_subscription_quantity(self, subscription_id: str, subscription_item_id: str, new_quantity: int) -> Response:
        """
            Updates a subscription in stripe
            Args:
                subscription_id (str): a stripe subscription id
                subscription_item_id (str): a stripe subscription item id
                new_quantity(int): the new total amount of licences
            Returns:
                response: A response object
        """
        response = Response()

        try:
            update_subscription_response = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription_item_id,
                    "quantity": new_quantity
                }])

            response.success = True if ("id" in update_subscription_response) else False
        except Exception as e:
            response.message = str(e)

        return response

    def read_setupintent(self, setupintent_id: str) -> Response:
        """
            A setup intent is an object that has the information for a stripe session that hads add a payment method,
            with a setup intent we can get a customer payment method and save it.
            Args:
                setupintent_id: a setup intent id
            Returns:
                response: a response object
                    response.response (dict): a dict object with the stripe subscription
                    {
                          "application": null,
                          "automatic_payment_methods": null,
                          "cancellation_reason": null,
                          "client_secret": "seti_1PIZcVEMUa1BUwGIBxCdlEUa_secret_Q8rLhWyxQhCrkrxZ7TPUGl2yDgQjQV4",
                          "created": 1716224611,
                          "customer": "cus_Q7oB3B1StmpKzG",
                          "description": null,
                          "flow_directions": null,
                          "id": "seti_1PIZcVEMUa1BUwGIBxCdlEUa",
                          "last_setup_error": null,
                          "latest_attempt": "setatt_1PIZd1EMUa1BUwGII4tpYOI3",
                          "livemode": false,
                          "mandate": null,
                          "metadata": {},
                          "next_action": null,
                          "object": "setup_intent",
                          "on_behalf_of": null,
                          "payment_method": "pm_1PIZd0EMUa1BUwGIMUMzYd36",
                          "payment_method_configuration_details": null,
                          "payment_method_options": {
                            "card": {
                              "mandate_options": null,
                              "network": null,
                              "request_three_d_secure": "automatic"
                            }
                          },
                          "payment_method_types": [
                            "card"
                          ],
                          "single_use_mandate": null,
                          "status": "succeeded",
                          "usage": "off_session"
                        }
        """
        response = Response()

        try:
            read_setupintent_response = stripe.SetupIntent.retrieve(setupintent_id)
            response.success = True if ("id" in read_setupintent_response) else False

            if (response.success):
                response.response = read_setupintent_response

        except Exception as e:
            response.message = str(e)

        return response

    def create_sub_account(self, subaccount: SubAccount) -> Response:
        """
            Creates a sub account in stripe connect, this account can be used to sell products and send payout to its bank account
            Args:
                subaccount: a Tutor account
            Returns:
                response: a Response object
                    response.response: a full stripe sub account object
                    {
                        "business_profile": {
                            "annual_revenue": null,
                            "estimated_worker_count": null,
                            "mcc": null,
                            "name": null,
                            "product_description": null,
                            "support_address": null,
                            "support_email": null,
                            "support_phone": null,
                            "support_url": null,
                            "url": null
                        },
                        "business_type": "individual",
                        "capabilities": {},
                        "charges_enabled": false,
                        "company": {
                            "address": {
                            "city": null,
                            "country": "US",
                            "line1": null,
                            "line2": null,
                            "postal_code": null,
                            "state": null
                            },
                            "directors_provided": true,
                            "executives_provided": true,
                            "name": null,
                            "owners_provided": true,
                            "tax_id_provided": false,
                            "verification": {
                            "document": {
                                "back": null,
                                "details": null,
                                "details_code": null,
                                "front": null
                            }
                            }
                        },
                        "controller": {
                            "fees": {
                            "payer": "account"
                            },
                            "is_controller": true,
                            "losses": {
                            "payments": "stripe"
                            },
                            "requirement_collection": "stripe",
                            "stripe_dashboard": {
                            "type": "full"
                            },
                            "type": "application"
                        },
                        "country": "US",
                        "created": 1716385461,
                        "default_currency": "usd",
                        "details_submitted": false,
                        "email": "bryan@test.com",
                        "external_accounts": {
                            "data": [
                            {
                                "account": "acct_1PJFSqCtt3heLqqB",
                                "account_holder_name": "Bryan ",
                                "account_holder_type": "individual",
                                "account_type": null,
                                "available_payout_methods": [
                                "standard"
                                ],
                                "bank_name": "STRIPE TEST BANK",
                                "country": "US",
                                "currency": "usd",
                                "default_for_currency": true,
                                "fingerprint": "JEQmPpZCblc68p5Q",
                                "future_requirements": {
                                "currently_due": [],
                                "errors": [],
                                "past_due": [],
                                "pending_verification": []
                                },
                                "id": "ba_1PJFSqCtt3heLqqBfKXCnlQ5",
                                "last4": "6789",
                                "metadata": {},
                                "object": "bank_account",
                                "requirements": {
                                "currently_due": [],
                                "errors": [],
                                "past_due": [],
                                "pending_verification": []
                                },
                                "routing_number": "110000000",
                                "status": "new"
                            }
                            ],
                            "has_more": false,
                            "object": "list",
                            "total_count": 1,
                            "url": "/v1/accounts/acct_1PJFSqCtt3heLqqB/external_accounts"
                        },
                        "future_requirements": {
                            "alternatives": [],
                            "current_deadline": null,
                            "currently_due": [],
                            "disabled_reason": null,
                            "errors": [],
                            "eventually_due": [],
                            "past_due": [],
                            "pending_verification": []
                        },
                        "id": "acct_1PJFSqCtt3heLqqB",
                        "metadata": {},
                        "object": "account",
                        "payouts_enabled": false,
                        "requirements": {
                            "alternatives": [],
                            "current_deadline": null,
                            "currently_due": [
                            "business_profile.product_description",
                            "business_profile.support_phone",
                            "business_profile.url",
                            "tos_acceptance.date",
                            "tos_acceptance.ip"
                            ],
                            "disabled_reason": "requirements.past_due",
                            "errors": [],
                            "eventually_due": [
                            "business_profile.product_description",
                            "business_profile.support_phone",
                            "business_profile.url",
                            "tos_acceptance.date",
                            "tos_acceptance.ip"
                            ],
                            "past_due": [
                            "tos_acceptance.date",
                            "tos_acceptance.ip"
                            ],
                            "pending_verification": []
                        },
                        "settings": {
                            "bacs_debit_payments": {
                            "display_name": null,
                            "service_user_number": null
                            },
                            "branding": {
                            "icon": null,
                            "logo": null,
                            "primary_color": null,
                            "secondary_color": null
                            },
                            "card_issuing": {
                            "tos_acceptance": {
                                "date": null,
                                "ip": null
                            }
                            },
                            "card_payments": {
                            "decline_on": {
                                "avs_failure": true,
                                "cvc_failure": true
                            },
                            "statement_descriptor_prefix": null,
                            "statement_descriptor_prefix_kana": null,
                            "statement_descriptor_prefix_kanji": null
                            },
                            "dashboard": {
                            "display_name": null,
                            "timezone": "Etc/UTC"
                            },
                            "invoices": {
                            "default_account_tax_ids": null
                            },
                            "payments": {
                            "statement_descriptor": null,
                            "statement_descriptor_kana": null,
                            "statement_descriptor_kanji": null
                            },
                            "payouts": {
                            "debit_negative_balances": true,
                            "schedule": {
                                "delay_days": 2,
                                "interval": "daily"
                            },
                            "statement_descriptor": null
                            },
                            "sepa_debit_payments": {}
                        },
                        "tos_acceptance": {
                            "date": null,
                            "ip": null,
                            "user_agent": null
                        },
                        "type": "standard"
                        }
        """
        response = Response()

        try:
            stripe_subaccount_response = stripe.Account.create(
                email=subaccount.email,
                country=subaccount.country,
                business_type=subaccount.business_type,
                type=subaccount.type
            )

            response.success = True if ("id" in stripe_subaccount_response) else False

            if (response.success):
                response.response = stripe_subaccount_response

        except Exception as e:
            response.message = str(e)

        return response

    def create_subaccount_onboarding_link(self, subaccount_id: str) -> Response:
        """
            Creates an onboarding link for a sub account, so the owner could enter his bank account
            Args:
                subaccount_id: a stripe sub account id
            Returns:
                response:
                    response.response: 
                        {
                            "object": "account_link",
                            "created": 1680577733,
                            "expires_at": 1680578033,
                            "url": "https://connect.stripe.com/setup/c/acct_1Mt0CORHFI4mz9Rw/TqckGNUHg2mG"
                        }
        """
        response = Response()

        try:
            stripe_onboarding_link_response = stripe.AccountLink.create(
                account=subaccount_id,
                type="account_onboarding",
                refresh_url=environ["BASE_URL"],
                return_url=environ["BASE_URL"]
            )
            response.success = True if ("created" in stripe_onboarding_link_response) else False

            if (response.success):
                response.response = stripe_onboarding_link_response

        except Exception as e:
            response.message = str(e)

        return response

    def intern_transfer_to_subaccount(self, subaccount_id: str, amount: int, currency: str) -> Response:
        """
            Makes a money transfer from the main stripe account to a subaccount
            Args:
                subaccount_id: a stripe sub account id
                amount: amount in cents to transfer
                currency: currency to transfer (ex: usd)
            Returns:
                - response:
                    response.response: 
                    {
                        "amount": 200,
                        "amount_reversed": 0,
                        "balance_transaction": "txn_1PJGgKEMUa1BUwGIo3yZQZS1",
                        "created": 1716390140,
                        "currency": "usd",
                        "description": null,
                        "destination": "acct_1PJGCC2QKjENfsH3",
                        "destination_payment": "py_1PJGgK2QKjENfsH3naV8jPLU",
                        "id": "tr_1PJGgKEMUa1BUwGIH8QGU87W",
                        "livemode": false,
                        "metadata": {},
                        "object": "transfer",
                        "reversals": {
                            "data": [],
                            "has_more": false,
                            "object": "list",
                            "total_count": 0,
                            "url": "/v1/transfers/tr_1PJGgKEMUa1BUwGIH8QGU87W/reversals"
                        },
                        "reversed": false,
                        "source_transaction": null,
                        "source_type": "card",
                        "transfer_group": null
                        }
        """
        response = Response()

        try:
            transfer_response = stripe.Transfer.create(
                amount=amount,
                currency=currency,
                destination=subaccount_id
            )

            response.success = True if ("id" in transfer_response) else False

            if (response.success):
                response.response = transfer_response

        except Exception as e:
            response.message = str(e)

        return response

    def create_payout(self, account_id: str, amount: int, currency: str) -> Response:
        """
            Creates and send a payout to the default's bank account from the stripe account
            Args:
                account_id: a stripe account id
                amount: amount in cents to transfer
                currency: currency to transfer (ex: usd)
            Returns:
                response:
                    response.response:
                    {
                        "amount": 200,
                        "application_fee": null,
                        "application_fee_amount": null,
                        "arrival_date": 1716336000,
                        "automatic": false,
                        "balance_transaction": "txn_1PJGxi2QKjENfsH3mqm0DVyU",
                        "created": 1716391217,
                        "currency": "usd",
                        "description": null,
                        "destination": "ba_1PJGGS2QKjENfsH3Z2DrXrBx",
                        "failure_balance_transaction": null,
                        "failure_code": null,
                        "failure_message": null,
                        "id": "po_1PJGxh2QKjENfsH31vdddZoG",
                        "livemode": false,
                        "metadata": {},
                        "method": "standard",
                        "object": "payout",
                        "original_payout": null,
                        "reconciliation_status": "not_applicable",
                        "reversed_by": null,
                        "source_type": "card",
                        "statement_descriptor": null,
                        "status": "pending",
                        "type": "bank_account"
                    }
        """
        response = Response()

        try:
            payout_response = stripe.Payout.create(
                amount=amount,
                currency=currency,
                stripe_account=account_id
            )
            response.success = True if ("id" in payout_response) else False

            if (response.success):
                response.response = payout_response

        except Exception as e:
            response.message = str(e)

        return response

    def create_an_invoice(self, customer_id: str,  reference: str, coupon_id: str = None) -> Response:
        """
            Creates an invoice in stripe, its necessary to charge a customer
            Args:
                coupon_id: a stripe coupon id to apply
                reference: a text to reference the invoice
                customer_id: the stripe customer id to charge

            Returns:
                response.response = {
                      "id": "in_1MtHbELkdIwHu7ixl4OzzPMv",
                      "object": "invoice",
                      "account_country": "US",
                      "account_name": "Stripe Docs",
                      "account_tax_ids": null,
                      "amount_due": 0,
                      "amount_paid": 0,
                      "amount_remaining": 0,
                      "amount_shipping": 0,
                      "application": null,
                      "application_fee_amount": null,
                      "attempt_count": 0,
                      "attempted": false,
                      "auto_advance": false,
                      "automatic_tax": {
                        "enabled": false,
                        "liability": null,
                        "status": null
                      },
                      "billing_reason": "manual",
                      "charge": null,
                      "collection_method": "charge_automatically",
                      "created": 1680644467,
                      "currency": "usd",
                      "custom_fields": null,
                      "customer": "cus_NeZwdNtLEOXuvB",
                      "customer_address": null,
                      "customer_email": "jennyrosen@example.com",
                      "customer_name": "Jenny Rosen",
                      "customer_phone": null,
                      "customer_shipping": null,
                      "customer_tax_exempt": "none",
                      "customer_tax_ids": [],
                      "default_payment_method": null,
                      "default_source": null,
                      "default_tax_rates": [],
                      "description": null,
                      "discount": null,
                      "discounts": [],
                      "due_date": null,
                      "ending_balance": null,
                      "footer": null,
                      "from_invoice": null,
                      "hosted_invoice_url": null,
                      "invoice_pdf": null,
                      "issuer": {
                        "type": "self"
                      },
                      "last_finalization_error": null,
                      "latest_revision": null,
                      "lines": {
                        "object": "list",
                        "data": [],
                        "has_more": false,
                        "total_count": 0,
                        "url": "/v1/invoices/in_1MtHbELkdIwHu7ixl4OzzPMv/lines"
                      },
                      "livemode": false,
                      "metadata": {},
                      "next_payment_attempt": null,
                      "number": null,
                      "on_behalf_of": null,
                      "paid": false,
                      "paid_out_of_band": false,
                      "payment_intent": null,
                      "payment_settings": {
                        "default_mandate": null,
                        "payment_method_options": null,
                        "payment_method_types": null
                      },
                      "period_end": 1680644467,
                      "period_start": 1680644467,
                      "post_payment_credit_notes_amount": 0,
                      "pre_payment_credit_notes_amount": 0,
                      "quote": null,
                      "receipt_number": null,
                      "rendering_options": null,
                      "shipping_cost": null,
                      "shipping_details": null,
                      "starting_balance": 0,
                      "statement_descriptor": null,
                      "status": "draft",
                      "status_transitions": {
                        "finalized_at": null,
                        "marked_uncollectible_at": null,
                        "paid_at": null,
                        "voided_at": null
                      },
                      "subscription": null,
                      "subtotal": 0,
                      "subtotal_excluding_tax": 0,
                      "tax": null,
                      "test_clock": null,
                      "total": 0,
                      "total_discount_amounts": [],
                      "total_excluding_tax": 0,
                      "total_tax_amounts": [],
                      "transfer_data": null,
                      "webhooks_delivered_at": 1680644467
                    }
        """
        response = Response()

        try:
            discounts = [{
                "coupon": coupon_id
            }] if (coupon_id is not None) else []
            invoice_response = stripe.Invoice.create(
                customer=customer_id,
                description=reference,
                discounts=discounts
            )
            response.success = True if ("id" in invoice_response) else False
            if (response.success):
                response.response = invoice_response

        except Exception as e:
            response.message = str(e)

        return response

    def create_an_invoice_item(self, customer_id: str, invoice_id: str, amount: int) -> Response:
        """
            Creates an invoice amount and associate it to a previous created invoice
            Args:
                amount: invoice's price in cents
                invoice_id: an invoice id of an invoice to associate
                customer_id: the customer id of the customer who must pay the invoice
            Returns:
                response.response = {
                      "id": "ii_1MtGUtLkdIwHu7ixBYwjAM00",
                      "object": "invoiceitem",
                      "amount": 1099,
                      "currency": "usd",
                      "customer": "cus_NeZei8imSbMVvi",
                      "date": 1680640231,
                      "description": "T-shirt",
                      "discountable": true,
                      "discounts": [],
                      "invoice": null,
                      "livemode": false,
                      "metadata": {},
                      "period": {
                        "end": 1680640231,
                        "start": 1680640231
                      },
                      "plan": null,
                      "price": {
                        "id": "price_1MtGUsLkdIwHu7ix1be5Ljaj",
                        "object": "price",
                        "active": true,
                        "billing_scheme": "per_unit",
                        "created": 1680640229,
                        "currency": "usd",
                        "custom_unit_amount": null,
                        "livemode": false,
                        "lookup_key": null,
                        "metadata": {},
                        "nickname": null,
                        "product": "prod_NeZe7xbBdJT8EN",
                        "recurring": null,
                        "tax_behavior": "unspecified",
                        "tiers_mode": null,
                        "transform_quantity": null,
                        "type": "one_time",
                        "unit_amount": 1099,
                        "unit_amount_decimal": "1099"
                      },
                      "proration": false,
                      "quantity": 1,
                      "subscription": null,
                      "tax_rates": [],
                      "test_clock": null,
                      "unit_amount": 1099,
                      "unit_amount_decimal": "1099"
                    }
        """
        response = Response()

        try:
            invoice_item_response = stripe.InvoiceItem.create(
                invoice=invoice_id,
                customer=customer_id,
                amount=amount
            )
            response.success = True if ("id" in invoice_item_response) else False
            if (response.success):
                response.response = invoice_item_response

        except Exception as e:
            response.message = str(e)

        return response

    def pay_an_invoice(self, invoice_id: str) -> Response:
        """
            Pay an invoice by charge the amount to the customer
            Args:
                invoice_id: the stripe invoice id
            Returns:
                response.response
        """
        response = Response()

        try:
            pay_response = stripe.Invoice.pay(invoice_id)
            response.success = True if ("id" in pay_response) else False

            if (response.success):
                response.response = pay_response

        except Exception as e:
            response.message = e

        return response

    def create_coupon(self, coupon: Coupon) -> Response:
        """
            Creates a coupon in stripe
            Args:
                coupon: a full coupon object
            Returns:
                response.response = {
                    "id": "jMT0WJUD",
                    "object": "coupon",
                    "amount_off": null,
                    "created": 1678037688,
                    "currency": null,
                    "duration": "repeating",
                    "duration_in_months": 3,
                    "livemode": false,
                    "max_redemptions": null,
                    "metadata": {},
                    "name": null,
                    "percent_off": 25.5,
                    "redeem_by": null,
                    "times_redeemed": 0,
                    "valid": true
                }
        """
        response = Response()

        try:
            coupon_response = stripe.Coupon.create(
                duration=coupon.duration,
                percent_off=coupon.percent_off,
                amount_off=coupon.amount_off,
                currency=coupon.currency,
                duration_in_months=coupon.duration_in_months
            )

            response.success = True if ("id" in coupon_response) else False

            if (response.success):
                response.response = coupon_response
        except Exception as e:
            response.message = e

        return response

    def delete_coupon_by_id(self, coupon_id: str) -> Response:
        """
            Deletes a coupon in stripe. it does not affect any customers
            who have already applied the coupon;
            it means that new customers can’t redeem the coupon.
            Args:
                coupon_id: the coupon's id
            Returns:
                response
        """
        response = Response()

        try:
            stripe_response = stripe.Coupon.delete(coupon_id)
            response.success = True if ("id" in stripe_response) else False
        except Exception as e:
            response.message = e

        return response

    def apply_coupon_to_subscription(self, subscription_id: str, coupon_id: str) -> Response:
        """
            Applies a discount coupon to an active subscription
            Args:
                coupon_id: the coupon's id
                subscription_id: a stripe subscription id
            Returns:
                response: A response object
        """
        response = Response()

        try:
            update_subscription_response = stripe.Subscription.modify(
                subscription_id,
                discounts=[{
                        "coupon": coupon_id
                    }
                ]
            )
            response.success = True if ("id" in update_subscription_response) else False
        except Exception as e:
            response.message = str(e)

        return response
