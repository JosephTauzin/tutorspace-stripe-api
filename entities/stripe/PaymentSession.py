from pydantic import BaseModel


class PaymentSession(BaseModel):
    status: str
    payment_url: str
