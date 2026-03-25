import { NextRequest, NextResponse } from 'next/server';
import { query, queryOne } from '@/lib/db';
import { auth } from '@/lib/auth';

export async function POST(
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
      `SELECT * FROM trip_plan WHERE id = $1 AND "userId" = $2`,
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

    // Update the status to pending/processing
    await query(
      `INSERT INTO trip_plan_status (id, "tripPlanId", status, "currentStep", "createdAt", "updatedAt")
       VALUES (gen_random_uuid(), $1, $2, $3, NOW(), NOW())
       ON CONFLICT ("tripPlanId") 
       DO UPDATE SET status = EXCLUDED.status, "currentStep" = EXCLUDED."currentStep", "updatedAt" = NOW()`,
      [id, 'processing', 'Restarting trip plan generation...']
    );

    // Prepare the request body for the backend API
    const requestBody = {
      trip_plan_id: id,
      travel_plan: {
        name: tripPlan.name,
        destination: tripPlan.destination,
        starting_location: tripPlan.startingLocation,
        travel_dates: {
          start: tripPlan.travelDatesStart,
          end: tripPlan.travelDatesEnd || ""
        },
        date_input_type: tripPlan.dateInputType,
        duration: tripPlan.duration,
        traveling_with: tripPlan.travelingWith,
        adults: tripPlan.adults,
        children: tripPlan.children,
        age_groups: tripPlan.ageGroups,
        budget: tripPlan.budget,
        budget_currency: tripPlan.budgetCurrency,
        travel_style: tripPlan.travelStyle,
        budget_flexible: tripPlan.budgetFlexible,
        vibes: tripPlan.vibes,
        priorities: tripPlan.priorities,
        interests: tripPlan.interests || "",
        rooms: tripPlan.rooms,
        pace: tripPlan.pace,
        been_there_before: tripPlan.beenThereBefore || "",
        loved_places: tripPlan.lovedPlaces || "",
        additional_info: tripPlan.additionalInfo || ""
      }
    };

    // Call backend API to trigger trip planning again
    const backendResponse = await fetch(`${process.env.BACKEND_API_URL}/api/plan/trigger`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!backendResponse.ok) {
      // If backend call fails, update status back to failed
      await query(
        `UPDATE trip_plan_status 
         SET status = $1, "currentStep" = $2, "updatedAt" = NOW()
         WHERE "tripPlanId" = $3`,
        ['failed', 'Failed to restart trip plan generation', id]
      );

      console.error('Backend API error:', await backendResponse.text());
      return NextResponse.json(
        {
          success: false,
          message: 'Failed to retry trip planning'
        },
        { status: 500 }
      );
    }

    const responseData = await backendResponse.json();
    console.log('Backend retry response:', JSON.stringify(responseData, null, 2));

    return NextResponse.json(
      {
        success: true,
        message: 'Trip planning retry triggered successfully',
        response: responseData
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error processing trip retry:', error);

    // Ensure we update the status to failed if there's an error
    try {
      await query(
        `UPDATE trip_plan_status 
         SET status = $1, "currentStep" = $2, "updatedAt" = NOW()
         WHERE "tripPlanId" = $3`,
        ['failed', 'Error occurred while retrying', id]
      );
    } catch (statusError) {
      console.error('Failed to update status after error:', statusError);
    }

    return NextResponse.json(
      {
        success: false,
        message: 'Failed to retry trip plan'
      },
      { status: 500 }
    );
  }
}
