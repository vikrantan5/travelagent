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

// Store token in localStorage
export const setAuthToken = (token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
};

// Get token from localStorage
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
};

// Remove token from localStorage
export const removeAuthToken = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
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
