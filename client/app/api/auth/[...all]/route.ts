// JWT Auth - No Better Auth handler needed
// All auth is handled by backend FastAPI endpoints
export async function GET() {
  return Response.json({ message: "JWT auth - use backend /api/auth endpoints" });
}

export async function POST() {
  return Response.json({ message: "JWT auth - use backend /api/auth endpoints" });
}