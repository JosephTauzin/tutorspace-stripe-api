from pydantic import BaseModel
from typing import Optional, List


class Membership(BaseModel):
    id: str = ""
    name: str
    description: str
    currency: str = "USD" #ISO 4217 coin code
    price: int #Price in cents
    interval: str  #day, week, month, year
    interval_count: int
    active_admin: bool = False  # Can an admin buy it?
    type_: List[str] = ["Individual"]  # Users type that can buy it
    stripe_id: str = ""  #Stripe product id to identify it in stripe platform
    stripe_price_id: str = ""  #Stripe product price id to identify it in stripe platform
    active: bool = True
