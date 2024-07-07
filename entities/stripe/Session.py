from pydantic import BaseModel
from typing import Optional


class LineItems(BaseModel):
    price: str  #product stripe id
    quantity: int


class Session(BaseModel):
    client_reference_id: str  # Any string to reference the payment
    customer: str  # customer stripe id
    mode: str = "subscription"  #Can be "payment" or "subscription"
    line_items: list['LineItems'] = []  #A list for the items the customer is purchasing
    payment_method_types: list = []
    discounts: Optional[list] = None
