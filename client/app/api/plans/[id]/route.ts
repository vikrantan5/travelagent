import { NextRequest, NextResponse } from 'next/server';
import { query, queryOne } from '@/lib/db';
import { auth } from '@/lib/auth';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
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

    // Fetch trip plan with status and output
    const tripPlan = await queryOne<any>(
      `SELECT 
        tp.*,
        tps.id as status_id,
        tps.status as status_status,
        tps."currentStep" as status_current_step,
        tps.error as status_error,
        tps."startedAt" as status_started_at,
        tps."completedAt" as status_completed_at,
        tpo.id as output_id,
        tpo.itinerary as output_itinerary,
        tpo.summary as output_summary
      FROM trip_plan tp
      LEFT JOIN trip_plan_status tps ON tp.id = tps."tripPlanId"
      LEFT JOIN trip_plan_output tpo ON tp.id = tpo."tripPlanId"
      WHERE tp.id = $1 AND tp."userId" = $2`,
      [id, session.user.id]
    );

    if (!tripPlan) {
      return NextResponse.json(
        {
          success: false,
          message: 'Trip plan not found'
        },
        { status: 404 }
      );
    }

    // Restructure the data to match the previous Prisma format
    const formattedTripPlan = {
      id: tripPlan.id,
      name: tripPlan.name,
      destination: tripPlan.destination,
      startingLocation: tripPlan.startingLocation,
      travelDatesStart: tripPlan.travelDatesStart,
      travelDatesEnd: tripPlan.travelDatesEnd,
      dateInputType: tripPlan.dateInputType,
      duration: tripPlan.duration,
      travelingWith: tripPlan.travelingWith,
      adults: tripPlan.adults,
      children: tripPlan.children,
      ageGroups: tripPlan.ageGroups,
      budget: tripPlan.budget,
      budgetCurrency: tripPlan.budgetCurrency,
      travelStyle: tripPlan.travelStyle,
      budgetFlexible: tripPlan.budgetFlexible,
      vibes: tripPlan.vibes,
      priorities: tripPlan.priorities,
      interests: tripPlan.interests,
      rooms: tripPlan.rooms,
      pace: tripPlan.pace,
      beenThereBefore: tripPlan.beenThereBefore,
      lovedPlaces: tripPlan.lovedPlaces,
      additionalInfo: tripPlan.additionalInfo,
      createdAt: tripPlan.createdAt,
      updatedAt: tripPlan.updatedAt,
      userId: tripPlan.userId,
      status: tripPlan.status_id ? {
        id: tripPlan.status_id,
        status: tripPlan.status_status,
        currentStep: tripPlan.status_current_step,
        error: tripPlan.status_error,
        startedAt: tripPlan.status_started_at,
        completedAt: tripPlan.status_completed_at
      } : null,
      output: tripPlan.output_id ? {
        id: tripPlan.output_id,
        itinerary: tripPlan.output_itinerary,
        summary: tripPlan.output_summary
      } : null
    };
    return NextResponse.json(
      {
        success: true,
        tripPlan: formattedTripPlan
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error fetching trip plan:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to fetch trip plan'
      },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
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

    // First check if the plan exists and belongs to the user
    const tripPlan = await queryOne<any>(
        'SELECT id FROM trip_plan WHERE id = $1 AND "userId" = $2',
      [id, session.user.id]
    );

    if (!tripPlan) {
      return NextResponse.json(
        {
          success: false,
          message: 'Trip plan not found'
        },
        { status: 404 }
      );
    }

    // Delete related records first (status and output) - CASCADE should handle this
    // But we'll do it explicitly for safety
    await query('DELETE FROM trip_plan_status WHERE "tripPlanId" = $1', [id]);
    await query('DELETE FROM trip_plan_output WHERE "tripPlanId" = $1', [id]);

    // Delete the trip plan
    await query('DELETE FROM trip_plan WHERE id = $1 AND "userId" = $2', [id, session.user.id]);

    return NextResponse.json(
      {
        success: true,
        message: 'Trip plan deleted successfully'
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error deleting trip plan:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to delete trip plan'
      },
      { status: 500 }
    );
  }
}
