import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { user_id } = body;
    
    const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8000";
    const response = await fetch(`${backendUrl}/api/payment/record-planner?user_id=${user_id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Record planner error:", error);
    return NextResponse.json(
      { error: "Failed to record planner" },
      { status: 500 }
    );
  }
}
