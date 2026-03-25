from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.trip_db import TripPlanStatus, TripPlanOutput
from models.travel_plan import (
    TravelPlanAgentRequest,
    TravelPlanRequest,
    TravelPlanTeamResponse,
)
from loguru import logger
from agents.team import trip_planning_team
import json
import time
from agents.structured_output import convert_to_model
from repository.trip_plan_repository import (
    create_trip_plan_status,
    update_trip_plan_status,
    get_trip_plan_status,
    create_trip_plan_output,
    delete_trip_plan_outputs,
)
from agents.destination import destination_agent
from agents.itinerary import itinerary_agent
from agents.flight import flight_search_agent
from agents.hotel import hotel_search_agent
from agents.food import dining_agent
from agents.budget import budget_agent
from services.unsplash_service import unsplash_service
from models.travel_plan import PlaceImage, ProductSuggestion
from typing import List  # ADD THIS IMPORT


# Import Groq agents
from config.groq_agents import (
    destination_agent_groq,
    flight_agent_groq,
    hotel_agent_groq,
    dining_agent_groq,
    budget_agent_groq,
    itinerary_agent_groq,
    generate_product_recommendations
)


def travel_request_to_markdown(data: TravelPlanRequest) -> str:
    # Map of travel vibes to their descriptions
    travel_vibes = {
        "relaxing": "a peaceful retreat focused on wellness, spa experiences, and leisurely activities",
        "adventure": "thrilling experiences including hiking, water sports, and adrenaline activities",
        "romantic": "intimate experiences with private dining, couples activities, and scenic spots",
        "cultural": "immersive experiences with local traditions, museums, and historical sites",
        "food-focused": "culinary experiences including cooking classes, food tours, and local cuisine",
        "nature": "outdoor experiences with national parks, wildlife, and scenic landscapes",
        "photography": "photogenic locations with scenic viewpoints, cultural sites, and natural wonders",
    }

    # Map of travel styles to their descriptions
    travel_styles = {
        "backpacker": "budget-friendly accommodations, local transportation, and authentic experiences",
        "comfort": "mid-range hotels, convenient transportation, and balanced comfort-value ratio",
        "luxury": "premium accommodations, private transfers, and exclusive experiences",
        "eco-conscious": "sustainable accommodations, eco-friendly activities, and responsible tourism",
    }

    # Map of pace levels (0-5) to their descriptions
    pace_levels = {
        0: "1-2 activities per day with plenty of free time and flexibility",
        1: "2-3 activities per day with significant downtime between activities",
        2: "3-4 activities per day with balanced activity and rest periods",
        3: "4-5 activities per day with moderate breaks between activities",
        4: "5-6 activities per day with minimal downtime",
        5: "6+ activities per day with back-to-back scheduling",
    }

    def format_date(date_str: str, is_picker: bool) -> str:
        if not date_str:
            return "Not specified"
        if is_picker:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.strftime("%B %d, %Y")
            except ValueError:
                return date_str
        return date_str.strip()

    date_type = data.date_input_type
    is_picker = date_type == "picker"
    start_date = format_date(data.travel_dates.start, is_picker)
    end_date = format_date(data.travel_dates.end, is_picker)
    date_range = (
        f"between {start_date} and {end_date}"
        if end_date and end_date != "Not specified"
        else start_date
    )

    vibes = data.vibes
    vibes_descriptions = [travel_vibes.get(v, v) for v in vibes]

    lines = [
        f"# 🧳 Travel Plan Request",
        "",
        "## 📍 Trip Overview",
        f"- **Traveler:** {data.name.title() if data.name else 'Unnamed Traveler'}",
        f"- **Route:** {data.starting_location.title()} → {data.destination.title()}",
        f"- **Duration:** {data.duration} days ({date_range})",
        "",
        "## 👥 Travel Group",
        f"- **Group Size:** {data.adults} adults, {data.children} children",
        f"- **Traveling With:** {data.traveling_with or 'Not specified'}",
        f"- **Age Groups:** {', '.join(data.age_groups) or 'Not specified'}",
        f"- **Rooms Needed:** {data.rooms or 'Not specified'}",
        "",
        "## 💰 Budget & Preferences",
        f"- **Budget per person:** {data.budget} {data.budget_currency} ({'Flexible' if data.budget_flexible else 'Fixed'})",
        f"- **Travel Style:** {travel_styles.get(data.travel_style, data.travel_style or 'Not specified')}",
        f"- **Preferred Pace:** {', '.join([pace_levels.get(p, str(p)) for p in data.pace]) or 'Not specified'}",
        "",
        "## ✨ Trip Preferences",
    ]

    if vibes_descriptions:
        lines.append("- **Travel Vibes:**")
        for vibe in vibes_descriptions:
            lines.append(f"  - {vibe}")
    else:
        lines.append("- **Travel Vibes:** Not specified")

    if data.priorities:
        lines.append(f"- **Top Priorities:** {', '.join(data.priorities)}")
    if data.interests:
        lines.append(f"- **Interests:** {data.interests}")

    lines.extend(
        [
            "",
            "## 🗺️ Destination Context",
            f"- **Previous Visit:** {data.been_there_before.capitalize() if data.been_there_before else 'Not specified'}",
            f"- **Loved Places:** {data.loved_places or 'Not specified'}",
            f"- **Additional Notes:** {data.additional_info or 'Not specified'}",
        ]
    )

    return "".join(lines)


async def extract_and_fetch_images(
    destination: str, 
    destination_content: str,
    itinerary_content: str,
    num_images: int = 8
) -> List[PlaceImage]:
    """
    Extract key places from destination research and itinerary, then fetch images from Unsplash.
    
    Args:
        destination: Main destination name
        destination_content: Destination research content
        itinerary_content: Itinerary content
        num_images: Number of place images to fetch
    
    Returns:
        List of PlaceImage objects with real Unsplash image URLs
    """
    place_images = []
    
    try:
        import re
        
        # Extract places from destination content using multiple patterns
        places = []
        
        # Enhanced regex patterns to catch more place names
        patterns = [
            r'\d+\.\s*\*\*([^*]+)\*\*',        # 1. **Place Name**
            r'\*\*([^*]+)\*\*\s*[-–—:]',         # **Place Name** -
            r'###?\s*([^#]+)',                  # ## Place Name or ### Place Name
            r'\d+\.\s*([^:]+)(?=:)',           # 1. Place Name:
            r'-\s*\*\*([^*]+)\*\*',            # - **Place Name**
            r'🏛️|🏰|🏝️|🏔️|🌊|🎭|🏖️|⛰️\s*\*\*([^*]+)\*\*',  # Emoji markers
            r'Visit\s+([A-Z][^,.!?]+?)(?=\s+[-–]|\.|,|)',  # Visit Place Name
        ]
        
        combined_content = destination_content + " " + itinerary_content
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_content, re.IGNORECASE)
            places.extend([m.strip() for m in matches if isinstance(m, str) and m.strip()])
        
        # Clean and filter places
        seen = set()
        unique_places = []
        for place in places:
            place_clean = place.strip()
            # Filter out noise
            if (place_clean 
                and place_clean not in seen 
                and len(place_clean) > 3 
                and len(place_clean) < 80
                and not place_clean.lower().startswith(('day ', 'morning', 'afternoon', 'evening'))
                and not any(x in place_clean.lower() for x in ['http', 'www', 'image_url'])):
                seen.add(place_clean)
                unique_places.append(place_clean)
        
        logger.info(f"Extracted {len(unique_places)} unique places from content")
        
        # Select best places for images (prioritize unique landmarks)
        selected_places = unique_places[:num_images + 5]  # Get extra in case some fail
        
        # Fetch images for each place with better error handling
        successful_fetches = 0
        for place in selected_places:
            if successful_fetches >= num_images:
                break
                
            # Create search query with destination context
            search_query = f"{place}, {destination}"
            logger.info(f"Fetching image for: {search_query}")
            
            image_url = unsplash_service.get_image_for_place(place, destination)
            
            if image_url:
                place_images.append(PlaceImage(place=place, image_url=image_url))
                successful_fetches += 1
                logger.info(f"✅ Fetched image for {place}: {image_url[:80]}...")
            else:
                logger.warning(f"⚠️ No image found for {place}")
        
        # If we didn't get enough place-specific images, fetch general destination images
        if len(place_images) < num_images:
            needed = num_images - len(place_images)
            logger.info(f"Fetching {needed} additional general destination images")
            general_images = unsplash_service.get_destination_images(destination, count=needed + 2)
            
            for idx, img_url in enumerate(general_images[:needed]):
                place_images.append(PlaceImage(
                    place=f"{destination} Scenic View {idx + 1}",
                    image_url=img_url
                ))
                logger.info(f"✅ Added general image: {img_url[:80]}...")
        
        logger.info(f"Total images fetched: {len(place_images)}")
        
    except Exception as e:
        logger.error(f"Error extracting and fetching images: {str(e)}", exc_info=True)
        # Fallback: fetch general destination images
        try:
            logger.info(f"Falling back to general destination images for {destination}")
            general_images = unsplash_service.get_destination_images(destination, count=num_images)
            for idx, img_url in enumerate(general_images):
                place_images.append(PlaceImage(
                    place=f"{destination} - Attraction {idx + 1}",
                    image_url=img_url
                ))
            logger.info(f"Fallback successful: {len(place_images)} images fetched")
        except Exception as fallback_error:
            logger.error(f"Fallback image fetch also failed: {str(fallback_error)}")
    
    return place_images


def parse_itinerary_to_daily_plan(text: str, duration: int, start_date: str):
    import re
    from datetime import datetime, timedelta

    days = []
    day_blocks = re.split(r"##\s*Day\s*\d+", text, flags=re.IGNORECASE)[1:]

    if not day_blocks:
        return []

    try:
        base_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except:
        base_date = None

    for i, block in enumerate(day_blocks[:duration]):
        morning = re.search(r"\*\*Morning:\*\*(.*?)(\*\*|$)", block, re.S)
        afternoon = re.search(r"\*\*Afternoon:\*\*(.*?)(\*\*|$)", block, re.S)
        evening = re.search(r"\*\*Evening:\*\*(.*?)(\*\*|$)", block, re.S)

        day_date = (
            (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            if base_date else ""
        )

        days.append(
            {
                "day": i + 1,
                "date": day_date,
                "morning": (morning.group(1).strip() if morning else ""),
                "afternoon": (afternoon.group(1).strip() if afternoon else ""),
                "evening": (evening.group(1).strip() if evening else ""),
                "image_url": "",
            }
        )

    return days


async def generate_travel_plan(request: TravelPlanAgentRequest) -> str:
    """Generate a travel plan based on the request and log status/output to database."""
    trip_plan_id = request.trip_plan_id
    logger.info(f"Generating travel plan for tripPlanId: {trip_plan_id}")

    # Get or create status entry using repository functions
    status_entry = await get_trip_plan_status(trip_plan_id)
    if not status_entry:
        status_entry = await create_trip_plan_status(
            trip_plan_id=trip_plan_id, status="pending"
        )

    # Update status to processing
    status_entry = await update_trip_plan_status(
        trip_plan_id=trip_plan_id,
        status="processing",
        current_step="Initializing travel plan generation",
        started_at=datetime.now(timezone.utc),
    )

    try:
        travel_request_md = travel_request_to_markdown(request.travel_plan)
        logger.info(f"Travel request markdown: {travel_request_md}")

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Generating plan with TripCraft AI agents",
        )

        last_response_content = ""
        time_start = time.time()

        # Team Collaboration
        # prompt = f"""
        #     Below is my travel plan request. Please generate a travel plan for the request.
        #     {travel_request_md}
        # """

        # time_start = time.time()
        # ai_response = await trip_planning_team.arun(prompt)
        # time_end = time.time()
        # logger.info(f"AI team processing time: {time_end - time_start:.2f} seconds")

        # last_response_content = ai_response.messages[-1].content
        # logger.info(
        #     f"Last AI Response for conversion: {last_response_content[:500]}..."
        # )

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Researching about the destination",
        )

        # Destination Research using Groq
        destination_research_content = await destination_agent_groq.arun(
            f"""
            Research destination: {request.travel_plan.destination}
            
            Trip details:
            - Duration: {request.travel_plan.duration} days
            - Budget: {request.travel_plan.budget} {request.travel_plan.budget_currency}
            - Travel style: {request.travel_plan.travel_style}
            - Vibes: {', '.join(request.travel_plan.vibes)}
            
            Provide 8-10 key attractions with brief descriptions.
            Be concise but informative.
            """
        )

        logger.info(
            f"Destination research response: {destination_research_content[:500]}..."
        )

        # Store agent responses separately, don't accumulate
        last_response_content = f"""
        ## Destination Attractions:
        ---
         {destination_research_content[:1500]}
        ---
"""

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Searching for the best flights",
        )
        # Flight Search using Groq
        flight_search_content = await flight_agent_groq.arun(
            f"""
            Find flights for:
            - Route: {request.travel_plan.starting_location} → {request.travel_plan.destination}
            - Dates: {request.travel_plan.travel_dates.start} to {request.travel_plan.travel_dates.end}
            - Travelers: {request.travel_plan.adults} adults, {request.travel_plan.children} children
            - Budget: {request.travel_plan.budget} {request.travel_plan.budget_currency}
            
            Provide exactly 4-5 flight options with variety.
            Include: airline, flight number, times, duration, stops, price, booking URL.
            Be concise.
            """
        )

        logger.info(
            f"Flight search response: {flight_search_content[:500]}..."
        )

        last_response_content += f"""
        ## Flight recommendations:
        ---
        {flight_search_content[:1200]}
        ---
        """

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Searching for the best hotels",
        )
        # Hotel Search using Groq
        hotel_search_content = await hotel_agent_groq.arun(
            f"""
            Find hotels for:
            - Destination: {request.travel_plan.destination}
            - Dates: {request.travel_plan.travel_dates.start} to {request.travel_plan.travel_dates.end}
            - Rooms: {request.travel_plan.rooms}
            - Style: {request.travel_plan.travel_style}
            - Budget: {request.travel_plan.budget} {request.travel_plan.budget_currency}
            
            Provide exactly 4-5 hotel options with variety.
            Include: name, address, rating, price, key amenities, description, booking URL.
            Be concise.
            """
        )

        last_response_content += f"""
        ## Hotel recommendations:
        ---
        {hotel_search_content[:1200]}
        ---
        """

        logger.info(
            f"Hotel search response: {hotel_search_content[:500]}..."
        )

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Searching for the best restaurants",
        )
        # Restaurant Search using Groq
        restaurant_search_content = await dining_agent_groq.arun(
            f"""
            Find restaurants for:
            - Destination: {request.travel_plan.destination}
            - Preferences: {', '.join(request.travel_plan.vibes)}
            - Budget: {request.travel_plan.budget} {request.travel_plan.budget_currency}
            
            Provide exactly 4-5 restaurant options with variety.
            Include: name, location, cuisine, price range, description, popular dishes, URL.
            Be concise.
            """
        )

        last_response_content += f"""
        ## Restaurant recommendations:
        ---
        {restaurant_search_content[:1200]}
        ---
        """

        logger.info(
            f"Restaurant search response: {restaurant_search_content[:500]}..."
        )

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Creating the day-by-day itinerary",
        )
        # Itinerary using Groq - Use summarized context
        itinerary_content = await itinerary_agent_groq.arun(
            f"""
            Create a detailed {request.travel_plan.duration}-day itinerary for {request.travel_plan.destination}
            
            Trip info:
            - Duration: {request.travel_plan.duration} days
            - Travelers: {request.travel_plan.adults} adults{f', {request.travel_plan.children} children' if request.travel_plan.children else ''}
            - Travel style: {request.travel_plan.travel_style}
            - Vibes: {', '.join(request.travel_plan.vibes[:3])}
            
            IMPORTANT: Structure each day clearly with:
            ## Day 1
            **Morning:** [activities with timing]
            **Afternoon:** [activities with timing]
            **Evening:** [activities with timing]
            
            Create {request.travel_plan.duration} days following this exact structure.
            Be specific with timings and locations.
            """
        )
    
        logger.info(f"Itinerary response: {itinerary_content[:500]}...")
        # Parse itinerary into structured format
        parsed_daily_plan = parse_itinerary_to_daily_plan(
            itinerary_content, 
            request.travel_plan.duration,
            request.travel_plan.travel_dates.start
        )
        logger.info(f"Parsed {len(parsed_daily_plan)} days from itinerary")

        last_response_content += f"""
        ## Day-by-day itinerary:
        ---
        {itinerary_content[:1500]}
        ---
        """

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Optimizing the budget",
        )
        # Budget using Groq - Use summarized context
        budget_content = await budget_agent_groq.arun(
            f"""
            Create budget breakdown for:
            - Destination: {request.travel_plan.destination}
            - Duration: {request.travel_plan.duration} days
            - Budget: {request.travel_plan.budget} {request.travel_plan.budget_currency}
            - Travelers: {request.travel_plan.adults} adults, {request.travel_plan.children} children
            
            Provide concise breakdown by category: flights, hotels, food, activities, transport.
            Include tips for saving money.
            """
        )
        logger.info(f"Budget response: {budget_content[:500]}...")
         
          # Update status for image fetching
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Fetching real images from Unsplash",
        )
        
        # Fetch images for key places (increased to 8 for better coverage)
        place_images = await extract_and_fetch_images(
            destination=request.travel_plan.destination,
            destination_content=destination_research_content,
            itinerary_content=itinerary_content,
            num_images=8
        )
        logger.info(f"✅ Fetched {len(place_images)} real place images from Unsplash")
        
        # Generate Product Recommendations using Groq
        logger.info("Generating product recommendations...")
        products = await generate_product_recommendations(
            destination=request.travel_plan.destination,
            travel_plan=travel_request_md[:500],
            activities=destination_research_content[:500]
        )
        logger.info(f"Generated {len(products)} product recommendations")

        time_end = time.time()
        logger.info(f"Total time taken: {time_end - time_start:.2f} seconds")

        # Update status for response conversion
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Adding finishing touches",
        )

        # Try to convert to structured format, but with better error handling
        json_response_output = None
        response_dict = {}
        
        try:
            json_response_output = await convert_to_model(
                last_response_content, TravelPlanTeamResponse
            )
            logger.info(f"Converted Structured Response: {json_response_output[:500]}...")
            response_dict = json.loads(json_response_output)
        except Exception as conversion_error:
            logger.error(f"Error in structured conversion: {str(conversion_error)}")
            # Create a minimal valid structure
            response_dict = {
                "title": f"{request.travel_plan.duration} Days in {request.travel_plan.destination}",
                "destination": request.travel_plan.destination,
                "duration": f"{request.travel_plan.duration} Days",
                "budget_estimate": f"{request.travel_plan.budget} {request.travel_plan.budget_currency}",
                "day_by_day_plan": [],
                "hotels": [],
                "attractions": [],
                "flights": [],
                "restaurants": [],
                "budget_insights": [],
                "tips": []
            }

        # Parse the JSON response to add our custom fields
        try:
            # Add new format fields (ensure they exist)
            response_dict["title"] = f"{request.travel_plan.duration} Days in {request.travel_plan.destination}"
            response_dict["destination"] = request.travel_plan.destination
            response_dict["duration"] = f"{request.travel_plan.duration} Days"
            response_dict["budget_estimate"] = f"{request.travel_plan.budget} {request.travel_plan.budget_currency}"
            
            # ✅ FORCE OVERRIDE: Use ONLY backend-fetched Unsplash images
            # Remove any AI-generated image URLs from response_dict
            if "images" in response_dict:
                logger.info("⚠️ Removing AI-generated images array")
                del response_dict["images"]
            
            # Add ONLY backend-fetched place images (real images.unsplash.com URLs)
            response_dict["images"] = [img.model_dump() for img in place_images]
            logger.info(f"✅ Added {len(place_images)} backend-fetched images to response")
            
            # Ensure day_by_day_plan exists and is populated
            if "day_by_day_plan" not in response_dict or not response_dict["day_by_day_plan"]:
                # Use parsed daily plan from itinerary
                response_dict["day_by_day_plan"] = parsed_daily_plan
                logger.info(f"Using parsed daily plan with {len(parsed_daily_plan)} days")
            
            # Rename day_by_day_plan to daily_plan for new format
            if "day_by_day_plan" in response_dict:
                response_dict["daily_plan"] = response_dict["day_by_day_plan"]
                
                # ✅ CRITICAL FIX: ALWAYS OVERRIDE image_url for each day
                # DO NOT trust AI-generated image URLs - they use source.unsplash.com which is unreliable
                logger.info(f"🔧 Force overriding image URLs for {len(response_dict['daily_plan'])} days")
                
                for idx, day in enumerate(response_dict["daily_plan"]):
                    # Remove any existing AI-generated image_url
                    if day.get("image_url"):
                        logger.info(f"⚠️ Day {idx+1} had AI-generated image URL, overriding...")
                    
                    # ALWAYS assign backend-fetched image (sequential mapping)
                    if idx < len(place_images):
                        day["image_url"] = place_images[idx].image_url
                        logger.info(f"✅ Day {idx+1}: Assigned image from place_images[{idx}]")
                    else:
                        # Fallback: fetch additional image if needed
                        logger.info(f"⚠️ Day {idx+1}: Not enough place images, fetching fallback...")
                        img_url = unsplash_service.get_image_for_place(
                            f"{request.travel_plan.destination}",
                            request.travel_plan.destination
                        )
                        day["image_url"] = img_url if img_url else ""
                        logger.info(f"✅ Day {idx+1}: Assigned fallback image: {img_url[:80] if img_url else 'None'}...")
            
            # Add product suggestions (convert from products format)
            if products:
                response_dict["product_suggestions"] = [
                    {
                        "name": p.get("name", ""),
                        "why_needed": p.get("reason", p.get("why_needed", "")),
                        "link": p.get("amazon_url", p.get("link", ""))
                    }
                    for p in products
                ]
            else:
                response_dict["product_suggestions"] = []
            
            # Convert back to JSON
            json_response_output = json.dumps(response_dict, indent=2)
            
        except Exception as parse_error:
            logger.error(f"Error parsing response for custom fields: {str(parse_error)}")
            # Create minimal valid JSON if all else fails
            json_response_output = json.dumps(response_dict, indent=2)

        # Delete any existing output entries for this trip plan
        await delete_trip_plan_outputs(trip_plan_id=trip_plan_id)

        final_response = json.dumps(
            {
                "itinerary": json_response_output,
                "budget_agent_response": budget_content,
                "destination_agent_response": destination_research_content,
                "flight_agent_response": flight_search_content,
                "hotel_agent_response": hotel_search_content,
                "restaurant_agent_response": restaurant_search_content,
                "itinerary_agent_response": itinerary_content,
                "product_recommendations": products,
            },
            indent=2,
        )

        # Create new output entry
        await create_trip_plan_output(
            trip_plan_id=trip_plan_id,
            itinerary=final_response,
            summary="",
        )

        # Update status to completed
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="completed",
            current_step="Plan generated and saved",
            completed_at=datetime.now(timezone.utc),
        )

        return final_response
    except Exception as e:
        logger.error(
            f"Error generating travel plan for {trip_plan_id}: {str(e)}", exc_info=True
        )
        # Update status to failed
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="failed",
            error=str(e),
            completed_at=datetime.now(timezone.utc),
        )
        raise