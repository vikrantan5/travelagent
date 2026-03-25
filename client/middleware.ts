import { NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
  // Check for auth token in cookies
  const authToken = request.cookies.get("auth_token")?.value;
  
  // If no auth token, redirect to auth page
  if (!authToken) {
    return NextResponse.redirect(new URL("/auth", request.url));
  }

  // Verify token with backend
  const backendUrl = process.env.BACKEND_API_URL || "http://localhost:8000";
  
  try {
    const response = await fetch(`${backendUrl}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      // Invalid token, redirect to auth
      return NextResponse.redirect(new URL("/auth", request.url));
    }

    // Token is valid, allow access
    return NextResponse.next();
  } catch (error) {
    console.error("Auth verification error:", error);
    // On error, redirect to auth page
    return NextResponse.redirect(new URL("/auth", request.url));
  }
}

export const config = {
  matcher: ["/plan", "/plans"],
};