from entities import Response, StudentUser, TutorUser, Membership, Subscription, StripeCustomer, Session, LineItems, SubAccount
from interfaces import StripeInterface
from dao import UserDao, SubscriptionsDao
from typing import Union


class StripeService():
    def __init__(self):
        self.stripe = StripeInterface()
        self.customer_dao = UserDao()
        self.subscription_dao = SubscriptionsDao()

    def create_stripe_customer(self, user: Union[StudentUser, TutorUser]) -> Response:
        """
            Creates a customer in stripe and associate it with a local customer, it is necessary to associate the buys
            and the payment method
            Args:
                user: a local user object
            Returns:
                response: a response object with the result
                    response.response: a dict with the stripe customer id
                        { "stripe_customer_id": stripe_customer_id }
        """
        response = Response()

        try:
            # Creates a customer in stripe with the user data
            create_stripe_customer_response = self.stripe.create_customer(StripeCustomer(
                name=user.name,
                email=user.email
            ))

            if (not create_stripe_customer_response.success):
                raise Exception(create_stripe_customer_response.message)

            new_customer_dict = StripeCustomer.model_validate(create_stripe_customer_response.response)
            user.stripe_customer_id = new_customer_dict.id

            # Save the stripe customer id in the database
            save_stripe_id_response = self.customer_dao.save_stripe_customer_id(
                user.id,
                user.stripe_customer_id
            )
            if (not save_stripe_id_response.success):
                raise Exception(save_stripe_id_response.message)

            response.success = True
            response.response = {"stripe_customer_id": user.stripe_customer_id}
        except Exception as e:
            response.message = e

        return response

    def create_stripe_payment_session(self,
                                      user: Union[StudentUser, TutorUser],
                                      membership: Membership,
                                      subscription: Subscription,
                                      licences: int,
                                      discounts: list
                                      ) -> Response:
        """
            Creates a stripe payment session, so a customer could buy a product or membership
            Args:
                discounts:
                user: a local user object
                membership: a local membership object
                subscription: a local subscription object
                licences: the total number of licences to buy
            Returns:
                response: a response object
                    response.response: a dict with stripe payment session information
        """
        response = Response()

        try:
            response = self.stripe.create_payment_session(Session(
                client_reference_id=subscription.payment_random_id,
                customer=user.stripe_customer_id,
                discounts=discounts,
                line_items=[LineItems(
                    price=membership.stripe_price_id,
                    quantity=licences
                )]))

        except Exception as e:
            response.message = str(e)

        return response

    def validate_stripe_payment_session(self, subscription: Subscription) -> Response:
        """
            Validates if a payment session is successfully or expired in stripe
            Args:
                subscription: a local subscription object
            Returns:
                response: a response object
                    response.success = True/False
        """
        response = Response()

        try:
            stripe_session_response = self.stripe.read_payment_session_by_id(subscription.stripe_session_id)
            if (not stripe_session_response.success):
                raise Exception(stripe_session_response.message)

            stripe_session = stripe_session_response.response

            paid_session = {
                "payment_status": "paid",
                "status": "complete",
                "client_reference_id": subscription.payment_random_id
            }

            valid_payment = all(paid_session[key] == stripe_session[key] for key in paid_session)

            if (valid_payment):
                stripe_subscription_id = stripe_session["subscription"]
                stripe_new_subscription_response = self.stripe.read_subscription_by_id(stripe_subscription_id)

                if (not stripe_new_subscription_response.success):
                    raise Exception(stripe_new_subscription_response.message)

                stripe_new_subscription = stripe_new_subscription_response.response
                renewal_date = stripe_new_subscription["current_period_end"]
                stripe_subscription_item_id = stripe_new_subscription["items"]["data"][0]["id"]

                response = self.subscription_dao.activate_subscription(
                    subscription.id,
                    stripe_subscription_id,
                    stripe_subscription_item_id,
                    renewal_date
                )
            else:
                expired_session = {
                    "payment_status": "unpaid",
                    "status": "expired",
                    "client_reference_id": subscription.payment_random_id
                }
                expired_payment = all(expired_session[key] == stripe_session[key] for key in expired_session)

                if (expired_payment):
                    response = self.subscription_dao.expired_payment(subscription.id)

        except Exception as e:
            response.message = str(e)

        return response

    def read_stripe_active_product_information(self, subscription: Subscription) -> Response:
        """
            Reads the stripe information about a bought product
            Args:
                subscription: the local active subscription object
            Returns:
                response: a response object
                    response.response: a dict with the stripe active subscripton information
        """
        response = Response()

        try:
            response = self.stripe.read_subscription_by_id(subscription.stripe_active_subscription_id)
        except Exception as e:
            response.message = str(e)

        return response

    def update_active_product_subscription(self, subscription: Subscription, new_total_license: int) -> Response:
        """
            Updates an active product subscription locally and in stripe, it will prorate
            the amount it the needed cases
            Args:
                subscription:
                new_total_license:
            Returns:
                response: a response object
                    response.success = True/False
        """
        response = Response()

        try:
            stripe_update_subscription_response = self.stripe.update_subscription_quantity(
                subscription.stripe_active_subscription_id,
                subscription.stripe_subscription_item_id,
                new_total_license
            )

            if (not stripe_update_subscription_response.success):
                raise Exception(stripe_update_subscription_response.message)

            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def cancel_active_product_subscription(self, stripe_subscription_id: str) -> Response:
        """
            Cancels an active product subscription to stop recurring payments
            Args:
                stripe_subscription_id: the stripe active subscription id
            Returns:
                response:
                    response.success = True/False
        """
        response = Response()

        try:
            response = self.stripe.unsubscribe(stripe_subscription_id)
        except Exception as e:
            response.message = str(e)

        return response

    def create_payment_information_onboarding_link(self, user: Union[StudentUser, TutorUser]) -> Response:
        """
            Creates a stripe payment session to ask the payment information form a customer
            Args:
                user: a local user object
            Returns:
                response: a response object
        """
        response = Response()

        try:
            stripe_payment_session_response = self.stripe.create_payment_session_without_pay(Session(
                client_reference_id=user.id,
                customer=user.stripe_customer_id,
                mode="setup",
                payment_method_types=["card"]
            ))

            if (not stripe_payment_session_response.success):
                raise Exception(stripe_payment_session_response.message)

            stripe_session = stripe_payment_session_response.response
            setup_intent_id = stripe_session["setup_intent"]

            save_setup_intent_response = self.customer_dao.save_stripe_setup_intent_id(user.id, setup_intent_id)

            if (not save_setup_intent_response.success):
                raise Exception(save_setup_intent_response.message)

            response = stripe_payment_session_response

        except Exception as e:
            response.message = str(e)

        return response

    def activate_customer_payment_method(self, user: Union[StudentUser, TutorUser]) -> Response:
        """
            Set a previous saved payment method as the default for a customer,
            It is necessary, so we could use it to charge the customer easily
            Args:
                user: a local user object
            Returns:
                response: a response object
        """
        response = Response()

        try:
            setup_intent_response = self.stripe.read_setupintent(user.setup_intent_id)

            if (not setup_intent_response.success):
                raise Exception(setup_intent_response.message)

            setup_intent = setup_intent_response.response
            payment_method_id = setup_intent["payment_method"]

            activate_payment_method_response = self.stripe.update_customer_default_payment_method(
                user.stripe_customer_id,
                payment_method_id
            )

            if (not activate_payment_method_response.success):
                raise Exception(activate_payment_method_response.message)

            response = self.customer_dao.set_has_default_payment_method(user.id, True)
        except Exception as e:
            response.message = str(e)

        return response

    def create_customer_sub_account(self, user: Union[StudentUser, TutorUser]) -> Response:
        """
            Creates a stripe sub account
            It is necessary a sub account to send payouts to our customers bank accounts
            Args:
                user: a local user object
            Returns:
                response: a response object
        """
        response = Response()

        try:
            create_sub_account_response = self.stripe.create_sub_account(SubAccount(
                email=user.email,
                country=user.country
            ))

            if (not create_sub_account_response.success):
                raise Exception(create_sub_account_response.message)

            sub_account = create_sub_account_response.response
            update_user_response = self.customer_dao.save_stripe_sub_account_id(user.id, sub_account["id"])

            if (not update_user_response.success):
                raise Exception(update_user_response.message)

            response.success = True
            response.response = sub_account
        except Exception as e:
            response.message = str(e)

        return response

    def create_sub_account_onboarding_link(self, sub_account_id: str) -> Response:
        """
            Creates an onboarding link for a sub account (Tutor) saves his bank information
            Args:
                sub_account_id: a stripe sub account id
            Returns:
                response: a response object
        """
        response = Response()

        try:
            onboarding_link_response = self.stripe.create_subaccount_onboarding_link(sub_account_id)

            if (not onboarding_link_response.success):
                raise Exception(onboarding_link_response.message)

            response.success = True
            response.response = {
                "sub_account_id": sub_account_id,
                "onboarding_link": onboarding_link_response.response["url"]
            }

        except Exception as e:
            response.message = str(e)

        return response

    def create_complete_invoice(self, customer_id: str, amount: int, reference: str, coupon_id: str = None) -> Response:
        """
            Creates an invoice and an invoice item
            Args:
                coupon_id: a stripe coupon id
                reference: a custom string to reference the invoice
                customer_id: a stripe customer id
                amount: the invoice price amount in dollars
            Returns:
                response.response =
        """
        response = Response()

        try:
            new_invoice_response = self.stripe.create_an_invoice(customer_id, reference, coupon_id)
            if (not new_invoice_response.success):
                raise Exception(new_invoice_response.message)

            invoice = new_invoice_response.response

            new_invoice_item_response = self.stripe.create_an_invoice_item(customer_id, invoice["id"], amount)
            if (not new_invoice_item_response.success):
                raise Exception(new_invoice_item_response)

            response.success = True
            response.response = invoice
        except Exception as e:
            response.message = str(e)

        return response

    def charge_invoice(self, invoice_id: str) -> Response:
        """
            Charges the invoice to the customer associated to it
            Args:
                invoice_id:
            Returns:
        """
        response = Response()

        try:
            charge_response = self.stripe.pay_an_invoice(invoice_id)
            if (not charge_response.success):
                raise Exception(charge_response.message)

            response.success = True
        except Exception as e:
            response.message = str(e)

        return response

    def transfer_amount_to_sub_account(self, sub_account_id: str, amount: int) -> Response:
        """
            Makes a stripe internal transfer from the main account to a tutor sub account
            So we could create a payout later to that sub account
            Args:
                sub_account_id:
                amount:
            Returns:
        """
        response = Response()

        try:
            response = self.stripe.intern_transfer_to_subaccount(sub_account_id, amount, currency="USD")
        except Exception as e:
            response.message = str(e)

        return response

    def payout_to_tutor_sub_account(self, sub_account_id: str, amount: int) -> Response:
        """
            Executes a payout to the default bank account from a tutor's sub account
            Args:
                sub_account_id: tutor's sub account id
                amount: the amount in cents
            Returns:
        """
        response = Response()

        try:
            response = self.stripe.create_payout(sub_account_id, amount, currency="USD")
        except Exception as e:
            response.message = str(e)

        return response

    def validate_stripe_payment_session_hook(self, stripe_session_event) -> Response:
        """
            Validates if a payment session is successfully or expired in stripe
            Args:
                stripe_session_event:
            Returns:
                response: a response object
                    response.success = True/False
        """
        response = Response()

        try:
            payment_random_id = stripe_session_event["client_reference_id"]

            subscription_response = self.subscription_dao.read_subscription_by_payment_random_id(payment_random_id)
            if (not subscription_response.success or len(subscription_response.response_list) == 0):
                raise Exception("no_valid_subscription")

            subscription: Subscription = subscription_response.response_list[0]

            paid_session = {
                "payment_status": "paid",
                "status": "complete",
                "client_reference_id": subscription.payment_random_id
            }

            valid_payment = all(paid_session[key] == stripe_session_event[key] for key in paid_session)

            if (valid_payment):
                stripe_subscription_id = stripe_session_event["subscription"]
                stripe_new_subscription_response = self.stripe.read_subscription_by_id(stripe_subscription_id)

                if (not stripe_new_subscription_response.success):
                    raise Exception(stripe_new_subscription_response.message)

                stripe_new_subscription = stripe_new_subscription_response.response
                renewal_date = stripe_new_subscription["current_period_end"]
                stripe_subscription_item_id = stripe_new_subscription["items"]["data"][0]["id"]

                response = self.subscription_dao.activate_subscription(
                    subscription.id,
                    stripe_subscription_id,
                    stripe_subscription_item_id,
                    renewal_date
                )

        except Exception as e:
            response.message = str(e)

        return response

    def activate_customer_payment_method_hook(self, stripe_session_event) -> Response:
        """
            Set a previous saved payment method as the default for a customer,
            It is necessary, so we could use it to charge the customer easily
            Args:
                stripe_session_event:
            Returns:
                response: a response object
        """
        response = Response()

        try:
            client_reference_id = stripe_session_event["client_reference_id"]
            setup_intent_id = stripe_session_event["setup_intent"]
            stripe_customer_id = stripe_session_event["customer"]
            setup_intent_response = self.stripe.read_setupintent(setup_intent_id)

            if (not setup_intent_response.success):
                raise Exception(setup_intent_response.message)

            setup_intent = setup_intent_response.response
            payment_method_id = setup_intent["payment_method"]

            activate_payment_method_response = self.stripe.update_customer_default_payment_method(
                stripe_customer_id,
                payment_method_id
            )

            if (not activate_payment_method_response.success):
                raise Exception(activate_payment_method_response.message)

            self.customer_dao.save_stripe_setup_intent_id(client_reference_id, setup_intent_id)
            response = self.customer_dao.set_has_default_payment_method(client_reference_id, True)
        except Exception as e:
            response.message = str(e)

        return response

    def manage_webhook(self, event):
        """
            Manages the webhook events
            Args:
                event: a stripe event
        """
        print(event)
        if (event.type == "checkout.session.completed"):
            data = event.data.object

            #new user subscription
            if (data.mode == "subscription"):
                self.validate_stripe_payment_session_hook(data)

            #new user payment method
            elif (data.mode == "setup"):
                self.activate_customer_payment_method_hook(data)

        else:
            print('Unhandled event type {}'.format(event.type))
