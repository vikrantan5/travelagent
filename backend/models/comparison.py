from pydantic import BaseModel
from typing import Dict, List


class ComparisonRequest(BaseModel):
    place_1: str
    place_2: str
    user_preferences: str = ""
    budget: str = "moderate"
    travel_style: str = "balanced"


class ProsCons(BaseModel):
    pros: List[str]
    cons: List[str]


class BestFor(BaseModel):
    budget: str
    nightlife: str
    luxury_honeymoon: str
    water_sports: str
    family_trip: str


class FinalRecommendation(BaseModel):
    best_option: str
    reason: str


class ComparisonResponse(BaseModel):
    place_1: str
    place_2: str
    best_for: BestFor
    pros_cons: Dict[str, ProsCons]
    final_recommendation: FinalRecommendation
