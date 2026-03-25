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
      `SELECT * FROM trip_plan WHERE id = $1 AND user_id = $2`,
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
      `INSERT INTO trip_plan_status (trip_plan_id, status, current_step, created_at, updated_at)
       VALUES ($1, $2, $3, NOW(), NOW())
       ON CONFLICT (trip_plan_id) 
       DO UPDATE SET status = $2, current_step = $3, updated_at = NOW()`,
      [id, 'processing', 'Restarting trip plan generation...']
    );

    // Prepare the request body for the backend API
    const requestBody = {
      trip_plan_id: id,
      travel_plan: {
        name: tripPlan.name,
        destination: tripPlan.destination,
        starting_location: tripPlan.starting_location,
        travel_dates: {
          start: tripPlan.travel_dates_start,
          end: tripPlan.travel_dates_end || ""
        },
        date_input_type: tripPlan.date_input_type,
        duration: tripPlan.duration,
        traveling_with: tripPlan.traveling_with,
        adults: tripPlan.adults,
        children: tripPlan.children,
        age_groups: tripPlan.age_groups,
        budget: tripPlan.budget,
        budget_currency: tripPlan.budget_currency,
        travel_style: tripPlan.travel_style,
        budget_flexible: tripPlan.budget_flexible,
        vibes: tripPlan.vibes,
        priorities: tripPlan.priorities,
        interests: tripPlan.interests || "",
        rooms: tripPlan.rooms,
        pace: tripPlan.pace,
        been_there_before: tripPlan.been_there_before || "",
        loved_places: tripPlan.loved_places || "",
        additional_info: tripPlan.additional_info || ""
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
         SET status = $1, current_step = $2, updated_at = NOW()
         WHERE trip_plan_id = $3`,
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
         SET status = $1, current_step = $2, updated_at = NOW()
         WHERE trip_plan_id = $3`,
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
