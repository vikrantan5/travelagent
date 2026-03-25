import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { auth } from '@/lib/auth';

export async function GET(request: NextRequest) {
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

    const tripPlans = await query<any>(
      `SELECT DISTINCT ON (id) 
        id, name, destination, starting_location as "startingLocation",
        travel_dates_start as "travelDatesStart", travel_dates_end as "travelDatesEnd",
        date_input_type as "dateInputType", duration, traveling_with as "travelingWith",
        adults, children, age_groups as "ageGroups", budget, budget_currency as "budgetCurrency",
        travel_style as "travelStyle", budget_flexible as "budgetFlexible",
        vibes, priorities, interests, rooms, pace, been_there_before as "beenThereBefore",
        loved_places as "lovedPlaces", additional_info as "additionalInfo",
        created_at as "createdAt", updated_at as "updatedAt", user_id as "userId"
      FROM trip_plan
      WHERE user_id = $1
      ORDER BY id, created_at DESC`,
      [session.user.id]
    );

    return NextResponse.json(
      {
        success: true,
        tripPlans
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error fetching trip plans:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to fetch trip plans'
      },
      { status: 500 }
    );
  }
}
