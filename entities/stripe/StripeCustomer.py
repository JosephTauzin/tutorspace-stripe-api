from pydantic import BaseModel
from typing import Optional


class Address(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None


class StripeCustomer(BaseModel):
    id: Optional[str] = None
    name: str  # Customer name
    email: str  # Customer email
    phone: Optional[str] = None  #Customer phone with country code
    description: Optional[str] = None  #Customer description (can be anything)
    address: Optional[Address] = None  #Customer address object
