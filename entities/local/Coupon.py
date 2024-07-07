from pydantic import BaseModel
from typing import Optional


class Coupon(BaseModel):
    id: str = ""
    name: str
    type_: str  #percentage, amount
    active: bool = True
    currency: str = "USD"
    amount_off: Optional[int] = None
    percent_off: Optional[float] = None
    max_redemptions: int = 1
    duration: str = "once"  #can be forever, once or repeating
    duration_in_months: Optional[int] = None  #necessary if duration=repeating
    stripe_coupon_id: str = ""
