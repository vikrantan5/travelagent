from fastapi import APIRouter, HTTPException, status
from loguru import logger
from models.comparison import (
    ComparisonRequest,
    ComparisonResponse,
    ProsCons,
    BestFor,
    FinalRecommendation,
)
from config.groq_agents import GroqAgent
import json
import re

router = APIRouter(prefix="/api/compare", tags=["Destination Comparison"])

# Create a dedicated comparison agent
comparison_agent_groq = GroqAgent(
    name="Destination Comparison Expert",
    role="travel destination comparison and recommendation specialist",
    instructions=[
        "Compare two travel destinations objectively",
        "Analyze destinations across multiple criteria: budget, nightlife, luxury options, activities, family-friendliness",
        "Provide balanced pros and cons for each destination",
        "Give clear, unbiased recommendations based on different traveler profiles",
        "Consider factors like: cost of living, safety, weather, attractions, food scene, accessibility",
        "Provide practical insights and real-world considerations",
        "Be concise but thorough",
        "Return output in valid JSON format only",
    ],
    temperature=0.3,
    max_tokens=4096,
)


@router.post(
    "/",
    response_model=ComparisonResponse,
    summary="Compare Two Destinations",
    description="Compare two travel destinations and get a detailed analysis with pros, cons, and recommendations",
)
async def compare_destinations(request: ComparisonRequest) -> ComparisonResponse:
    """
    Compare two destinations and provide detailed analysis.

    Args:
        request: Comparison request with two destinations and user preferences

    Returns:
        ComparisonResponse: Detailed comparison with pros, cons, and recommendations
    """
    try:
        logger.info(f"Comparing destinations: {request.place_1} vs {request.place_2}")

        prompt = f"""
Compare these two travel destinations and provide a comprehensive analysis:

Place 1: {request.place_1}
Place 2: {request.place_2}
User Preferences: {request.user_preferences or 'Not specified'}
Budget: {request.budget}
Travel Style: {request.travel_style}

Provide a detailed comparison in the following JSON format:

{{
    "place_1": "{request.place_1}",
    "place_2": "{request.place_2}",
    "best_for": {{
        "budget": "Place name that's better for budget travelers",
        "nightlife": "Place name with better nightlife",
        "luxury_honeymoon": "Place name better for luxury honeymoons",
        "water_sports": "Place name better for water sports",
        "family_trip": "Place name better for family trips"
    }},
    "pros_cons": {{
        "{request.place_1}": {{
            "pros": ["List of 4-5 specific advantages"],
            "cons": ["List of 3-4 specific disadvantages"]
        }},
        "{request.place_2}": {{
            "pros": ["List of 4-5 specific advantages"],
            "cons": ["List of 3-4 specific disadvantages"]
        }}
    }},
    "final_recommendation": {{
        "best_option": "Place name (choose one)",
        "reason": "Clear, concise explanation (2-3 sentences) of why this place is recommended based on the comparison"
    }}
}}

Return ONLY the JSON object, no other text or markdown.
"""

        response = await comparison_agent_groq.arun(prompt)
        logger.info(f"Received comparison response: {response[:300]}...")

        # Extract JSON from response
        try:
            # Try to find JSON object in response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                comparison_data = json.loads(json_str)

                # Validate and create response
                return ComparisonResponse(
                    place_1=comparison_data["place_1"],
                    place_2=comparison_data["place_2"],
                    best_for=BestFor(**comparison_data["best_for"]),
                    pros_cons={
                        place: ProsCons(**data)
                        for place, data in comparison_data["pros_cons"].items()
                    },
                    final_recommendation=FinalRecommendation(
                        **comparison_data["final_recommendation"]
                    ),
                )
            else:
                raise ValueError("No JSON object found in response")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing comparison response: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse comparison response: {str(e)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing destinations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare destinations: {str(e)}",
        )
