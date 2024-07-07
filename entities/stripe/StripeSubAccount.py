from pydantic import BaseModel


class Capabilities(BaseModel):
    card_payments: dict = {"requested": True}


class Controller(BaseModel):
    stripe_dashboard: dict = {"type": "none"}
    requirement_collection: str = "stripe"
    fees: dict = {"payer": "application"}


class SubAccount(BaseModel):
    id: str = ""
    email: str
    country: str = "US"
    business_type: str = "individual"
    type: str = "express"
