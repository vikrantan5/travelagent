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
        id, name, destination, "startingLocation",
        "travelDatesStart", "travelDatesEnd",
        "dateInputType", duration, "travelingWith",
        adults, children, "ageGroups", budget, "budgetCurrency",
        "travelStyle", "budgetFlexible",
        vibes, priorities, interests, rooms, pace, "beenThereBefore",
        "lovedPlaces", "additionalInfo",
        "createdAt", "updatedAt", "userId"
      FROM trip_plan
      WHERE "userId" = $1
      ORDER BY id, "createdAt" DESC`,
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
