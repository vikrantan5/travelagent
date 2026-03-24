from pydantic import BaseModel
from typing import Optional


class UserPlannerStatus(BaseModel):
    user_id: str
    has_used_free_planner: bool
    total_planners_created: int
    is_premium: bool


class PaymentCheckRequest(BaseModel):
    user_id: str


class PaymentCheckResponse(BaseModel):
    can_create_planner: bool
    requires_payment: bool
    message: str


class PaymentInitiateRequest(BaseModel):
    user_id: str
    plan_type: str  # "monthly" or "yearly" or "lifetime"
    amount: int


class PaymentInitiateResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    razorpay_key_id: str


class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    user_id: str


class PaymentVerificationResponse(BaseModel):
    success: bool
    message: str
