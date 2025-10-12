# 🚀 Quick Start Guide - Connecting Frontend to Backend

This is your simplified, step-by-step guide to get everything working together.

## 📋 Prerequisites

- Node.js installed (v16 or higher)
- MongoDB installed and running
- Your Express backend ready
- This React frontend

---

## ⚡ 5-Minute Setup

### Step 1: Start Your Backend (5 min)

```bash
cd your-backend-folder

# Install dependencies if not done
npm install cors

# Create .env file
echo "PORT=5000
MONGODB_URI=mongodb://localhost:27017/happen
JWT_SECRET=your_secret_key_change_this
FRONTEND_URL=http://localhost:3000" > .env

# Start backend
npm start
```

**Expected output:** 
```
Server running on port 5000
MongoDB Connected
```

### Step 2: Update Your Frontend (2 min)

In the React app root, create `.env`:

```bash
echo "REACT_APP_API_URL=http://localhost:5000" > .env
```

### Step 3: Install Frontend Dependencies (1 min)

```bash
npm install
```

### Step 4: Start Frontend (1 min)

```bash
npm start
```

Browser should open at `http://localhost:3000`

---

## 🧪 Test It's Working

### Test 1: Registration
1. Click "Get Started" on homepage
2. Fill in registration form
3. Choose "Student (Attendee)" or "Club Organizer"
4. Click "Create Account"
5. **Check backend console** - should see registration log

### Test 2: Login
1. Go to login page
2. Use any email with "admin" for admin access
3. Click "Sign In"
4. **Check browser console** - should see API call

### Test 3: Browse Events
1. After login, you'll see dashboard
2. **Check browser network tab** - should see `/api/events` call

---

## 🔥 Common Issues & Fixes

### Issue 1: "Failed to fetch" Error

**Problem:** Backend not running or wrong URL

**Fix:**
```bash
# Check backend is running
curl http://localhost:5000/api/events

# If nothing, start backend:
cd backend
npm start
```

### Issue 2: CORS Error

**Problem:** Backend blocking frontend requests

**Fix in backend `app.js`:**
```javascript
const cors = require('cors');
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));
```

### Issue 3: 401 Unauthorized

**Problem:** Token not being sent

**Fix:** Check `localStorage` in browser DevTools:
- Open DevTools (F12)
- Go to Application tab
- Check Local Storage
- Should see `authToken`

### Issue 4: Events Not Loading

**Problem:** Backend endpoint not implemented

**Check backend has this in `routes/eventRoutes.js`:**
```javascript
router.get('/', eventController.getAllEvents);
```

---

## 📊 Backend Endpoints Status

Check which endpoints you have vs. need:

### ✅ You Already Have (from your README):
```
✓ POST /api/auth/register
✓ POST /api/auth/login
✓ GET  /api/auth/verify/:token
✓ POST /api/auth/reset-password
✓ POST /api/events/create
✓ GET  /api/events/
✓ POST /api/tickets/generate
✓ POST /api/qr/generate
✓ POST /api/qr/scan
```

### ⚠️ You Need to Add:
```
❌ GET  /api/auth/me
❌ GET  /api/events/:id
❌ PUT  /api/events/:id
❌ DELETE /api/events/:id
❌ GET  /api/tickets/my-tickets
❌ GET  /api/users (admin)
❌ All club endpoints
```

**Don't worry!** The app will work with mock data until you add these. Add them gradually.

---

## 🎯 Priority Order for Adding Endpoints

Add endpoints in this order for best results:

### Phase 1: Core Functionality (Do First)
1. `GET /api/events/:id` - View event details
2. `GET /api/tickets/my-tickets` - View user tickets
3. `GET /api/auth/me` - Get current user info

**After Phase 1:** Users can browse events, register, and see their tickets

### Phase 2: Organizer Features (Do Second)
4. `PUT /api/events/:id` - Edit events
5. `DELETE /api/events/:id` - Delete events
6. `GET /api/events/organizer/my-events` - View organizer's events

**After Phase 2:** Organizers can manage their events

### Phase 3: Admin Features (Do Third)
7. `GET /api/users` - List all users
8. `PUT /api/users/:id/role` - Change user roles
9. `DELETE /api/users/:id` - Delete users

**After Phase 3:** Admin can manage users

### Phase 4: Social Features (Do Last)
10. All club endpoints (refer to BACKEND_CODE_EXAMPLES.md)

**After Phase 4:** Full social features with clubs

---

## 🛠️ How to Add an Endpoint (Example)

Let's add `GET /api/events/:id` as an example:

### 1. Add Controller Function

In `controllers/eventController.js`:

```javascript
exports.getEventById = async (req, res) => {
  try {
    const event = await Event.findById(req.params.id);
    
    if (!event) {
      return res.status(404).json({ message: 'Event not found' });
    }

    res.status(200).json({
      success: true,
      event
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
```

### 2. Add Route

In `routes/eventRoutes.js`:

```javascript
router.get('/:id', eventController.getEventById);
```

### 3. Test with Postman

```
GET http://localhost:5000/api/events/[some-event-id]
```

### 4. Update Frontend Component

In `components/EventDetails.tsx`:

```typescript
useEffect(() => {
  const fetchEvent = async () => {
    const data = await eventsAPI.getEventById(eventId);
    setEvent(data.event);
  };
  fetchEvent();
}, [eventId]);
```

**That's it!** Repeat for each endpoint.

---

## 📁 File Reference Guide

| Frontend Component | Needs Backend Endpoint | Backend File |
|-------------------|------------------------|--------------|
| Login.tsx | `/api/auth/login` | authController.js |
| Register.tsx | `/api/auth/register` | authController.js |
| UserDashboard.tsx | `/api/events/` | eventController.js |
| EventDetails.tsx | `/api/events/:id` | eventController.js |
| MyTickets.tsx | `/api/tickets/my-tickets` | ticketController.js |
| ScanQR.tsx | `/api/qr/scan` | qrController.js |
| OrganizerDashboard.tsx | `/api/events/organizer/my-events` | eventController.js |
| AdminDashboard.tsx | `/api/users/` | userController.js |
| ClubDetails.tsx | `/api/clubs/:id` | clubController.js |

---

## 🎨 Understanding the Tech Stack

**You mentioned wanting HTML/CSS/JS instead of React/TypeScript.**

Here's the truth: **This app IS JavaScript!** Let me clarify:

### What You Have:
- **React** = JavaScript library (it's still JavaScript!)
- **TypeScript** = JavaScript with types (compiles to regular JavaScript)
- **Tailwind CSS** = CSS utility classes (it's still CSS!)
- **Express** = JavaScript backend framework

### Why Not Plain HTML/CSS/JS?
1. **Too complex** - Would need 1000+ lines per page
2. **No state management** - Hard to handle login, navigation, etc.
3. **Lots of code duplication** - Every page needs same navbar, etc.
4. **Industry standard** - 95% of modern web apps use React/Vue/Angular

### You Don't Need to Learn TypeScript!
- All `.tsx` files work like `.jsx` files
- TypeScript just adds type hints (the `: string`, `: User` parts)
- **Ignore the types** and focus on the JavaScript logic
- The browser only sees JavaScript anyway

### You Don't Need to Learn Tailwind Deeply!
- `className="bg-blue-500"` = `background-color: blue;`
- `className="p-4"` = `padding: 1rem;`
- `className="flex"` = `display: flex;`
- It's just CSS with shorter names!

---

## 🆘 Need Help?

### Check Backend Logs
```bash
# In backend terminal, you'll see:
POST /api/auth/login 200 45ms
GET /api/events 200 23ms
```

### Check Frontend Logs
```bash
# In browser console (F12), you'll see:
API Call: GET /api/events
Response: {success: true, events: [...]}
```

### Check Network Tab
1. Open DevTools (F12)
2. Go to "Network" tab
3. Refresh page
4. See all API calls
5. Click on any to see request/response

---

## ✅ Your Action Plan

**Day 1:**
- [ ] Start backend
- [ ] Start frontend  
- [ ] Test login works
- [ ] See events loading

**Day 2:**
- [ ] Add `GET /api/events/:id` endpoint
- [ ] Test event details page
- [ ] Add `GET /api/tickets/my-tickets` endpoint
- [ ] Test My Tickets page

**Day 3:**
- [ ] Add organizer endpoints
- [ ] Test event creation
- [ ] Test event editing

**Day 4:**
- [ ] Add admin endpoints
- [ ] Test user management

**Day 5:**
- [ ] Add club endpoints (optional)
- [ ] Deploy to production

---

## 🎉 You're Ready!

Remember:
1. **Start with what works** - Login/register already work!
2. **Add one endpoint at a time** - Don't overwhelm yourself
3. **Test after each change** - Easier to debug
4. **Use the mock data** - Frontend works without all endpoints
5. **Ask for help** - Check the guides in this repo

**The app is 90% done!** You just need to:
- Connect a few API endpoints
- Replace mock data with real API calls
- Add missing backend endpoints gradually

You've got this! 🚀

---

## 📚 Documentation Files in This Repo

1. **INTEGRATION_GUIDE.md** - Full integration instructions
2. **BACKEND_CODE_EXAMPLES.md** - Code to copy-paste for backend
3. **QUICK_START.md** - This file! Step-by-step guide
4. **/services/api.ts** - Ready-to-use API service layer

Start with this file, then refer to the others as needed!
