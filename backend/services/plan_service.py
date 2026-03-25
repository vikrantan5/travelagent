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
    num_images: int = 5
) -> List[PlaceImage]:
    """
    Extract key places from destination research and itinerary, then fetch images from Unsplash.
    
    Args:
        destination: Main destination name
        destination_content: Destination research content
        itinerary_content: Itinerary content
        num_images: Number of place images to fetch
    
    Returns:
        List of PlaceImage objects
    """
    place_images = []
    
    try:
        # Use a simple extraction approach - look for numbered attractions or bullet points
        # This is a basic implementation - you might want to use an LLM to extract places properly
        import re
        
        # Extract places from destination content (looking for numbered or bulleted items)
        places = []
        
        # FIXED: Correct regex patterns
        patterns = [
            r'\d+\.\s*\*\*([^*]+)\*\*',  # 1. **Place Name**
            r'\d+\.\s*([^:]+)[:：]',      # 1. Place Name:
            r'-\s*\*\*([^*]+)\*\*',       # - **Place Name**
            r'##\s+([^#]+)',              # ## Place Name
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, destination_content + " " + itinerary_content)
            places.extend([m.strip() for m in matches if m.strip()])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_places = []
        for place in places:
            place_clean = place.strip()
            if place_clean and place_clean not in seen and len(place_clean) < 100:
                seen.add(place_clean)
                unique_places.append(place_clean)
        
        # Take first num_images places
        selected_places = unique_places[:num_images]
        
        logger.info(f"Extracted {len(selected_places)} places: {selected_places}")
        
        # Fetch images for each place
        for place in selected_places:
            image_url = unsplash_service.get_image_for_place(place, destination)
            if image_url:
                place_images.append(PlaceImage(place=place, image_url=image_url))
                logger.info(f"Fetched image for {place}: {image_url}")
        
        # If we didn't get enough place-specific images, get general destination images
        if len(place_images) < 3:
            logger.info(f"Not enough place images, fetching general destination images")
            general_images = unsplash_service.get_destination_images(destination, count=3)
            for idx, img_url in enumerate(general_images):
                if len(place_images) >= num_images:
                    break
                place_images.append(PlaceImage(
                    place=f"{destination} - View {idx + 1}",
                    image_url=img_url
                ))
        
    except Exception as e:
        logger.error(f"Error extracting and fetching images: {str(e)}")
        # Fallback: fetch general destination images
        try:
            general_images = unsplash_service.get_destination_images(destination, count=num_images)
            for idx, img_url in enumerate(general_images):
                place_images.append(PlaceImage(
                    place=f"{destination} - View {idx + 1}",
                    image_url=img_url
                ))
        except Exception as fallback_error:
            logger.error(f"Fallback image fetch also failed: {str(fallback_error)}")
    
    return place_images


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
            Please research about the destination {request.travel_plan.destination}

            Below are user's travel request:
            {travel_request_md}

            Provide a very detailed research about the destination, its attractions, activities, and other relevant information that user might be interested in.

            Give 10 attractions/activities that user might be interested in.
            """
        )

        logger.info(
              f"Destination research response: {destination_research_content[:500]}..."
        )

        last_response_content = f"""
        ## Destination Attractions:
        ---
         {destination_research_content}
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
            Please find flights according to the user's travel request:
            {travel_request_md}

            If user has not specified the exact flight date, please consider it by yourself based on the user's travel request.

            Provide a very detailed research about the flights, its price, duration, and other relevant information that user might be interested in.

            ive exactly 5-6 flight options with variety (budget-friendly, standard, and premium if possible).
            For each flight, include:
            - Airline name and flight number
            - Departure and arrival times
            - Duration and number of stops
            - Price estimate
            - Booking URL (use format like https://www.google.com/flights or https://www.kayak.com/flights)
            """
        )

        logger.info(
            f"Flight search response: {flight_search_content[:500]}..."
        )

        last_response_content += f"""
        ## Flight recommendations:
        ---
        {flight_search_content}
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
            Please find hotels according to the user's travel request:
            {travel_request_md}

            If user has not specified the exact hotel dates, please consider it by yourself based on the user's travel request.

            Provide a very detailed research about the hotels, its price, amenities, and other relevant information that user might be interested in.

             Give exactly 5-6 hotel options with variety (budget, mid-range, luxury).
            For each hotel, include:
            - Hotel name and full address
            - Rating (out of 5 stars)
            - Price range per night
            - Key amenities (as a list)
            - Description
            - Booking URL (use format like https://www.booking.com or https://www.hotels.com)
            """
        )

        last_response_content += f"""
        ## Hotel recommendations:
        ---
        {hotel_search_content}
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
            Please find restaurants according to the user's travel request:
            {travel_request_md}

            If user has not specified the exact restaurant dates, please consider it by yourself based on the user's travel request.

            Provide a very detailed research about the restaurants, its price, menu, and other relevant information that user might be interested in.

            Give exactly 5-6 restaurant options with variety (budget-friendly, mid-range, fine dining).
            For each restaurant, include:
            - Restaurant name and location/address
            - Cuisine type and price range ($, $$, $$$)
            - Description and ambiance
            - Popular dishes
            - Website URL or Google Maps URL
            """
        )

        last_response_content += f"""
        ## Restaurant recommendations:
        ---
        {restaurant_search_content}
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
        # Itinerary using Groq
        itinerary_content = await itinerary_agent_groq.arun(
            f"""
            Please create a detailed day-by-day itinerary for a trip to {request.travel_plan.destination}  for user's travel request:
            {travel_request_md}

            Based on the following information:
            {last_response_content}
            """
        )

        logger.info(f"Itinerary response: {itinerary_content[:500]}...")

        last_response_content += f"""
        ## Day-by-day itinerary:
        ---
        {itinerary_content}
        ---
        """

        # Update status for AI team generation
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Optimizing the budget",
        )
        # Budget using Groq
        budget_content = await budget_agent_groq.arun(
            f"""
            Please optimize the budget according to the user's travel request:
            {travel_request_md}

            Based on the following information:
            {last_response_content}
            """
        )

        logger.info(f"Budget response: {budget_content[:500]}...")
         
        # Update status for image fetching
        await update_trip_plan_status(
            trip_plan_id=trip_plan_id,
            status="processing",
            current_step="Fetching images from Unsplash",
        )
        
        # Fetch images for key places
        place_images = await extract_and_fetch_images(
            destination=request.travel_plan.destination,
            destination_content=destination_research_content,
            itinerary_content=itinerary_content,
            num_images=5
        )
        logger.info(f"Fetched {len(place_images)} place images")
        
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

        json_response_output = await convert_to_model(
            last_response_content, TravelPlanTeamResponse
        )
        logger.info(f"Converted Structured Response: {json_response_output[:500]}...")

         # Parse the JSON response to add our custom fields
        try:
            response_dict = json.loads(json_response_output)
            
            # Add new format fields
            response_dict["title"] = f"{request.travel_plan.duration} Days in {request.travel_plan.destination}"
            response_dict["destination"] = request.travel_plan.destination
            response_dict["duration"] = f"{request.travel_plan.duration} Days"
            response_dict["budget_estimate"] = f"{request.travel_plan.budget} {request.travel_plan.budget_currency}"
            
            # Add place images
            response_dict["images"] = [img.model_dump() for img in place_images]
            
            # Rename day_by_day_plan to daily_plan for new format
            if "day_by_day_plan" in response_dict:
                response_dict["daily_plan"] = response_dict["day_by_day_plan"]
                
                # Fetch an image for each day if not already present
                for idx, day in enumerate(response_dict["daily_plan"]):
                    if not day.get("image_url"):
                        # Use existing place images or fetch new one
                        if idx < len(place_images):
                            day["image_url"] = place_images[idx].image_url
                        else:
                            # Fetch a generic destination image
                            img_url = unsplash_service.get_image_for_place(
                                f"Day {day.get('day', idx+1)} {request.travel_plan.destination}",
                                request.travel_plan.destination
                            )
                            day["image_url"] = img_url if img_url else ""
            
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
            # Continue with original response

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