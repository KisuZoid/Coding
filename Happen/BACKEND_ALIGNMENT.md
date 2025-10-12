# 🔄 Backend-Frontend Data Structure Alignment

This document shows exactly how your backend data should match the frontend expectations.

## 📊 Data Structure Mapping

### 1. User Object

**What Frontend Expects:**
```typescript
{
  id: string,              // User's MongoDB _id
  email: string,           // User's email
  name: string,            // User's full name
  role: 'admin' | 'organizer' | 'user',
  verified: boolean,       // Email verification status
  organizationId?: string  // Club ID if organizer
}
```

**What Your Backend Should Return:**

In `authController.js` login response:
```javascript
res.json({
  success: true,
  token: "jwt_token_here",
  user: {
    _id: user._id,              // Frontend will use this as 'id'
    name: user.name,
    email: user.email,
    role: user.role,
    verified: user.verified,
    organizationId: user.organizationId
  }
});
```

**Backend Model Should Have:**
```javascript
// userModel.js
{
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { 
    type: String, 
    enum: ['user', 'organizer', 'admin'], 
    default: 'user' 
  },
  verified: { type: Boolean, default: false },
  organizationId: { type: ObjectId, ref: 'Club' }
}
```

---

### 2. Event Object

**What Frontend Expects:**
```typescript
{
  id: string,              // Event's MongoDB _id
  title: string,
  description: string,
  date: string,            // ISO date string: "2025-10-15"
  time: string,            // Time string: "18:00"
  location: string,
  organizerId: string,
  organizerName: string,   // Name of the organizer
  category: string,
  image: string,           // Image URL
  attendees: number,       // COUNT of attendees (not array)
  capacity: number,
  clubId?: string,
  clubName?: string
}
```

**What Your Backend Should Return:**

```javascript
// In eventController.js - getAllEvents
res.json({
  success: true,
  events: events.map(event => ({
    id: event._id,                    // ← Important: 'id' not '_id'
    title: event.title,
    description: event.description,
    date: event.date,                 // Make sure this is ISO string
    time: event.time,
    location: event.location,
    organizerId: event.organizerId,
    organizerName: event.organizerName,  // ← Add this
    category: event.category,
    image: event.image || 'default-image-url',
    attendees: event.attendees.length,   // ← COUNT not array
    capacity: event.capacity,
    clubId: event.clubId,
    clubName: event.clubName            // ← Add this
  }))
});
```

**Backend Model Should Have:**
```javascript
// eventModel.js
{
  title: { type: String, required: true },
  description: { type: String, required: true },
  date: { type: Date, required: true },     // Store as Date, return as ISO string
  time: { type: String, required: true },   // "18:00" format
  location: { type: String, required: true },
  organizerId: { type: ObjectId, ref: 'User', required: true },
  organizerName: { type: String },          // ← Add this for easy access
  category: { 
    type: String, 
    enum: ['Technology', 'Entertainment', 'Career', 'Wellness', 'Business', 'Arts']
  },
  image: { type: String },
  capacity: { type: Number, required: true },
  attendees: [{ type: ObjectId, ref: 'User' }],  // Array of user IDs
  clubId: { type: ObjectId, ref: 'Club' },
  clubName: { type: String }                // ← Add this
}
```

**Important Date Handling:**
```javascript
// When creating event, convert date to ISO
const event = new Event({
  ...req.body,
  date: new Date(req.body.date).toISOString()
});

// When returning events, ensure date is string
const formattedEvent = {
  ...event._doc,
  date: event.date.toISOString().split('T')[0]  // "2025-10-15"
};
```

---

### 3. Ticket Object

**What Frontend Expects:**
```typescript
{
  id: string,
  eventId: string,
  eventTitle: string,      // ← Event details
  date: string,
  time: string,
  location: string,
  organizer: string,
  qrCode: string,          // QR code data/ID
  status: 'active' | 'used' | 'expired',
  image: string            // Event image
}
```

**What Your Backend Should Return:**

```javascript
// ticketController.js - getUserTickets
const tickets = await Ticket.find({ userId: req.user.id })
  .populate('eventId');

res.json({
  success: true,
  tickets: tickets.map(ticket => ({
    id: ticket._id,
    eventId: ticket.eventId._id,
    eventTitle: ticket.eventId.title,      // ← From populated event
    date: ticket.eventId.date,
    time: ticket.eventId.time,
    location: ticket.eventId.location,
    organizer: ticket.eventId.organizerName,
    qrCode: ticket.qrCode,
    status: ticket.status,
    image: ticket.eventId.image
  }))
});
```

**Backend Model Should Have:**
```javascript
// ticketModel.js
{
  userId: { type: ObjectId, ref: 'User', required: true },
  eventId: { type: ObjectId, ref: 'Event', required: true },
  qrCode: { type: String, unique: true, required: true },
  qrCodeImage: { type: String },  // Base64 or URL of QR image
  status: { 
    type: String, 
    enum: ['active', 'used', 'expired'], 
    default: 'active' 
  },
  scannedAt: { type: Date }
}
```

---

### 4. Club Object

**What Frontend Expects:**
```typescript
{
  id: string,
  name: string,
  description: string,
  category: string,
  image: string,
  memberCount: number,     // COUNT not array
  events: number           // COUNT not array
}
```

**What Your Backend Should Return:**

```javascript
// clubController.js - getAllClubs
res.json({
  success: true,
  clubs: clubs.map(club => ({
    id: club._id,
    name: club.name,
    description: club.description,
    category: club.category,
    image: club.image,
    memberCount: club.members.length,    // ← COUNT
    events: club.events.length           // ← COUNT
  }))
});
```

---

### 5. QR Scan Response

**What Frontend Expects:**
```typescript
{
  success: boolean,
  event: string,           // Event title
  user: string,            // User name
  message: string
}
```

**What Your Backend Should Return:**

```javascript
// qrController.js - scanQRCode
res.json({
  success: true,
  eventTitle: "Tech Talk: AI in Education",  // ← Frontend expects 'event' key
  userName: "John Doe",                       // ← Frontend expects 'user' key
  message: "Attendance marked successfully!"
});
```

**Better - Match Frontend Exactly:**
```javascript
res.json({
  success: true,
  event: attendance.eventId.title,    // ← Use 'event' not 'eventTitle'
  user: attendance.userId.name,       // ← Use 'user' not 'userName'
  message: "Attendance marked successfully!"
});
```

---

## 🔧 Common Data Transformation Issues

### Issue 1: MongoDB _id vs id

**Problem:** Frontend uses `id`, MongoDB returns `_id`

**Solution 1 - Transform in controller:**
```javascript
const formattedEvents = events.map(event => ({
  id: event._id,  // Convert _id to id
  ...event._doc
}));
```

**Solution 2 - Use lean() and transform:**
```javascript
const events = await Event.find().lean();
const formatted = events.map(e => ({
  ...e,
  id: e._id,
  _id: undefined  // Remove _id
}));
```

---

### Issue 2: Dates Not Formatting Correctly

**Problem:** Date stored as Date object, frontend needs string

**Solution:**
```javascript
// When saving
event.date = new Date(req.body.date);

// When returning
formattedEvent.date = event.date.toISOString().split('T')[0];  // "2025-10-15"
```

---

### Issue 3: Returning Arrays Instead of Counts

**Problem:** Frontend shows `[object Object]` instead of number

**Wrong:**
```javascript
{
  attendees: [userId1, userId2, userId3]  // ❌ Array
}
```

**Right:**
```javascript
{
  attendees: event.attendees.length  // ✅ Number
}
```

---

### Issue 4: Missing Populated Fields

**Problem:** Frontend expects organizer name, but only ID returned

**Solution - Use populate:**
```javascript
const event = await Event.findById(id)
  .populate('organizerId', 'name email')     // Get organizer details
  .populate('clubId', 'name');               // Get club details

res.json({
  event: {
    ...event._doc,
    organizerName: event.organizerId.name,   // ← Add this
    clubName: event.clubId?.name             // ← Add this
  }
});
```

---

## 📋 Endpoint Response Cheatsheet

### POST /api/auth/register
```json
{
  "success": true,
  "message": "User registered. Please verify email.",
  "userId": "507f1f77bcf86cd799439011"
}
```

### POST /api/auth/login
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "verified": true
  }
}
```

### GET /api/events/
```json
{
  "success": true,
  "count": 2,
  "events": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Tech Talk",
      "description": "...",
      "date": "2025-10-15",
      "time": "18:00",
      "location": "Room 301",
      "organizerId": "507f1f77bcf86cd799439012",
      "organizerName": "CS Club",
      "category": "Technology",
      "image": "https://...",
      "attendees": 45,
      "capacity": 100
    }
  ]
}
```

### GET /api/events/:id
```json
{
  "success": true,
  "event": {
    "id": "507f1f77bcf86cd799439011",
    "title": "Tech Talk",
    // ... same as above
  }
}
```

### POST /api/tickets/generate
```json
{
  "success": true,
  "ticket": {
    "_id": "507f1f77bcf86cd799439013",
    "userId": "507f1f77bcf86cd799439011",
    "eventId": "507f1f77bcf86cd799439012",
    "qrCode": "QR-123-ABC",
    "qrCodeImage": "data:image/png;base64,...",
    "status": "active"
  }
}
```

### GET /api/tickets/my-tickets
```json
{
  "success": true,
  "count": 2,
  "tickets": [
    {
      "id": "507f1f77bcf86cd799439013",
      "eventId": "507f1f77bcf86cd799439012",
      "eventTitle": "Tech Talk",
      "date": "2025-10-15",
      "time": "18:00",
      "location": "Room 301",
      "organizer": "CS Club",
      "qrCode": "QR-123-ABC",
      "status": "active",
      "image": "https://..."
    }
  ]
}
```

### POST /api/qr/scan
```json
{
  "success": true,
  "event": "Tech Talk",
  "user": "John Doe",
  "message": "Attendance marked successfully!"
}
```

### GET /api/users/ (Admin)
```json
{
  "success": true,
  "count": 5,
  "users": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "verified": true,
      "eventsAttended": 12
    }
  ]
}
```

---

## ✅ Validation Checklist

Before deploying, verify these:

**User Response:**
- [ ] Returns `_id` or `id` (both work, but be consistent)
- [ ] Includes `role` field
- [ ] Includes `verified` boolean
- [ ] Password is NOT included

**Event Response:**
- [ ] `date` is string format "YYYY-MM-DD"
- [ ] `time` is string format "HH:MM"
- [ ] `attendees` is NUMBER not array
- [ ] Includes `organizerName` not just `organizerId`
- [ ] `image` has default if none provided

**Ticket Response:**
- [ ] Includes event details (populated)
- [ ] Has `qrCode` string
- [ ] Has `status` enum value
- [ ] Event image is included

**Error Response:**
```json
{
  "success": false,
  "message": "Error description here"
}
```
- [ ] Always includes `message` field
- [ ] HTTP status code matches error type
- [ ] No stack traces in production

---

## 🔍 Testing Your Backend Responses

Use this curl command to test:

```bash
# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test get events
curl http://localhost:5000/api/events/

# Test with auth token
curl http://localhost:5000/api/tickets/my-tickets \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Or use Postman/Insomnia for easier testing.

---

## 🎯 Priority Fixes

If you're getting errors, fix in this order:

1. **Make sure date is a string** - Most common issue
2. **Return counts not arrays** - For attendees, members
3. **Include populated fields** - organizerName, clubName
4. **Use `id` consistently** - Convert `_id` to `id`
5. **Add CORS** - Allow frontend origin

---

That's everything! Your backend data should now perfectly match what the frontend expects. 🎉
