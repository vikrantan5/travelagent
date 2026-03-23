"""
Additional API Routes
- PDF Download
- Trip History
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from loguru import logger
from typing import List
import json
import os

from models.trip_history import TripHistoryCreate, TripHistoryResponse
from repository.trip_history_repository import (
    create_trip_history,
    get_all_trip_history,
    get_trip_history_by_id,
    delete_trip_history
)
from repository.trip_plan_repository import get_trip_plan_output
from services.pdf_service import generate_trip_pdf_from_json

router = APIRouter(prefix="/api", tags=["Additional Features"])


@router.post("/plan/download")
async def download_trip_plan(trip_plan_id: str):
    """
    Generate and download trip plan as PDF
    
    Args:
        trip_plan_id: ID of the trip plan to download
        
    Returns:
        PDF file
    """
    try:
        logger.info(f"Generating PDF for trip plan: {trip_plan_id}")
        
        # Get trip plan data
        trip_output = await get_trip_plan_output(trip_plan_id)
        
        if not trip_output:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip plan not found"
            )
        
        # Parse itinerary JSON
        trip_data = json.loads(trip_output.itinerary)
        
        # Extract destination name for filename
        destination_name = "trip"
        if 'itinerary' in trip_data:
            try:
                itinerary_obj = json.loads(trip_data['itinerary']) if isinstance(trip_data['itinerary'], str) else trip_data['itinerary']
                if 'destination' in itinerary_obj:
                    destination_name = itinerary_obj['destination']
            except:
                pass
        
        # Generate PDF
        pdf_path = generate_trip_pdf_from_json(trip_output.itinerary, destination_name)
        
        logger.info(f"PDF generated successfully: {pdf_path}")
        
        # Return file
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"{destination_name}_travel_plan.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.post("/history/save", response_model=TripHistoryResponse)
async def save_trip_to_history(trip_data: TripHistoryCreate):
    """
    Save a trip to history
    
    Args:
        trip_data: Trip history data
        
    Returns:
        Created trip history entry
    """
    try:
        logger.info(f"Saving trip to history: {trip_data.destination}")
        
        trip = await create_trip_history(trip_data)
        
        return TripHistoryResponse(
            id=trip.id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            duration=trip.duration,
            budget=trip.budget,
            budget_currency=trip.budget_currency,
            travelers=trip.travelers,
            trip_plan_id=trip.trip_plan_id,
            created_at=trip.created_at.isoformat(),
            has_plan=True
        )
        
    except Exception as e:
        logger.error(f"Error saving trip to history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save trip: {str(e)}"
        )


@router.get("/history", response_model=List[TripHistoryResponse])
async def get_trip_history(limit: int = 50):
    """
    Get all trip history
    
    Args:
        limit: Maximum number of trips to return
        
    Returns:
        List of trip history entries
    """
    try:
        logger.info(f"Fetching trip history (limit: {limit})")
        
        trips = await get_all_trip_history(limit)
        
        return [
            TripHistoryResponse(
                id=trip.id,
                destination=trip.destination,
                start_date=trip.start_date,
                end_date=trip.end_date,
                duration=trip.duration,
                budget=trip.budget,
                budget_currency=trip.budget_currency,
                travelers=trip.travelers,
                trip_plan_id=trip.trip_plan_id,
                created_at=trip.created_at.isoformat(),
                has_plan=True
            )
            for trip in trips
        ]
        
    except Exception as e:
        logger.error(f"Error fetching trip history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


@router.get("/history/{trip_id}", response_model=TripHistoryResponse)
async def get_single_trip_history(trip_id: str):
    """
    Get a specific trip from history
    
    Args:
        trip_id: ID of the trip
        
    Returns:
        Trip history entry
    """
    try:
        trip = await get_trip_history_by_id(trip_id)
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        return TripHistoryResponse(
            id=trip.id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            duration=trip.duration,
            budget=trip.budget,
            budget_currency=trip.budget_currency,
            travelers=trip.travelers,
            trip_plan_id=trip.trip_plan_id,
            created_at=trip.created_at.isoformat(),
            has_plan=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching trip: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trip: {str(e)}"
        )


@router.delete("/history/{trip_id}")
async def delete_trip_from_history(trip_id: str):
    """
    Delete a trip from history
    
    Args:
        trip_id: ID of the trip to delete
        
    Returns:
        Success message
    """
    try:
        await delete_trip_history(trip_id)
        return {"message": "Trip deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting trip: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete trip: {str(e)}"
        )
