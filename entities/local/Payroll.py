from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class StudentDebt(BaseModel):
    start_hours: List[datetime]
    end_hours: List[datetime]
    hours: float
    student_id: str
    student_name: str
    student_debt: int #cents
    tutor_id: str
    tutor_name: str
    tutor_cost: int #cents
    admin_profit: int #cents
    stripe_customer_id: str = ""
    stripe_invoice_id: str = ""
    pending_onboarding: bool
    pending_coupon: Optional[str] = None
    paid: bool = False
    error: str = ""


class TutorPayout(BaseModel):
    tutor_id: str
    tutor_name: str
    tutor_payout: int #cents
    tutor_total_hours: float
    pending_onboarding: bool
    stripe_sub_account_id: str = ""
    stripe_transference_id: str = ""
    stripe_payout_id: str = ""
    paid: bool = False
    error: str = ""


class TutorNotFound(BaseModel):
    tutor_name: str
    students: List[dict]


class AdminPayout(BaseModel):
    admin_total_profit: int = 0 #cents
    admin_sub_account_id: str = ""
    admin_transference_id: str = ""
    admin_payout_id: str = ""
    pending_onboarding: bool = True
    error: str = ""


class Payroll(BaseModel):
    id: str = ""
    company_code: str
    admin_id: str
    completed: bool = False #to update
    students_charged: bool = False #to update
    tutors_paid: bool = False #to update
    admin_paid: bool = False #to update
    admin_payout: AdminPayout
    students_debt: List[StudentDebt] = []
    tutors_payout: List[TutorPayout] = []
    tutors_not_found: List[TutorNotFound] = []
    students_with_error: List = []
    error: str = ""

