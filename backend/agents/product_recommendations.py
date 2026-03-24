"""
Product Recommendations Agent
Generates AI-powered travel product recommendations based on trip details
"""
from agno.agent import Agent
from config.llm import model
from loguru import logger


product_recommendations_agent = Agent(
    name="Product Recommendation Specialist",
    role="Travel Essentials & Product Expert",
    model=model,
    markdown=True,
    description=(
        "You are an expert in recommending travel products and essentials. "
        "Based on the destination, weather, activities, and travel style, you suggest "
        "practical and essential items travelers should consider bringing or purchasing."
    ),
    instructions=[
        "1. Analyze the travel details:",
        "   - Destination and climate",
        "   - Season and expected weather conditions",
        "   - Planned activities (beach, hiking, city tour, adventure, etc.)",
        "   - Trip duration",
        "   - Travel style (luxury, budget, backpacking, family)",
        "",
        "2. Generate product recommendations in these categories:",
        "   - Clothing & Footwear (appropriate for weather and activities)",
        "   - Electronics & Gadgets (chargers, adapters, power banks)",
        "   - Travel Accessories (luggage, packing cubes, organizers)",
        "   - Health & Safety (first aid, sunscreen, insect repellent)",
        "   - Documents & Money (travel wallet, RFID protection)",
        "   - Entertainment (books, headphones, travel guides)",
        "",
        "3. For each product recommendation, provide:",
        "   - Product name (specific and searchable)",
        "   - Category",
        "   - Why it's needed for this specific trip",
        "   - Estimated price range in USD",
        "   - Priority level (Essential, Recommended, Optional)",
        "",
        "4. Prioritize:",
        "   - Climate-specific items (rain gear for rainy season, warm clothes for cold)",
        "   - Activity-specific gear (hiking boots, snorkel gear, formal wear)",
        "   - Destination-specific needs (power adapters for international, reef-safe sunscreen)",
        "   - Practical essentials over luxury items",
        "",
        "5. Consider:",
        "   - Weather patterns and seasonal variations",
        "   - Local customs and dress codes",
        "   - Activity requirements and safety",
        "   - Space-saving and multi-functional items",
        "",
        "6. Limit recommendations to 8-12 most relevant products",
        "   Focus on items that significantly enhance the travel experience",
    ],
    expected_output="""
A structured JSON list of product recommendations:

```json
[
  {
    "name": "Universal Travel Adapter with USB-C",
    "category": "Electronics",
    "reason": "Essential for charging devices in [destination] as they use [plug type] outlets",
    "price_range": "$20-$35",
    "priority": "Essential",
    "keywords": "universal travel adapter usb-c"
  },
  {
    "name": "Lightweight Quick-Dry Travel Towel",
    "category": "Travel Accessories",
    "reason": "Perfect for beach activities and quick-drying in humid climate",
    "price_range": "$15-$25",
    "priority": "Recommended",
    "keywords": "microfiber travel towel quick dry"
  }
]
```

Focus on practical, trip-specific recommendations that address the unique needs of the destination and activities.
""",
)


def generate_product_recommendations(trip_details: dict) -> list[dict]:
    """
    Generate product recommendations based on trip details
    
    Args:
        trip_details: Dictionary containing trip information
        
    Returns:
        List of product recommendation dictionaries
    """
    try:
        # Extract relevant trip information
        destination = trip_details.get('destination', 'Unknown')
        dates = f"{trip_details.get('start_date', '')} to {trip_details.get('end_date', '')}"
        duration = trip_details.get('duration', 'several days')
        budget = trip_details.get('budget', {})
        preferences = trip_details.get('preferences', {})
        activities = preferences.get('activities', [])
        travel_style = preferences.get('travel_style', 'moderate')
        
        # Build context for the agent
        context = f"""
Generate travel product recommendations for the following trip:

**Destination:** {destination}
**Travel Dates:** {dates}
**Duration:** {duration} days
**Budget:** ${budget.get('min', 0)} - ${budget.get('max', 'flexible')}
**Travel Style:** {travel_style}
**Planned Activities:** {', '.join(activities) if activities else 'General sightseeing'}
**Special Preferences:** {preferences.get('special_notes', 'None specified')}

Please provide 8-12 essential product recommendations that are specifically relevant to this trip.
Return the recommendations as a JSON array following the expected output format.
"""
        
        logger.info(f"Generating product recommendations for destination: {destination}")
        
        # Get recommendations from the agent
        response = product_recommendations_agent.run(context)
        
        # Parse the response to extract JSON
        import json
        import re
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```jsons*([[sS]*?])s*```', response.content)
        if json_match:
            products_json = json_match.group(1)
            products = json.loads(products_json)
        else:
            # Try to parse entire response as JSON
            products = json.loads(response.content)
        
        # Add Amazon search URLs
        for product in products:
            keywords = product.get('keywords', product.get('name', ''))
            # Create Amazon search URL
            search_query = keywords.replace(' ', '+')
            product['amazon_url'] = f"https://www.amazon.com/s?k={search_query}"
        
        logger.info(f"Generated {len(products)} product recommendations")
        return products
        
    except Exception as e:
        logger.error(f"Error generating product recommendations: {e}")
        # Return fallback generic recommendations
        return [
            {
                "name": "Universal Travel Adapter",
                "category": "Electronics",
                "reason": "Essential for charging devices internationally",
                "price_range": "$20-$35",
                "priority": "Essential",
                "amazon_url": "https://www.amazon.com/s?k=universal+travel+adapter"
            },
            {
                "name": "Portable Power Bank 20000mAh",
                "category": "Electronics",
                "reason": "Keep devices charged during long days of exploration",
                "price_range": "$25-$40",
                "priority": "Recommended",
                "amazon_url": "https://www.amazon.com/s?k=portable+power+bank+20000mah"
            },
            {
                "name": "Travel Packing Cubes Set",
                "category": "Travel Accessories",
                "reason": "Organize luggage efficiently and maximize space",
                "price_range": "$15-$30",
                "priority": "Recommended",
                "amazon_url": "https://www.amazon.com/s?k=travel+packing+cubes"
            }
        ]
