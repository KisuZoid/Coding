# 🔗 Backend-Frontend Integration Guide

This guide explains how to connect your React frontend with your Express.js backend.

## 📋 Table of Contents
1. [Backend Endpoints You Need to Add](#backend-endpoints-to-add)
2. [Frontend Files to Modify](#frontend-files-to-modify)
3. [Step-by-Step Integration](#step-by-step-integration)
4. [Database Schema Alignment](#database-schema-alignment)
5. [Environment Variables](#environment-variables)
6. [Testing the Integration](#testing)

---

## 🔧 Backend Endpoints You Need to Add

Based on your README, here are the endpoints you have and what's missing:

### ✅ Existing Endpoints (from your README)
```
POST   /api/auth/register          - User registration
POST   /api/auth/login             - User login
GET    /api/auth/verify/:token     - Email verification
POST   /api/auth/reset-password    - Password reset request

POST   /api/events/create          - Create event
GET    /api/events/                - Get all events

POST   /api/tickets/generate       - Generate ticket

POST   /api/qr/generate            - Generate QR code
POST   /api/qr/scan                - Scan QR & mark attendance
```

### ❌ Missing Endpoints You Need to Add

Add these to your backend to support all frontend features:

#### **Authentication Endpoints**
```javascript
// In your authRoutes.js
GET    /api/auth/me                      - Get current user info (requires auth)
POST   /api/auth/reset-password/confirm  - Confirm password reset with OTP
```

#### **Event Endpoints**
```javascript
// In your eventRoutes.js
GET    /api/events/:id                   - Get single event by ID
PUT    /api/events/:id                   - Update event (organizer/admin)
DELETE /api/events/:id                   - Delete event (organizer/admin)
GET    /api/events/organizer/my-events   - Get organizer's events (requires auth)
GET    /api/events/user/registered       - Get user's registered events
```

#### **Ticket Endpoints**
```javascript
// In your ticketRoutes.js
GET    /api/tickets/my-tickets           - Get user's tickets (requires auth)
GET    /api/tickets/:id                  - Get ticket by ID
```

#### **Attendance Endpoints**
```javascript
// In your attendanceRoutes.js
GET    /api/attendance/event/:eventId    - Get attendance for event
GET    /api/attendance/my-attendance     - Get user's attendance history
POST   /api/attendance/mark              - Manual attendance marking
```

#### **User Management Endpoints** (Admin)
```javascript
// In your userRoutes.js
GET    /api/users                        - Get all users (admin only)
GET    /api/users/:id                    - Get user by ID
PUT    /api/users/:id                    - Update user
DELETE /api/users/:id                    - Delete user (admin only)
PUT    /api/users/:id/role               - Update user role (admin only)
```

#### **Club Endpoints** (NEW - You need to create these)
```javascript
// Create new clubRoutes.js
GET    /api/clubs                        - Get all clubs
GET    /api/clubs/:id                    - Get club by ID
POST   /api/clubs/create                 - Create club (organizer)
PUT    /api/clubs/:id                    - Update club (organizer)
DELETE /api/clubs/:id                    - Delete club (admin)
POST   /api/clubs/:id/join               - Join club
POST   /api/clubs/:id/leave              - Leave club
GET    /api/clubs/:id/events             - Get club events
GET    /api/clubs/:id/posts              - Get club posts (for social feed)
POST   /api/clubs/:id/posts              - Create club post
```

#### **Analytics Endpoints** (NEW)
```javascript
// Create new analyticsRoutes.js
GET    /api/analytics/dashboard          - Dashboard stats
GET    /api/analytics/events/:id         - Event analytics
```

---

## 📝 Frontend Files to Modify

### 1. **Update Login Component** (`/components/Login.tsx`)

Replace the mock login with real API call:

```typescript
// Find this section around line 25
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);

  try {
    // Replace mock login with real API call
    const response = await authAPI.login({ email, password });
    
    const user: User = {
      id: response.user._id,
      email: response.user.email,
      name: response.user.name || response.user.email.split('@')[0],
      role: response.user.role,
      verified: response.user.verified,
      organizationId: response.user.organizationId
    };

    onLogin(user);
    toast.success(`Welcome back, ${user.name}!`);
  } catch (error: any) {
    toast.error(error.message || 'Login failed');
  } finally {
    setLoading(false);
  }
};
```

### 2. **Update Register Component** (`/components/Register.tsx`)

Replace mock registration around line 41:

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (formData.password !== formData.confirmPassword) {
    toast.error('Passwords do not match');
    return;
  }

  if (!formData.agreeToTerms) {
    toast.error('Please accept the terms and conditions');
    return;
  }

  setLoading(true);

  try {
    await authAPI.register({
      name: formData.name,
      email: formData.email,
      password: formData.password,
      role: formData.role
    });
    
    toast.success('Account created! Please check your email to verify your account.');
    onNavigate('email-verification');
  } catch (error: any) {
    toast.error(error.message || 'Registration failed');
  } finally {
    setLoading(false);
  }
};
```

### 3. **Update UserDashboard** (`/components/UserDashboard.tsx`)

Replace mock events around line 70:

```typescript
import { useState, useEffect } from 'react';
import { eventsAPI } from '../services/api';

// Inside component
const [events, setEvents] = useState<Event[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchEvents = async () => {
    try {
      const data = await eventsAPI.getAllEvents();
      setEvents(data.events || []);
    } catch (error: any) {
      toast.error('Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  fetchEvents();
}, []);
```

### 4. **Update EventDetails** (`/components/EventDetails.tsx`)

Replace mock event data:

```typescript
const [event, setEvent] = useState<Event | null>(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  const fetchEvent = async () => {
    if (!eventId) return;
    
    try {
      const data = await eventsAPI.getEventById(eventId);
      setEvent(data.event);
    } catch (error: any) {
      toast.error('Failed to load event');
    } finally {
      setLoading(false);
    }
  };

  fetchEvent();
}, [eventId]);

const handleRegister = async () => {
  try {
    await ticketsAPI.generateTicket(eventId!);
    setRegistered(true);
    toast.success('Successfully registered for event!');
    setShowQRDialog(true);
  } catch (error: any) {
    toast.error(error.message || 'Registration failed');
  }
};
```

### 5. **Update OrganizerDashboard** (`/components/OrganizerDashboard.tsx`)

Replace event creation around line 185:

```typescript
const handleCreateEvent = async () => {
  if (!newEvent.title || !newEvent.date || !newEvent.time || !newEvent.location) {
    toast.error('Please fill in all required fields');
    return;
  }

  try {
    await eventsAPI.createEvent({
      title: newEvent.title,
      description: newEvent.description,
      date: newEvent.date,
      time: newEvent.time,
      location: newEvent.location,
      category: newEvent.category,
      capacity: parseInt(newEvent.capacity) || 100
    });

    toast.success('Event created successfully!');
    setShowCreateDialog(false);
    // Refresh events list
    fetchOrganizerEvents();
  } catch (error: any) {
    toast.error(error.message || 'Failed to create event');
  }
};
```

### 6. **Update AdminDashboard** (`/components/AdminDashboard.tsx`)

Add user management functionality:

```typescript
const [users, setUsers] = useState([]);

useEffect(() => {
  const fetchUsers = async () => {
    try {
      const data = await usersAPI.getAllUsers();
      setUsers(data.users || []);
    } catch (error: any) {
      toast.error('Failed to load users');
    }
  };

  fetchUsers();
}, []);

const handleToggleUserRole = async (userId: string, currentRole: string) => {
  try {
    const newRole = currentRole === 'user' ? 'organizer' : 'user';
    await usersAPI.updateUserRole(userId, newRole);
    toast.success(`User role updated to ${newRole}`);
    // Refresh users list
  } catch (error: any) {
    toast.error(error.message || 'Failed to update role');
  }
};
```

### 7. **Update MyTickets** (`/components/MyTickets.tsx`)

Fetch real tickets:

```typescript
const [tickets, setTickets] = useState([]);

useEffect(() => {
  const fetchTickets = async () => {
    try {
      const data = await ticketsAPI.getUserTickets();
      setTickets(data.tickets || []);
    } catch (error: any) {
      toast.error('Failed to load tickets');
    }
  };

  fetchTickets();
}, []);
```

### 8. **Update ScanQR** (`/components/ScanQR.tsx`)

Implement real QR scanning:

```typescript
const handleManualScan = async () => {
  if (!qrCode) {
    toast.error('Please enter a QR code');
    return;
  }

  try {
    const result = await qrAPI.scanQRCode(qrCode);
    
    setScanResult({
      success: result.success,
      event: result.eventTitle,
      user: result.userName,
      message: result.message
    });

    toast.success('Attendance marked!');
    setQrCode('');
  } catch (error: any) {
    toast.error(error.message || 'Invalid QR code');
  }
};
```

---

## 🗄️ Database Schema Alignment

### Your MongoDB Models Need These Fields:

#### **User Model** (userModel.js)
```javascript
{
  name: String,
  email: String,
  password: String,  // hashed
  role: { type: String, enum: ['user', 'organizer', 'admin'], default: 'user' },
  verified: { type: Boolean, default: false },
  organizationId: { type: ObjectId, ref: 'Club' }, // for organizers
  eventsAttended: [{ type: ObjectId, ref: 'Event' }],
  clubsMembership: [{ type: ObjectId, ref: 'Club' }],
  createdAt: Date,
  updatedAt: Date
}
```

#### **Event Model** (eventModel.js)
```javascript
{
  title: String,
  description: String,
  date: Date,
  time: String,
  location: String,
  organizerId: { type: ObjectId, ref: 'User' },
  organizerName: String,
  category: String,
  image: String,  // URL or base64
  capacity: Number,
  attendees: [{ type: ObjectId, ref: 'User' }],
  clubId: { type: ObjectId, ref: 'Club' },
  status: { type: String, enum: ['upcoming', 'ongoing', 'completed'], default: 'upcoming' },
  createdAt: Date,
  updatedAt: Date
}
```

#### **Ticket Model** (ticketModel.js)
```javascript
{
  userId: { type: ObjectId, ref: 'User' },
  eventId: { type: ObjectId, ref: 'Event' },
  qrCode: String,  // unique QR code string
  qrCodeImage: String,  // base64 or URL
  status: { type: String, enum: ['active', 'used', 'expired'], default: 'active' },
  scannedAt: Date,
  createdAt: Date
}
```

#### **Club Model** (NEW - clubModel.js)
```javascript
{
  name: String,
  description: String,
  category: String,
  image: String,
  coverImage: String,
  foundedYear: Number,
  email: String,
  website: String,
  socials: {
    instagram: String,
    discord: String,
    twitter: String
  },
  organizerId: { type: ObjectId, ref: 'User' },
  members: [{ type: ObjectId, ref: 'User' }],
  events: [{ type: ObjectId, ref: 'Event' }],
  createdAt: Date,
  updatedAt: Date
}
```

#### **Attendance Model** (attendanceModel.js)
```javascript
{
  userId: { type: ObjectId, ref: 'User' },
  eventId: { type: ObjectId, ref: 'Event' },
  ticketId: { type: ObjectId, ref: 'Ticket' },
  checkInTime: Date,
  checkInMethod: { type: String, enum: ['qr', 'manual'] },
  verifiedBy: { type: ObjectId, ref: 'User' },  // organizer who scanned
  createdAt: Date
}
```

---

## 🔐 Environment Variables

### Frontend (.env in React app root)
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENV=development
```

### Backend (.env in your backend)
```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/happen
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRE=7d

EMAIL_SERVICE=gmail
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

FRONTEND_URL=http://localhost:3000

NODE_ENV=development
```

---

## 🚀 Step-by-Step Integration

### Step 1: Setup Backend
```bash
cd backend
npm install
# Create .env file with variables above
npm start
```

### Step 2: Setup Frontend
```bash
cd frontend
npm install
# Create .env file with REACT_APP_API_URL
npm start
```

### Step 3: Test API Connection
1. Open browser console
2. Try login: `await fetch('http://localhost:5000/api/auth/login', {...})`
3. Check for CORS errors

### Step 4: Fix CORS (in your backend app.js)
```javascript
const cors = require('cors');

app.use(cors({
  origin: 'http://localhost:3000',  // your React app URL
  credentials: true
}));
```

### Step 5: Import API Service
In each component that needs API calls:
```typescript
import api from '../services/api';
// or
import { authAPI, eventsAPI } from '../services/api';
```

### Step 6: Replace Mock Data
Search for `setTimeout` and `mockEvents` in all components and replace with API calls.

---

## 🧪 Testing the Integration

### Test Checklist:
- [ ] Register new user
- [ ] Verify email (check email logs)
- [ ] Login with different roles
- [ ] Create event (organizer)
- [ ] Browse events
- [ ] Register for event
- [ ] Generate ticket
- [ ] Scan QR code
- [ ] View attendance
- [ ] Admin user management

### Common Issues:

**CORS Error:**
```
Access to fetch at 'http://localhost:5000' from origin 'http://localhost:3000' has been blocked by CORS
```
**Fix:** Add CORS middleware in backend

**401 Unauthorized:**
```
Token not provided or invalid
```
**Fix:** Check token storage in localStorage and Authorization header

**404 Not Found:**
```
Cannot GET /api/events/123
```
**Fix:** Implement missing endpoints in backend

---

## 📦 Required npm Packages

Make sure you have these in your backend:
```json
{
  "express": "^4.18.0",
  "mongoose": "^7.0.0",
  "bcrypt": "^5.1.0",
  "jsonwebtoken": "^9.0.0",
  "nodemailer": "^6.9.0",
  "qrcode": "^1.5.0",
  "cors": "^2.8.5",
  "dotenv": "^16.0.0"
}
```

---

## 📚 Additional Resources

- Express.js Docs: https://expressjs.com/
- MongoDB Docs: https://docs.mongodb.com/
- JWT Authentication: https://jwt.io/introduction
- React API Integration: https://react.dev/learn

---

## 🆘 Need Help?

If you encounter issues:
1. Check backend console for errors
2. Check browser console for frontend errors
3. Verify .env files are loaded
4. Test API endpoints with Postman
5. Check MongoDB connection

---

Good luck with the integration! 🚀
