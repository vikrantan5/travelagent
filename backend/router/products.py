"""
Product Recommendations Router
API endpoints for travel product recommendations
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger
from agents.product_recommendations import generate_product_recommendations


router = APIRouter(prefix="/api/products", tags=["Product Recommendations"])


class ProductRecommendationRequest(BaseModel):
    """Request model for product recommendations"""
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[int] = None
    budget: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class ProductRecommendation(BaseModel):
    """Product recommendation model"""
    name: str
    category: str
    reason: str
    price_range: str
    priority: str
    amazon_url: str


class ProductRecommendationResponse(BaseModel):
    """Response model for product recommendations"""
    success: bool
    products: List[ProductRecommendation]
    count: int


@router.post(
    "/recommendations",
    response_model=ProductRecommendationResponse,
    summary="Get Product Recommendations",
    description="Get AI-powered travel product recommendations based on trip details",
)
async def get_product_recommendations(
    request: ProductRecommendationRequest,
) -> ProductRecommendationResponse:
    """
    Generate personalized product recommendations for a trip.
    
    Args:
        request: Trip details including destination, dates, and preferences
        
    Returns:
        ProductRecommendationResponse: List of recommended products with Amazon links
    """
    try:
        logger.info(f"Generating product recommendations for destination: {request.destination}")
        
        # Convert request to dict
        trip_details = request.model_dump()
        
        # Generate recommendations
        products = generate_product_recommendations(trip_details)
        
        logger.info(f"Successfully generated {len(products)} product recommendations")
        
        return ProductRecommendationResponse(
            success=True,
            products=products,
            count=len(products)
        )
        
    except Exception as e:
        logger.error(f"Error getting product recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate product recommendations: {str(e)}",
        )
