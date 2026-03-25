// JWT-based authentication utilities

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.REACT_APP_BACKEND_URL + '/api';

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  subscription_type: string;
  has_used_free_planner: boolean;
  total_planners_created: number;
  is_premium: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Store token in localStorage and cookies
export const setAuthToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
    // Also set cookie for middleware
    document.cookie = `auth_token=${token}; path=/; max-age=604800; SameSite=Lax`;
  }
};

// Get token from localStorage
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
};

// Remove token from localStorage and cookies
export const removeAuthToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
    // Remove cookie
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  }
};

// Register new user
export const register = async (email: string, password: string, name: string): Promise<AuthResponse> => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  const data = await response.json();
  setAuthToken(data.access_token);
  return data;
};

// Login user
export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  setAuthToken(data.access_token);
  return data;
};

// Get current user
export const getCurrentUser = async (): Promise<User | null> => {
  const token = getAuthToken();
  if (!token) return null;

  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        removeAuthToken();
        return null;
      }
      throw new Error('Failed to get user');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting current user:', error);
    removeAuthToken();
    return null;
  }
};

// Logout user
export const logout = async () => {
  const token = getAuthToken();
  if (token) {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (error) {
      console.error('Error during logout:', error);
    }
  }
  removeAuthToken();
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return getAuthToken() !== null;
};



// Server-side auth helper for API routes
export const auth = {
  api: {
    getSession: async ({ headers }: { headers: Headers }): Promise<{ user: User } | null> => {
      const authorization = headers.get('authorization');
      const cookieHeader = headers.get('cookie');
      
      let token: string | null = null;
      
      // Try to get token from Authorization header
      if (authorization?.startsWith('Bearer ')) {
        token = authorization.substring(7);
      }
      
      // Try to get token from cookies
      if (!token && cookieHeader) {
        const cookies = cookieHeader.split(';').map(c => c.trim());
        const authCookie = cookies.find(c => c.startsWith('auth_token='));
        if (authCookie) {
          token = authCookie.split('=')[1];
        }
      }
      
      if (!token) {
        return null;
      }
      
      try {
        const response = await fetch(`${process.env.BACKEND_API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (!response.ok) {
          return null;
        }
        
        const user = await response.json();
        return { user };
      } catch (error) {
        console.error('Error getting session:', error);
        return null;
      }
    }
  }
};