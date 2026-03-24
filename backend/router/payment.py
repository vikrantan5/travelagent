import os
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, status
from loguru import logger
import razorpay
from models.payment import (
    PaymentCheckRequest,
    PaymentCheckResponse,
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentVerificationRequest,
    PaymentVerificationResponse,
)
from repository.payment_repository import (
    get_user_planner_status,
    update_user_premium_status,
    increment_planner_count,
)

router = APIRouter(prefix="/api/payment", tags=["Payment"])

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)


@router.post(
    "/check",
    response_model=PaymentCheckResponse,
    summary="Check Payment Status",
    description="Check if user can create a planner or needs to pay",
)
async def check_payment_status(request: PaymentCheckRequest) -> PaymentCheckResponse:
    """
    Check if user can create a new planner.

    Returns:
        - can_create_planner: True if user can create planner
        - requires_payment: True if payment is required
        - message: Information message
    """
    try:
        logger.info(f"Checking payment status for user: {request.user_id}")

        user_status = await get_user_planner_status(request.user_id)

        # If user is premium, they can always create planners
        if user_status.is_premium:
            return PaymentCheckResponse(
                can_create_planner=True,
                requires_payment=False,
                message="You have premium access. Create unlimited planners!",
            )

        # If user hasn't used free planner yet
        if not user_status.has_used_free_planner:
            return PaymentCheckResponse(
                can_create_planner=True,
                requires_payment=False,
                message="You can create your first free planner!",
            )

        # User has used free planner and is not premium
        return PaymentCheckResponse(
            can_create_planner=False,
            requires_payment=True,
            message="You have used your free planner. Please upgrade to continue.",
        )

    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check payment status: {str(e)}",
        )


@router.post(
    "/initiate",
    response_model=PaymentInitiateResponse,
    summary="Initiate Payment",
    description="Initiate Razorpay payment for premium plans",
)
async def initiate_payment(
    request: PaymentInitiateRequest,
) -> PaymentInitiateResponse:
    """
    Initiate Razorpay payment for premium plans.

    Args:
        request: Payment initiation request with user_id, plan_type, and amount

    Returns:
        PaymentInitiateResponse with Razorpay order details
    """
    try:
        logger.info(
            f"Initiating payment for user: {request.user_id}, plan: {request.plan_type}"
        )

        # Create Razorpay order
        order_data = {
            "amount": request.amount * 100,  # Amount in paise
            "currency": "INR",
            "receipt": f"order_{request.user_id}_{request.plan_type}",
            "notes": {
                "user_id": request.user_id,
                "plan_type": request.plan_type,
            },
        }

        order = razorpay_client.order.create(data=order_data)
        logger.info(f"Razorpay order created: {order['id']}")

        return PaymentInitiateResponse(
            order_id=order["id"],
            amount=order["amount"],
            currency=order["currency"],
            razorpay_key_id=os.getenv("RAZORPAY_KEY_ID"),
        )

    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate payment: {str(e)}",
        )


@router.post(
    "/verify",
    response_model=PaymentVerificationResponse,
    summary="Verify Payment",
    description="Verify Razorpay payment and upgrade user to premium",
)
async def verify_payment(
    request: PaymentVerificationRequest,
) -> PaymentVerificationResponse:
    """
    Verify Razorpay payment signature and upgrade user.

    Args:
        request: Payment verification request with Razorpay IDs and signature

    Returns:
        PaymentVerificationResponse with success status
    """
    try:
        logger.info(f"Verifying payment for user: {request.user_id}")

        # Verify signature
        generated_signature = hmac.new(
            os.getenv("RAZORPAY_KEY_SECRET").encode(),
            f"{request.razorpay_order_id}|{request.razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()

        if generated_signature != request.razorpay_signature:
            logger.error("Payment signature verification failed")
            return PaymentVerificationResponse(
                success=False,
                message="Payment verification failed. Invalid signature.",
            )

        # Upgrade user to premium
        await update_user_premium_status(request.user_id, is_premium=True)
        logger.info(f"User {request.user_id} upgraded to premium")

        return PaymentVerificationResponse(
            success=True,
            message="Payment successful! You now have premium access.",
        )

    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}",
        )


@router.post(
    "/record-planner",
    summary="Record Planner Creation",
    description="Record that user has created a planner (for tracking free usage)",
)
async def record_planner_creation(user_id: str):
    """
    Record that a user has created a planner.
    Used to track free planner usage.
    """
    try:
        logger.info(f"Recording planner creation for user: {user_id}")
        await increment_planner_count(user_id)
        return {"success": True, "message": "Planner creation recorded"}

    except Exception as e:
        logger.error(f"Error recording planner creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record planner creation: {str(e)}",
        )
