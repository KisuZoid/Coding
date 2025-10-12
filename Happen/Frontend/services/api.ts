/**
 * API Service Layer
 * This file handles all API calls to your Express backend
 * 
 * SETUP INSTRUCTIONS:
 * 1. Replace 'http://localhost:5000' with your actual backend URL
 * 2. Update endpoints to match your backend routes
 * 3. Handle token storage for JWT authentication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Helper function to get auth token
const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.message || 'Something went wrong');
  }
  
  return data;
};

// Helper function to make API calls
const apiCall = async (
  endpoint: string,
  options: RequestInit = {}
) => {
  const token = getAuthToken();
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  return handleResponse(response);
};

// ========================================
// AUTHENTICATION API CALLS
// ========================================

export const authAPI = {
  // POST /api/auth/register
  register: async (userData: {
    name: string;
    email: string;
    password: string;
    role: 'user' | 'organizer';
  }) => {
    return apiCall('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // POST /api/auth/login
  login: async (credentials: { email: string; password: string }) => {
    const data = await apiCall('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    // Store token in localStorage
    if (data.token) {
      localStorage.setItem('authToken', data.token);
    }
    
    return data;
  },

  // GET /api/auth/verify/:token
  verifyEmail: async (token: string) => {
    return apiCall(`/api/auth/verify/${token}`, {
      method: 'GET',
    });
  },

  // POST /api/auth/reset-password
  requestPasswordReset: async (email: string) => {
    return apiCall('/api/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  // POST /api/auth/reset-password/confirm (you may need to add this endpoint)
  resetPassword: async (token: string, newPassword: string) => {
    return apiCall('/api/auth/reset-password/confirm', {
      method: 'POST',
      body: JSON.stringify({ token, newPassword }),
    });
  },

  // Logout (client-side)
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
  },

  // Get current user info (you may need to add this endpoint)
  getCurrentUser: async () => {
    return apiCall('/api/auth/me', {
      method: 'GET',
    });
  },
};

// ========================================
// EVENTS API CALLS
// ========================================

export const eventsAPI = {
  // GET /api/events/
  getAllEvents: async (filters?: {
    category?: string;
    search?: string;
    date?: string;
  }) => {
    const params = new URLSearchParams();
    if (filters?.category) params.append('category', filters.category);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.date) params.append('date', filters.date);
    
    const queryString = params.toString();
    return apiCall(`/api/events${queryString ? `?${queryString}` : ''}`, {
      method: 'GET',
    });
  },

  // GET /api/events/:id
  getEventById: async (eventId: string) => {
    return apiCall(`/api/events/${eventId}`, {
      method: 'GET',
    });
  },

  // POST /api/events/create
  createEvent: async (eventData: {
    title: string;
    description: string;
    date: string;
    time: string;
    location: string;
    category: string;
    capacity: number;
    clubId?: string;
  }) => {
    return apiCall('/api/events/create', {
      method: 'POST',
      body: JSON.stringify(eventData),
    });
  },

  // PUT /api/events/:id (you may need to add this endpoint)
  updateEvent: async (eventId: string, eventData: any) => {
    return apiCall(`/api/events/${eventId}`, {
      method: 'PUT',
      body: JSON.stringify(eventData),
    });
  },

  // DELETE /api/events/:id (you may need to add this endpoint)
  deleteEvent: async (eventId: string) => {
    return apiCall(`/api/events/${eventId}`, {
      method: 'DELETE',
    });
  },

  // GET /api/events/user/:userId (you may need to add this endpoint)
  getUserEvents: async (userId: string) => {
    return apiCall(`/api/events/user/${userId}`, {
      method: 'GET',
    });
  },

  // GET /api/events/organizer/:organizerId (you may need to add this endpoint)
  getOrganizerEvents: async () => {
    return apiCall('/api/events/organizer/my-events', {
      method: 'GET',
    });
  },
};

// ========================================
// TICKETS API CALLS
// ========================================

export const ticketsAPI = {
  // POST /api/tickets/generate
  generateTicket: async (eventId: string) => {
    return apiCall('/api/tickets/generate', {
      method: 'POST',
      body: JSON.stringify({ eventId }),
    });
  },

  // GET /api/tickets/user/:userId (you may need to add this endpoint)
  getUserTickets: async () => {
    return apiCall('/api/tickets/my-tickets', {
      method: 'GET',
    });
  },

  // GET /api/tickets/:ticketId (you may need to add this endpoint)
  getTicketById: async (ticketId: string) => {
    return apiCall(`/api/tickets/${ticketId}`, {
      method: 'GET',
    });
  },
};

// ========================================
// QR CODE API CALLS
// ========================================

export const qrAPI = {
  // POST /api/qr/generate
  generateQRCode: async (eventId: string) => {
    return apiCall('/api/qr/generate', {
      method: 'POST',
      body: JSON.stringify({ eventId }),
    });
  },

  // POST /api/qr/scan
  scanQRCode: async (qrData: string) => {
    return apiCall('/api/qr/scan', {
      method: 'POST',
      body: JSON.stringify({ qrData }),
    });
  },

  // POST /api/qr/validate (you may need to add this endpoint)
  validateQRCode: async (qrCode: string, eventId: string) => {
    return apiCall('/api/qr/validate', {
      method: 'POST',
      body: JSON.stringify({ qrCode, eventId }),
    });
  },
};

// ========================================
// ATTENDANCE API CALLS
// ========================================

export const attendanceAPI = {
  // GET /api/attendance/event/:eventId (you may need to add this endpoint)
  getEventAttendance: async (eventId: string) => {
    return apiCall(`/api/attendance/event/${eventId}`, {
      method: 'GET',
    });
  },

  // POST /api/attendance/mark (you may need to add this endpoint)
  markAttendance: async (eventId: string, userId: string) => {
    return apiCall('/api/attendance/mark', {
      method: 'POST',
      body: JSON.stringify({ eventId, userId }),
    });
  },

  // GET /api/attendance/user/:userId (you may need to add this endpoint)
  getUserAttendance: async () => {
    return apiCall('/api/attendance/my-attendance', {
      method: 'GET',
    });
  },
};

// ========================================
// USER API CALLS
// ========================================

export const usersAPI = {
  // GET /api/users/ (Admin only - you may need to add this endpoint)
  getAllUsers: async () => {
    return apiCall('/api/users', {
      method: 'GET',
    });
  },

  // GET /api/users/:id (you may need to add this endpoint)
  getUserById: async (userId: string) => {
    return apiCall(`/api/users/${userId}`, {
      method: 'GET',
    });
  },

  // PUT /api/users/:id (you may need to add this endpoint)
  updateUser: async (userId: string, userData: any) => {
    return apiCall(`/api/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  },

  // DELETE /api/users/:id (Admin only - you may need to add this endpoint)
  deleteUser: async (userId: string) => {
    return apiCall(`/api/users/${userId}`, {
      method: 'DELETE',
    });
  },

  // PUT /api/users/:id/role (Admin only - you may need to add this endpoint)
  updateUserRole: async (userId: string, role: 'user' | 'organizer' | 'admin') => {
    return apiCall(`/api/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
  },
};

// ========================================
// CLUBS API CALLS (you need to add these endpoints to your backend)
// ========================================

export const clubsAPI = {
  // GET /api/clubs/
  getAllClubs: async () => {
    return apiCall('/api/clubs', {
      method: 'GET',
    });
  },

  // GET /api/clubs/:id
  getClubById: async (clubId: string) => {
    return apiCall(`/api/clubs/${clubId}`, {
      method: 'GET',
    });
  },

  // POST /api/clubs/create (Organizer only)
  createClub: async (clubData: any) => {
    return apiCall('/api/clubs/create', {
      method: 'POST',
      body: JSON.stringify(clubData),
    });
  },

  // POST /api/clubs/:id/join
  joinClub: async (clubId: string) => {
    return apiCall(`/api/clubs/${clubId}/join`, {
      method: 'POST',
    });
  },

  // POST /api/clubs/:id/leave
  leaveClub: async (clubId: string) => {
    return apiCall(`/api/clubs/${clubId}/leave`, {
      method: 'POST',
    });
  },

  // GET /api/clubs/:id/events
  getClubEvents: async (clubId: string) => {
    return apiCall(`/api/clubs/${clubId}/events`, {
      method: 'GET',
    });
  },

  // GET /api/clubs/:id/posts
  getClubPosts: async (clubId: string) => {
    return apiCall(`/api/clubs/${clubId}/posts`, {
      method: 'GET',
    });
  },
};

// ========================================
// ANALYTICS API CALLS (for Admin & Organizer dashboards)
// ========================================

export const analyticsAPI = {
  // GET /api/analytics/dashboard (you need to add this endpoint)
  getDashboardStats: async () => {
    return apiCall('/api/analytics/dashboard', {
      method: 'GET',
    });
  },

  // GET /api/analytics/events/:eventId (you need to add this endpoint)
  getEventAnalytics: async (eventId: string) => {
    return apiCall(`/api/analytics/events/${eventId}`, {
      method: 'GET',
    });
  },
};

export default {
  auth: authAPI,
  events: eventsAPI,
  tickets: ticketsAPI,
  qr: qrAPI,
  attendance: attendanceAPI,
  users: usersAPI,
  clubs: clubsAPI,
  analytics: analyticsAPI,
};
