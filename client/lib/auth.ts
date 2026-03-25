// Simple mock auth for testing without database
export const auth = {
  api: {
    getSession: async () => {
      // Return a mock session so app works
      return {
        session: {
          user: {
            id: "test-user-123",
            email: "test@example.com",
            name: "Test User"
          }
        }
      };
    },
    signOut: async () => {
      console.log("Sign out called");
    },
  },
  handler: async (req: any) => {
    return new Response(JSON.stringify({ status: "ok" }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  },
};