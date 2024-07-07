from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime


class StudentUser(BaseModel):
    id: str = ""
    uid: str = ""
    ParentName: str = ""
    name: str = ""
    authProvider: str = ""
    email: str = ""
    Type: str = ""
    Test1: str = ""
    Test2: str = ""
    Test3: str = ""
    Test4: str = ""
    Test5: str = ""
    Test6: str = ""
    Test7: str = ""
    Test8: str = ""
    Test9: str = ""
    Test10: str = ""
    Test1ACT: str = ""
    Test2ACT: str = ""
    Test3ACT: str = ""
    Test4ACT: str = ""
    Test5ACT: str = ""
    Test6ACT: str = ""
    Test7ACT: str = ""
    Test8ACT: str = ""
    Test9ACT: str = ""
    Test10ACT: str = ""
    DiagnosticsTestResults: str = ""
    assignmentsArc: str = ""
    assignmentsDone: str = ""
    QuizResults: str = ""
    topics: str = ""
    ClassDate: Union[datetime | str] = ""
    NextMeetingDate: Union[datetime | str] = ""
    Notepad: str = ""
    assignments: str = ""
    HistMeetingTimes: List[datetime] = []
    HistMeetingTimesEnd: List[datetime] = []
    Tutor: str = ""
    Test: str = ""
    Improvement: str = ""
    PhoneNumber: str = ""
    CompanyCode: str = ""
    ConnectedAccountCreated: bool = False
    StartTime: Union[datetime | str] = ""
    DisableService: bool = False
    Admin: bool = False

    country: str = "US"
    stripe_customer_id: str = ""
    stripe_subaccount_id: str = ""
    company_type: str = ""
    setup_intent_id: str = ""
    has_default_payment_method: bool = False
    last_payout_date: Optional[datetime] = None
    has_pending_discount_coupon: bool = False
    pending_discount_coupon: str = ""
