from entities import Response, Coupon
from interfaces import StripeInterface
from repositories import FirestoreRepository


class CouponsDao():
    def __init__(self):
        self.collection = "coupons"
        self.stripe = StripeInterface()
        self.repository = FirestoreRepository(self.collection)

    def create_coupon(self, coupon: Coupon) -> Response:
        """
            Creates a coupon in stripe then save it in the database
            Args:
                coupon: a coupon object
            Returns:
                response
        """
        response = Response()

        try:
            insert_response = self.repository.create_object(coupon.model_dump())
            if (not insert_response.success):
                raise Exception(insert_response.message)

            response.response = Coupon.model_validate(insert_response.response)
            response.success = True
        except Exception as e:
            response.message = e

        return response

    def read_coupon_by_id(self, coupon_id: str) -> Response:
        """
            Reads a single coupon by id
            Args:
                coupon_id: The coupon id
            Returns:
                response
        """
        response = Response()

        try:
            read_response = self.repository.read_object_by_id(coupon_id)
            if (not read_response.success):
                raise Exception(read_response.message)

            response.response = Coupon.model_validate(read_response.response)
            response.success = True
        except Exception as e:
            response.message = e

        return response

    def read_active_coupons(self) -> Response:
        """
            Reads all the coupons that can be used
            Returns:
                response
        """
        response = Response()

        try:
            read_response = self.repository.read_objects_with_equal("active", True)
            if (not read_response.success):
                raise Exception(read_response.message)

            response.response_list = [Coupon.model_validate(item) for item in read_response.response_list]
            response.success = True
        except Exception as e:
            response.message = e

        return response

    def read_all_coupons(self) -> Response:
        """
            Reads all the coupons
            Returns:
                response
        """
        response = Response()

        try:
            read_response = self.repository.read_collection()
            if (not read_response.success):
                raise Exception(read_response.message)

            response.response_list = [Coupon.model_validate(item) for item in read_response.response_list]
            response.success = True
        except Exception as e:
            response.message = e

        return response
