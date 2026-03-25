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
      model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.3,
          max_tokens: int = 3000
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
            if self.model == "llama-3.3-70b-versatile":
                logger.info(f"[{self.name}] Trying fallback model: mixtral-8x7b-32768")
                self.model = "mixtral-8x7b-32768"
                return await self.arun(user_message, context)
            raise


# Destination Agent
destination_agent_groq = GroqAgent(
    name="Destination Explorer",
    role="destination research specialist",
    instructions=[
        "Research destinations with focus on user preferences",
        "Provide 8-10 attractions with brief descriptions",
        "Include practical info: hours, fees, visit duration",
        "Consider seasonality and current events",
        "Format in clear Markdown with emojis"
    ],
    temperature=0.3
)

# Flight Search Agent
flight_agent_groq = GroqAgent(
    name="Flight Search Assistant",
    role="flight search specialist",
    instructions=[
        "Provide 4-5 realistic flight options with variety",
        "Include direct and connecting flights",
        "Provide: airline, flight number, times, duration, stops, estimated price",
        "Include booking URLs (Google Flights or Kayak format)",
        "Format clearly with pricing breakdown"
    ],
    temperature=0.2
)
# Hotel Search Agent
hotel_agent_groq = GroqAgent(
    name="Hotel Search Assistant",
    role="accommodation specialist",
    instructions=[
        "Provide 4-5 hotels with variety (budget, mid-range, luxury)",
        "Include: name, address, rating, price, key amenities, description",
        "Include booking URLs (Booking.com or Hotels.com format)",
        "Consider location relative to attractions",
        "Format with clear sections"
    ],
    temperature=0.3
)

# Dining Agent
dining_agent_groq = GroqAgent(
    name="Culinary Guide",
    role="dining specialist",
    instructions=[
        "Provide 4-5 restaurants with variety (budget, mid-range, fine dining)",
        "Include: name, location, cuisine, price range, description, popular dishes",
        "Include website or Google Maps URLs",
        "Highlight local specialties",
        "Format with emojis and clear price indicators ($, $$, $$$)"
    ],
    temperature=0.3
)

# Budget Agent
budget_agent_groq = GroqAgent(
    name="Budget Optimizer",
    role="travel budget specialist",
    instructions=[
        "Calculate costs by category: transport, accommodation, food, activities",
        "Suggest cost-saving alternatives",
        "Include hidden costs and contingencies",
        "Calculate daily spending estimates",
        "Format with clear tables and totals"
    ],
    temperature=0.2
)
# Itinerary Agent
itinerary_agent_groq = GroqAgent(
    name="Itinerary Planner",
    role="day-by-day itinerary specialist",
    instructions=[
        "Create detailed day-by-day itineraries with CLEAR structure:",
        "- Each day must have: Day number, Morning activities, Afternoon activities, Evening activities",
        "- Use format: '## Day X' for each day header",
        "- Under each day, use '**Morning:**', '**Afternoon:**', '**Evening:**' sections",
        "- Include specific timing (e.g., 9:00 AM, 2:00 PM)",
        "- Balance activities with rest periods",
        "- Consider travel time between locations",
        "- Add practical tips at the end of each day",
        "- Keep descriptions concise (2-3 sentences per time slot)"
    ],
    temperature=0.3,
    max_tokens=2000
)

# Product Recommendation Agent (NEW)
product_agent_groq = GroqAgent(
    name="Travel Essentials Advisor",
    role="travel product recommendation specialist",
    instructions=[
        "Recommend essential travel products based on destination and activities",
        "Consider weather, terrain, and cultural requirements",
        "Suggest 6-8 practical items travelers should bring",
        "Include categories: clothing, gadgets, accessories, health & safety",
        "Provide specific product recommendations (not generic categories)",
        "Explain why each product is needed for this specific trip",
        "Include approximate price ranges",
        "Prioritize items by importance (must-have vs nice-to-have)",
        "Format with product name, category, reason, and estimated price",
        "Output in JSON format for easy parsing"
    ],
    temperature=0.4,
     max_tokens=2500
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
    Generate 6-8 essential travel product recommendations for this trip:
    
    Destination: {destination}
    Duration & Budget: {travel_plan[:300]}
    Activities: {activities[:300]}
    
    For each product, provide:
    - name: Specific product name (e.g., "Waterproof Hiking Boots" not just "shoes")
    - category: Product category (clothing/gadgets/accessories/health)
    - reason: Why needed for this trip (max 50 words)
    - price_range: Estimated price in USD (e.g., "$50-80")
    - priority: must-have or nice-to-have
    - search_term: Amazon search keywords
    
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

            
            # Add Amazon URLs to each product
            for product in products:
                search_term = product.get('search_term', product.get('name', ''))
                # Create Amazon search URL
                search_query = search_term.replace(' ', '+')
                product['amazon_url'] = f"https://www.amazon.com/s?k={search_query}"
            
            logger.info(f"Successfully generated {len(products)} product recommendations with Amazon links")
            return products
    except Exception as e:
        logger.error(f"Error parsing product recommendations: {e}")
    
    return []