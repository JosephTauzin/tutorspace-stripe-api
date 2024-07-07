from dao import CouponsDao, UserDao
from entities import Coupon, Response, StudentUser
from interfaces import StripeInterface
from services import MembershipService
from utils import dollars_to_cents


class CouponService():
    def __init__(self):
        self.coupon_dao = CouponsDao()
        self.stripe = StripeInterface()
        self.user_dao = UserDao()

    def create_coupon(self,
                      name: str,
                      _type: str,
                      amount_off: float,
                      max_redemptions: int,
                      duration: str,
                      duration_in_months: int
                      ) -> Response:
        """
            Creates a coupon in stripe and the database
            Returns:
        """
        response = Response()

        try:
            coupon = Coupon(
                name=name,
                max_redemptions=max_redemptions,
                duration=duration,
                type_=_type
            )

            if (amount_off <= 0 or amount_off > 100):
                raise Exception("invalid_percentage_amount")

            if (_type == "percentage"):
                coupon.percent_off = amount_off
            elif (_type == "amount"):
                coupon.amount_off = dollars_to_cents(amount_off)
            else:
                raise Exception("invalid_coupon_type")

            if (duration == "repeating"):
                coupon.duration_in_months = duration_in_months

            new_coupon_response = self.stripe.create_coupon(coupon)
            if (not new_coupon_response.success):
                raise Exception(new_coupon_response.message)

            stripe_coupon = new_coupon_response.response
            coupon.stripe_coupon_id = stripe_coupon["id"]

            insert_response = self.coupon_dao.create_coupon(coupon)
            if (not insert_response.success):
                raise Exception(insert_response.message)

            response.response = insert_response.response
            response.success = True
        except Exception as e:
            response.message = e

        return response

    def read_available_coupons(self) -> Response:
        """
            Retrieves a list of available coupons to be used
            Returns:
                response
        """
        response = Response()

        try:
            coupons_response = self.coupon_dao.read_active_coupons()
            if (not coupons_response.success):
                raise Exception(coupons_response.message)

            response.response_list = coupons_response.response_list
            response.success = True
        except Exception as e:
            response.message = e

        return response

    def apply_coupon_to_user_subscription(self, user_id: str, coupon_id: str) -> Response:
        """
            Apply a coupon to a user subscription
            Args:
                user_id:
                coupon_id:
            Returns:
                response
        """
        response = Response()

        try:
            active_subscription_response = MembershipService(user_id).read_active_membership()
            coupon_response = self.coupon_dao.read_coupon_by_id(coupon_id)

            if (not active_subscription_response.success):
                raise Exception(active_subscription_response.message)

            if (not coupon_response.success):
                raise Exception(coupon_response.message)

            active_subscriptions = active_subscription_response.response_list
            coupon: Coupon = coupon_response.response

            apply_coupon_response = Response()
            active_subscription = None
            for subscription in active_subscriptions:
                if (not subscription.pending_cancel):
                    active_subscription = subscription
                    apply_coupon_response = self.stripe.apply_coupon_to_subscription(
                        subscription.stripe_active_subscription_id,
                        coupon.stripe_coupon_id
                    )
                    if (apply_coupon_response.success):
                        self.user_dao.save_coupon_applied(user_id, coupon.id)
                        break

            response.success = apply_coupon_response.success
            response.response = {
                "coupon_applied": coupon.model_dump(),
                "subscription": active_subscription
            } if (apply_coupon_response.success) else {}
        except Exception as e:
            response.message = e

        return response

    def apply_coupon_to_student_next_invoice(self, user_id: str, coupon_id: str) -> Response:
        """
            Apply a coupon to the next user invoice
            Args:
                user_id: a local user id
                coupon_id: a local coupon id
            Returns:
        """
        response = Response()

        try:
            user_response = self.user_dao.read_user_by_id(user_id)
            coupon_response = self.coupon_dao.read_coupon_by_id(coupon_id)

            if (not user_response.success):
                raise Exception(user_response.message)

            if (not coupon_response.success):
                raise Exception(coupon_response.message)

            user: StudentUser = user_response.response["user"]
            coupon: Coupon = coupon_response.response

            if (user.Type != "student"):
                raise Exception("user_is_not_an_student")

            if (user.has_pending_discount_coupon):
                raise Exception("user_has_an_active_coupon")

            save_coupon_response = self.user_dao.save_pending_invoice_coupon(user.id, coupon.stripe_coupon_id)
            response.message = save_coupon_response.message
            response.success = save_coupon_response.success
        except Exception as e:
            response.message = e

        return response
