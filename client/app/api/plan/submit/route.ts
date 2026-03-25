import { NextRequest, NextResponse } from 'next/server';
import { queryOne } from '@/lib/db';
import { auth } from '@/lib/auth';
import { randomUUID } from 'crypto';

interface TripFormData {
  name: string;
  destination: string;
  startingLocation: string;
  travelDates: { start: string; end: string };
  dateInputType: "picker" | "text";
  duration: number;
  travelingWith: string;
  adults: number;
  children: number;
  ageGroups: string[];
  budget: number;
  budgetCurrency: string;
  travelStyle: string;
  budgetFlexible: boolean;
  vibes: string[];
  priorities: string[];
  interests?: string;
  rooms: number;
  pace: number[];
  beenThereBefore?: string;
  lovedPlaces?: string;
  additionalInfo?: string;
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth.api.getSession({ headers: request.headers });
    
    if (!session) {
      return NextResponse.json(
        {
          success: false,
          message: 'Authentication required'
        },
        { status: 401 }
      );
    }

    const tripData: TripFormData = await request.json();

    // Log the trip data for debugging
    console.log('Received trip planning data:', JSON.stringify(tripData, null, 2));

    // Validate required fields
    if (!tripData.name || !tripData.destination || !tripData.startingLocation) {
      return NextResponse.json(
        {
          success: false,
          message: 'Missing required fields: name, destination, or starting location'
        },
        { status: 400 }
      );
    }

    // Generate a unique ID
    const tripPlanId = randomUUID();

    // Save to database using raw SQL
    const savedTripPlan = await queryOne<any>(
      `INSERT INTO trip_plan (
          id, name, destination, "startingLocation", "travelDatesStart", "travelDatesEnd",
        "dateInputType", duration, "travelingWith", adults, children, "ageGroups",
        budget, "budgetCurrency", "travelStyle", "budgetFlexible", vibes, priorities,
        interests, rooms, pace, "beenThereBefore", "lovedPlaces", "additionalInfo",
        "userId", "createdAt", "updatedAt"
      ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18,
        $19, $20, $21, $22, $23, $24, $25, NOW(), NOW()
      ) RETURNING id`,
      [
        tripPlanId,
        tripData.name,
        tripData.destination,
        tripData.startingLocation,
        tripData.travelDates.start,
        tripData.travelDates.end || null,
        tripData.dateInputType || "picker",
        tripData.duration || null,
        tripData.travelingWith,
        tripData.adults || 1,
        tripData.children || 0,
        tripData.ageGroups || [],
        tripData.budget,
        tripData.budgetCurrency || "USD",
        tripData.travelStyle,
        tripData.budgetFlexible || false,
        tripData.vibes || [],
        tripData.priorities || [],
        tripData.interests || null,
        tripData.rooms || 1,
        tripData.pace || [3],
        tripData.beenThereBefore || null,
        tripData.lovedPlaces || null,
        tripData.additionalInfo || null,
        session.user.id
      ]
    );

    console.log('Trip plan saved to database:', tripPlanId);

    const requestBody = {
      trip_plan_id: tripPlanId,
      travel_plan: {
        name: tripData.name,
        destination: tripData.destination,
        starting_location: tripData.startingLocation,
        travel_dates: {
          start: tripData.travelDates.start,
          end: tripData.travelDates.end || ""
        },
        date_input_type: tripData.dateInputType,
        duration: tripData.duration,
        traveling_with: tripData.travelingWith,
        adults: tripData.adults,
        children: tripData.children,
        age_groups: tripData.ageGroups,
        budget: tripData.budget,
        budget_currency: tripData.budgetCurrency,
        travel_style: tripData.travelStyle,
        budget_flexible: tripData.budgetFlexible,
        vibes: tripData.vibes,
        priorities: tripData.priorities,
        interests: tripData.interests || "",
        rooms: tripData.rooms,
        pace: tripData.pace,
        been_there_before: tripData.beenThereBefore || "",
        loved_places: tripData.lovedPlaces || "",
        additional_info: tripData.additionalInfo || ""
      }
    }

    console.log('Request body:', JSON.stringify(requestBody, null, 2));

    // Call backend API to trigger trip planning
    const backendResponse = await fetch(`${process.env.BACKEND_API_URL}/api/plan/trigger`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!backendResponse.ok) {
      console.error('Backend API error:', await backendResponse.text());
      return NextResponse.json(
        {
          success: false,
          message: 'Failed to trigger trip planning'
        },
        { status: 500 }
      );
    }

    const responseData = await backendResponse.json();
    console.log('Backend response:', JSON.stringify(responseData, null, 2));

    return NextResponse.json(
      {
        success: true,
        message: 'Trip planning triggered successfully',
        response: responseData,
        tripPlanId: tripPlanId
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error processing trip submission:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to save trip plan to database'
      },
      { status: 500 }
    );
  }
}
