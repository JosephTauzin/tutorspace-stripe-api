from pydantic import BaseModel


class Subscription(BaseModel):
    id: str = ""
    status: str = "pending_payment"  #active, canceled, pending_payment, expired_payment, renewal_error
    quantity: int
    payment_random_id: str
    stripe_active_subscription_id: str = ""
    stripe_subscription_item_id: str = ""
    stripe_subscription_id: str
    stripe_customer_id: str
    stripe_session_id: str = ""
    local_subscription_id: str
    local_user_id: str
    start_date: float
    renewal_date: float
    is_paid: bool = False
    admin: bool
    company_type: str
    prorate_data: list = []
    pending_cancel: bool = False
