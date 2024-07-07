from pydantic import BaseModel
from typing import Optional


class Recurring(BaseModel):  #Example: inverval=day & interval_count=3 would charge every three days.
    interval: str  #day, week, month, year
    interval_count: int


class PriceData(BaseModel):
    currency: str  #Product payment currency
    unit_amount: int  #Product amount in cents. Example 2000 would be $20.00
    recurring: Optional[Recurring] = None


class Product(BaseModel):
    name: str
    description: str
    default_price_data: Optional[PriceData] = None
