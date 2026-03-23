"""
Groq-based AI Agent System for TripCraft
Replaces OpenRouter/OpenAI with Groq LLM
"""

from groq import Groq
import os
import json
from typing import List, Dict, Any, Optional
from loguru import logger

class GroqAgent:
    """Base class for Groq-powered agents"""
    
    def __init__(
        self,
        name: str,
        role: str,
        instructions: List[str],
        model: str = "llama3-70b-8192",
        temperature: float = 0.3,
        max_tokens: int = 8096
    ):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def _build_system_prompt(self) -> str:
        """Build system prompt from instructions"""
        prompt = f"You are {self.name}, a {self.role}."
        prompt += "INSTRUCTIONS:"
        prompt += "".join(self.instructions)
        return prompt
    
    async def arun(self, user_message: str, context: Optional[str] = None) -> str:
        """Run agent with user message"""
        try:
            messages = [
                {"role": "system", "content": self._build_system_prompt()}
            ]
            
            if context:
                messages.append({"role": "system", "content": f"CONTEXT:{context}"})
            
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"[{self.name}] Processing request with {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"[{self.name}] Response generated successfully")
            
            return content
            
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            # Try fallback model
            if self.model == "llama3-70b-8192":
                logger.info(f"[{self.name}] Trying fallback model: mixtral-8x7b-32768")
                self.model = "mixtral-8x7b-32768"
                return await self.arun(user_message, context)
            raise


# Destination Agent
destination_agent_groq = GroqAgent(
    name="Destination Explorer",
    role="destination research specialist",
    instructions=[
        "Research and provide detailed information about travel destinations",
        "Focus on attractions, activities, and experiences that match user preferences",
        "Provide practical information: opening hours, entrance fees, typical visit duration",
        "Organize information logically with main attractions first",
        "Include hidden gems and local experiences",
        "Consider seasonality and current events",
        "Provide at least 10 detailed attraction recommendations",
        "Include cultural context and local tips",
        "Format output in clear Markdown with emojis"
    ],
    temperature=0.3
)

# Flight Search Agent
flight_agent_groq = GroqAgent(
    name="Flight Search Assistant",
    role="flight search and comparison specialist",
    instructions=[
        "Analyze flight requirements from user travel plans",
        "Provide realistic flight recommendations with routes, times, and estimated prices",
        "Consider both direct and connecting flights",
        "Include major airlines and budget carriers",
        "Provide detailed timing (departure, arrival, duration, layovers)",
        "Estimate realistic pricing based on route and season",
        "Recommend at least 5 flight options",
        "Include baggage allowances and booking tips",
        "Format with clear sections and pricing breakdown"
    ],
    temperature=0.2
)

# Hotel Search Agent
hotel_agent_groq = GroqAgent(
    name="Hotel Search Assistant",
    role="accommodation research specialist",
    instructions=[
        "Research and recommend hotels based on user preferences",
        "Consider budget, location, amenities, and travel style",
        "Provide at least 5 detailed hotel recommendations",
        "Include pricing estimates, ratings, and key amenities",
        "Consider location relative to attractions",
        "Include family-friendly features if applicable",
        "Provide booking tips and cancellation policies",
        "Organize by price range and value",
        "Format with clear sections and highlight special features"
    ],
    temperature=0.3
)

# Dining Agent
dining_agent_groq = GroqAgent(
    name="Culinary Guide",
    role="dining and food experience specialist",
    instructions=[
        "Research and recommend restaurants and food experiences",
        "Match recommendations to cuisine preferences and dietary restrictions",
        "Provide at least 5 restaurant recommendations",
        "Include price ranges, popular dishes, and ambiance descriptions",
        "Consider meal timing and reservation requirements",
        "Highlight local specialties and must-try dishes",
        "Include food markets and culinary experiences",
        "Provide local food customs and etiquette tips",
        "Format with emojis and clear price indicators ($, $$, $$$)"
    ],
    temperature=0.3
)

# Budget Agent
budget_agent_groq = GroqAgent(
    name="Budget Optimizer",
    role="travel budget optimization specialist",
    instructions=[
        "Calculate comprehensive travel costs",
        "Break down budget by category: transport, accommodation, food, activities",
        "Identify areas where budget can be optimized",
        "Suggest cost-saving alternatives that maintain experience quality",
        "Include hidden costs and contingencies",
        "Provide comparison between budget-friendly and premium options",
        "Calculate daily spending estimates",
        "Format with clear tables and total breakdowns",
        "Highlight best value recommendations"
    ],
    temperature=0.2
)

# Itinerary Agent
itinerary_agent_groq = GroqAgent(
    name="Itinerary Planner",
    role="day-by-day itinerary creation specialist",
    instructions=[
        "Create detailed, realistic day-by-day itineraries",
        "Consider travel time between locations",
        "Balance activities with rest periods based on travel pace",
        "Include specific timing for each activity",
        "Incorporate flight, hotel, and dining recommendations",
        "Add morning, afternoon, and evening activities",
        "Include backup options for weather contingencies",
        "Provide practical tips for each day",
        "Format with clear day headers and timeline structure",
        "Include emoji indicators for activity types"
    ],
    temperature=0.3
)

# Product Recommendation Agent (NEW)
product_agent_groq = GroqAgent(
    name="Travel Essentials Advisor",
    role="travel product recommendation specialist",
    instructions=[
        "Recommend essential travel products based on destination and activities",
        "Consider weather, terrain, and cultural requirements",
        "Suggest 8-10 practical items travelers should bring",
        "Include categories: clothing, gadgets, accessories, health & safety",
        "Provide specific product recommendations (not generic categories)",
        "Explain why each product is needed for this specific trip",
        "Include approximate price ranges",
        "Prioritize items by importance (must-have vs nice-to-have)",
        "Format with product name, category, reason, and estimated price",
        "Output in JSON format for easy parsing"
    ],
    temperature=0.4,
    max_tokens=4096
)


async def generate_product_recommendations(
    destination: str,
    travel_plan: str,
    activities: str
) -> List[Dict[str, Any]]:
    """
    Generate product recommendations for a trip
    Returns list of products with name, category, reason, price
    """
    prompt = f"""
    Generate 8-10 essential travel product recommendations for this trip:
    
    Destination: {destination}
    Travel Plan Summary: {travel_plan}
    Activities: {activities}
    
    For each product, provide:
    - name: Specific product name (e.g., "Waterproof Hiking Boots" not just "shoes")
    - category: Product category (clothing/gadgets/accessories/health)
    - reason: Why this product is needed for this specific trip
    - price_range: Estimated price in USD (e.g., "$50-80")
    - priority: must-have or nice-to-have
    - search_term: Amazon search keywords for this product
    
    Return ONLY valid JSON array format, no other text:
    [
        {{"name": "...", "category": "...", "reason": "...", "price_range": "...", "priority": "...", "search_term": "..."}}
    ]
    """
    
    response = await product_agent_groq.arun(prompt)
    
    # Extract JSON from response
    try:
        # Try to find JSON array in response
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            products = json.loads(json_str)
            return products
    except Exception as e:
        logger.error(f"Error parsing product recommendations: {e}")
    
    return []
