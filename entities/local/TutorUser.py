from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime


class TutorUser(BaseModel):
    id: str = ""
    uid: str = ""
    name: str = ""
    authProvider: str = ""
    email: str = ""
    Type: str = ""
    ClassNumbersSAT: list = []
    ClassNumbersACT: list = []
    topics: str = ""
    ClassDate: Union[datetime | str] = ""
    NextMeetingDate: Union[datetime | str] = ""
    Notepad: str = ""
    assignments: str = ""
    HistMeetingTimes: List[datetime] = []
    HistMeetingTimesEnd: List[datetime] = []
    ClassACT: list = []
    Class: list = []
    Students: list = []
    ZoomLink: str = ""
    Admin: bool = False
    PhoneNumber: str = ""
    AdditionalPDFUrl: str = ""
    CompanyCode: str = ""
    ConnectedAccountCreated: bool = False
    StartTime: Union[datetime | str] = ""
    Availability: list = []
    DisableService: bool = False
    DisableBilling: bool = False

    country: str = "US"
    stripe_customer_id: str = ""
    stripe_subaccount_id: str = ""
    company_type: str = ""
    setup_intent_id: str = ""
    has_default_payment_method: bool = False
    currency: str = "USD"
    cost_per_session: int = 0 #cost in cents
    pay_per_hour: int = 0 #pay in cents
    last_payout_date: Optional[datetime] = None
    subscription_coupons_applied: list = []
    has_pending_invoice_coupon: bool = False
    pending_invoice_coupon: str = ""
