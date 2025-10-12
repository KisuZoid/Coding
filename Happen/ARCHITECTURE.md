# 🏗️ System Architecture

## 📊 Complete System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            React Frontend (Port 3000)                │   │
│  │  ┌──────────┬──────────┬──────────┬──────────────┐  │   │
│  │  │  Home    │  Login   │Dashboard │ EventDetails │  │   │
│  │  │  Page    │  Page    │  Pages   │    Page      │  │   │
│  │  └────┬─────┴─────┬────┴────┬─────┴──────┬───────┘  │   │
│  │       │           │         │            │          │   │
│  │       └───────────┴─────────┴────────────┘          │   │
│  │                      │                               │   │
│  │              ┌───────▼────────┐                      │   │
│  │              │  API Service   │                      │   │
│  │              │ (/services/    │                      │   │
│  │              │    api.ts)     │                      │   │
│  │              └───────┬────────┘                      │   │
│  └──────────────────────┼───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          │ HTTP/HTTPS
                          │ (REST API)
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Express.js Backend (Port 5000)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  API Routes                          │   │
│  │  ┌──────────┬──────────┬──────────┬──────────────┐  │   │
│  │  │  /auth   │ /events  │ /tickets │   /users     │  │   │
│  │  └────┬─────┴─────┬────┴────┬─────┴──────┬───────┘  │   │
│  │       │           │         │            │          │   │
│  │  ┌────▼──────┬────▼─────┬───▼────┬───────▼──────┐   │   │
│  │  │  Auth     │  Event   │Ticket  │    User      │   │   │
│  │  │Controller │Controller│Controller│ Controller  │   │   │
│  │  └────┬──────┴────┬─────┴───┬────┴───────┬──────┘   │   │
│  │       │           │         │            │          │   │
│  │  ┌────▼───────────▼─────────▼────────────▼──────┐   │   │
│  │  │            MongoDB Connection               │   │   │
│  │  └────────────────────┬─────────────────────────┘   │   │
│  └───────────────────────┼──────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   MongoDB Database                          │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐   │
│  │ Users  │ Events │Tickets │  QR    │Attend- │ Clubs  │   │
│  │Collection│Collection│Collection│Collection│ance│Collection│   │
│  └────────┴────────┴────────┴────────┴────────┴────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Examples

### Example 1: User Logs In

```
1. User Interface
   ├─ User types email/password
   └─ Clicks "Sign In" button

2. Frontend (Login.tsx)
   ├─ Validates form fields
   ├─ Calls authAPI.login()
   └─ Shows loading state

3. API Service (/services/api.ts)
   ├─ Constructs request
   ├─ Adds headers
   └─ POST http://localhost:5000/api/auth/login

4. Backend (authRoutes.js)
   ├─ Receives request
   ├─ Routes to authController.login()
   └─ Validates credentials

5. Auth Controller (authController.js)
   ├─ Queries User collection
   ├─ Compares password hash
   ├─ Generates JWT token
   └─ Returns user + token

6. Backend → Frontend
   └─ Response: { token: "...", user: {...} }

7. Frontend (Login.tsx)
   ├─ Stores token in localStorage
   ├─ Stores user in state
   ├─ Shows success toast
   └─ Redirects to dashboard

8. User sees Dashboard
```

---

### Example 2: Browse Events

```
1. User visits Dashboard

2. Frontend (UserDashboard.tsx)
   ├─ useEffect() hook runs
   └─ Calls eventsAPI.getAllEvents()

3. API Service
   └─ GET http://localhost:5000/api/events

4. Backend (eventRoutes.js)
   └─ Routes to eventController.getAllEvents()

5. Event Controller
   ├─ Event.find() from MongoDB
   ├─ Formats response
   └─ Returns events array

6. Frontend receives data
   ├─ setEvents(data.events)
   └─ React re-renders

7. User sees event grid
```

---

### Example 3: Generate Ticket

```
1. User clicks event

2. Frontend (EventDetails.tsx)
   └─ Shows event details

3. User clicks "Register"

4. Frontend
   └─ Calls ticketsAPI.generateTicket(eventId)

5. API Service
   ├─ Adds auth token to header
   └─ POST http://localhost:5000/api/tickets/generate

6. Backend (ticketController.js)
   ├─ Verifies JWT token
   ├─ Generates unique QR code
   ├─ Creates ticket in DB
   └─ Returns ticket + QR

7. Frontend
   ├─ Receives ticket data
   ├─ Shows QR code modal
   └─ Updates UI

8. User sees QR code
```

---

### Example 4: Scan QR Code

```
1. Organizer opens Scanner

2. Frontend (ScanQR.tsx)
   ├─ Shows camera view
   └─ Or manual input field

3. User scans QR code

4. Frontend
   └─ Calls qrAPI.scanQRCode(qrData)

5. Backend (qrController.js)
   ├─ Validates QR code
   ├─ Checks if already used
   ├─ Marks attendance
   └─ Updates ticket status

6. Frontend
   ├─ Shows success/error
   └─ Displays attendee info

7. Organizer sees confirmation
```

---

## 🔐 Authentication Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    First Visit                          │
│  User → Frontend → No token → Shows Login Page          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      Login                              │
│  POST /api/auth/login                                   │
│  ├─ Backend validates credentials                       │
│  ├─ Generates JWT token                                 │
│  └─ Returns: { token: "...", user: {...} }             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Token Storage                           │
│  localStorage.setItem('authToken', token)               │
│  localStorage.setItem('currentUser', user)              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Protected Requests                         │
│  Every API call includes:                               │
│  Authorization: Bearer {token}                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            Backend Middleware                           │
│  authMiddleware.js                                      │
│  ├─ Extracts token from header                          │
│  ├─ Verifies JWT signature                              │
│  ├─ Decodes user ID                                     │
│  └─ Attaches user to req.user                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│             Role Authorization                          │
│  roleMiddleware.js                                      │
│  ├─ Checks req.user.role                                │
│  ├─ Compares with required role                         │
│  └─ Allows or denies access                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📱 Frontend Component Hierarchy

```
App.tsx
├── Home.tsx (Public)
│   └── Features showcase
│
├── Login.tsx (Public)
│   └── Login form
│
├── Register.tsx (Public)
│   └── Registration form
│
├── EmailVerification.tsx (Public)
│   └── Verification status
│
├── PasswordReset.tsx (Public)
│   └── Reset flow
│
├── UserDashboard.tsx (Protected - User)
│   ├── Event grid
│   ├── Club list
│   └── Search/filters
│
├── OrganizerDashboard.tsx (Protected - Organizer)
│   ├── My events list
│   ├── Create event form
│   ├── Attendance tracking
│   └── Analytics
│
├── AdminDashboard.tsx (Protected - Admin)
│   ├── All events management
│   ├── User management
│   ├── System stats
│   └── Settings
│
├── EventDetails.tsx (Protected)
│   ├── Event info
│   ├── Registration button
│   └── QR code modal
│
├── MyTickets.tsx (Protected)
│   ├── Active tickets
│   └── Past tickets
│
├── ClubDetails.tsx (Protected)
│   ├── Club info
│   ├── Events
│   └── Posts
│
├── ScanQR.tsx (Protected - Organizer/Admin)
│   ├── Camera scanner
│   └── Manual input
│
└── Profile.tsx (Protected)
    ├── User info
    ├── Settings
    └── History
```

---

## 🗄️ Database Schema Relationships

```
┌─────────────────────────────────────────────────────────┐
│                      USERS                              │
│  _id, name, email, password, role, verified             │
└───────┬─────────────────────────────────────────────────┘
        │
        │ organizerId (1:Many)
        ├──────────────────────────────────────┐
        │                                      │
        ▼                                      ▼
┌────────────────┐                    ┌────────────────┐
│    EVENTS      │                    │     CLUBS      │
│  _id, title,   │                    │  _id, name,    │
│  organizerId,  │◄───────────────────┤  organizerId,  │
│  clubId        │  clubId            │  members[]     │
└───────┬────────┘                    └────────────────┘
        │
        │ eventId (1:Many)
        ├──────────────────────────────────────┐
        │                                      │
        ▼                                      ▼
┌────────────────┐                    ┌────────────────┐
│    TICKETS     │                    │  ATTENDANCE    │
│  _id, userId,  │                    │  _id, userId,  │
│  eventId,      │                    │  eventId,      │
│  qrCode        │                    │  checkInTime   │
└────────────────┘                    └────────────────┘
        │
        │ qrCode (1:1)
        ▼
┌────────────────┐
│   QR_CODES     │
│  _id, code,    │
│  ticketId,     │
│  used          │
└────────────────┘
```

---

## 🔄 State Management Flow

```
┌─────────────────────────────────────────────────────────┐
│                    App.tsx (Root)                       │
│  ┌───────────────────────────────────────────────┐     │
│  │  Global State:                                │     │
│  │  - currentUser (User | null)                  │     │
│  │  - currentPage (Page type)                    │     │
│  │  - selectedEventId (string | null)            │     │
│  │  - selectedClubId (string | null)             │     │
│  └───────────────────────────────────────────────┘     │
│                          │                              │
│                          │ Props passed down            │
│                          │                              │
│  ┌───────────────────────▼───────────────────────┐     │
│  │              Child Components                 │     │
│  │  - Receive: currentUser, onNavigate, onLogout │     │
│  │  - Manage: Local state (forms, loading, etc.) │     │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**State Flow:**
1. App.tsx holds global state
2. Props pass data to children
3. Callbacks update parent state
4. Parent re-renders → children re-render
5. LocalStorage persists auth data

---

## 📦 API Response Standards

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "errors": [ ... ]  // Optional validation errors
}
```

### List Response
```json
{
  "success": true,
  "count": 10,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "totalPages": 5
  }
}
```

---

## 🔌 API Endpoint Categories

### 1️⃣ Public Endpoints (No Auth)
```
GET    /api/events/              # Browse events
POST   /api/auth/register        # Register
POST   /api/auth/login           # Login
GET    /api/auth/verify/:token   # Verify email
```

### 2️⃣ User Endpoints (Auth Required)
```
GET    /api/auth/me              # Get current user
GET    /api/events/:id           # Event details
POST   /api/tickets/generate     # Generate ticket
GET    /api/tickets/my-tickets   # My tickets
POST   /api/clubs/:id/join       # Join club
```

### 3️⃣ Organizer Endpoints (Organizer Role)
```
POST   /api/events/create        # Create event
PUT    /api/events/:id           # Update event
DELETE /api/events/:id           # Delete event
GET    /api/events/organizer/my-events  # My events
POST   /api/qr/scan              # Scan QR code
```

### 4️⃣ Admin Endpoints (Admin Role)
```
GET    /api/users/               # All users
PUT    /api/users/:id/role       # Update role
DELETE /api/users/:id            # Delete user
GET    /api/analytics/dashboard  # System stats
```

---

## 🎯 Component → Endpoint Mapping

| Component | Primary Endpoints Used |
|-----------|------------------------|
| Login.tsx | POST /api/auth/login |
| Register.tsx | POST /api/auth/register |
| UserDashboard.tsx | GET /api/events/, GET /api/clubs/ |
| EventDetails.tsx | GET /api/events/:id, POST /api/tickets/generate |
| MyTickets.tsx | GET /api/tickets/my-tickets |
| OrganizerDashboard.tsx | GET /api/events/organizer/my-events, POST /api/events/create |
| AdminDashboard.tsx | GET /api/users/, PUT /api/users/:id/role |
| ScanQR.tsx | POST /api/qr/scan |
| ClubDetails.tsx | GET /api/clubs/:id |
| Profile.tsx | GET /api/auth/me, PUT /api/users/:id |

---

## 🚀 Deployment Architecture

```
Production Setup:

┌─────────────────────────────────────────────────────┐
│  Users                                              │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  CDN / Frontend Hosting (Vercel/Netlify)            │
│  - React app (static files)                         │
│  - HTTPS enabled                                    │
│  - Auto-scaling                                     │
└───────────────┬─────────────────────────────────────┘
                │
                │ API Calls (HTTPS)
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Backend Server (Heroku/Railway/DigitalOcean)       │
│  - Express.js                                       │
│  - Environment variables                            │
│  - CORS configured                                  │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Database (MongoDB Atlas)                           │
│  - Cloud hosted                                     │
│  - Automatic backups                                │
│  - Scalable                                         │
└─────────────────────────────────────────────────────┘
```

---

## 🔒 Security Layers

```
Layer 1: Frontend
├─ Input validation
├─ XSS protection (React)
├─ No sensitive data stored
└─ HTTPS only

Layer 2: API Gateway
├─ Rate limiting
├─ CORS policies
└─ Request validation

Layer 3: Authentication
├─ JWT tokens
├─ Token expiration
└─ Refresh token logic

Layer 4: Authorization
├─ Role-based access
├─ Resource ownership checks
└─ Permission validation

Layer 5: Database
├─ Connection encryption
├─ Query sanitization
├─ Password hashing
└─ Data validation
```

---

This architecture provides a solid foundation for your Happen platform! 🎉
