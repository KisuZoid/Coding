# 🔨 Backend Code Examples

This file contains code examples for endpoints you need to add to your backend.

## 📁 File Structure Your Backend Should Have

```
backend/
├── config/
│   └── db.js
├── controllers/
│   ├── authController.js
│   ├── eventController.js
│   ├── qrController.js
│   ├── ticketController.js
│   ├── userController.js
│   ├── attendanceController.js
│   ├── clubController.js          ← ADD THIS
│   └── analyticsController.js     ← ADD THIS
├── middleware/
│   ├── authMiddleware.js
│   ├── roleMiddleware.js
│   └── errorHandler.js
├── models/
│   ├── eventModel.js
│   ├── qrModel.js
│   ├── ticketModel.js
│   ├── userModel.js
│   ├── attendanceModel.js
│   └── clubModel.js               ← ADD THIS
├── routes/
│   ├── authRoutes.js
│   ├── eventRoutes.js
│   ├── qrRoutes.js
│   ├── ticketRoutes.js
│   ├── userRoutes.js
│   ├── attendanceRoutes.js
│   ├── clubRoutes.js              ← ADD THIS
│   └── analyticsRoutes.js         ← ADD THIS
├── utils/
│   ├── emailService.js
│   ├── jwtUtils.js
│   ├── hashUtils.js
│   └── qrUtils.js
├── .env
├── package.json
├── app.js
└── index.js
```

---

## 1️⃣ Add Missing Auth Endpoints

### File: `controllers/authController.js`

Add these functions:

```javascript
// GET /api/auth/me - Get current user
exports.getCurrentUser = async (req, res) => {
  try {
    // req.user is set by authMiddleware
    const user = await User.findById(req.user.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.status(200).json({
      success: true,
      user: {
        _id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        verified: user.verified,
        organizationId: user.organizationId
      }
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// POST /api/auth/reset-password/confirm
exports.confirmPasswordReset = async (req, res) => {
  try {
    const { token, newPassword } = req.body;

    // Find user by reset token (you need to add resetToken field to User model)
    const user = await User.findOne({
      resetPasswordToken: token,
      resetPasswordExpires: { $gt: Date.now() }
    });

    if (!user) {
      return res.status(400).json({ message: 'Invalid or expired token' });
    }

    // Hash new password
    const bcrypt = require('bcrypt');
    user.password = await bcrypt.hash(newPassword, 10);
    user.resetPasswordToken = undefined;
    user.resetPasswordExpires = undefined;
    await user.save();

    res.status(200).json({
      success: true,
      message: 'Password reset successful'
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
```

### File: `routes/authRoutes.js`

Add these routes:

```javascript
const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const { protect } = require('../middleware/authMiddleware');

// Existing routes
router.post('/register', authController.register);
router.post('/login', authController.login);
router.get('/verify/:token', authController.verifyEmail);
router.post('/reset-password', authController.requestPasswordReset);

// NEW ROUTES - Add these
router.get('/me', protect, authController.getCurrentUser);
router.post('/reset-password/confirm', authController.confirmPasswordReset);

module.exports = router;
```

---

## 2️⃣ Add Missing Event Endpoints

### File: `controllers/eventController.js`

Add these functions:

```javascript
// GET /api/events/:id
exports.getEventById = async (req, res) => {
  try {
    const event = await Event.findById(req.params.id)
      .populate('organizerId', 'name email')
      .populate('clubId', 'name');

    if (!event) {
      return res.status(404).json({ message: 'Event not found' });
    }

    res.status(200).json({
      success: true,
      event: {
        id: event._id,
        title: event.title,
        description: event.description,
        date: event.date,
        time: event.time,
        location: event.location,
        organizerId: event.organizerId._id,
        organizerName: event.organizerId.name,
        category: event.category,
        image: event.image,
        attendees: event.attendees.length,
        capacity: event.capacity,
        clubId: event.clubId?._id,
        clubName: event.clubId?.name
      }
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// PUT /api/events/:id
exports.updateEvent = async (req, res) => {
  try {
    const event = await Event.findById(req.params.id);

    if (!event) {
      return res.status(404).json({ message: 'Event not found' });
    }

    // Check if user is organizer of this event or admin
    if (event.organizerId.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Not authorized to update this event' });
    }

    const updatedEvent = await Event.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    res.status(200).json({
      success: true,
      event: updatedEvent
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// DELETE /api/events/:id
exports.deleteEvent = async (req, res) => {
  try {
    const event = await Event.findById(req.params.id);

    if (!event) {
      return res.status(404).json({ message: 'Event not found' });
    }

    // Check authorization
    if (event.organizerId.toString() !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ message: 'Not authorized to delete this event' });
    }

    await event.deleteOne();

    res.status(200).json({
      success: true,
      message: 'Event deleted successfully'
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// GET /api/events/organizer/my-events
exports.getOrganizerEvents = async (req, res) => {
  try {
    const events = await Event.find({ organizerId: req.user.id })
      .sort({ date: 1 });

    res.status(200).json({
      success: true,
      count: events.length,
      events
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// GET /api/events/user/registered
exports.getUserRegisteredEvents = async (req, res) => {
  try {
    // Find all tickets for this user
    const Ticket = require('../models/ticketModel');
    const tickets = await Ticket.find({ userId: req.user.id })
      .populate('eventId');

    const events = tickets.map(ticket => ticket.eventId);

    res.status(200).json({
      success: true,
      count: events.length,
      events
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
```

### File: `routes/eventRoutes.js`

Update your routes:

```javascript
const express = require('express');
const router = express.Router();
const eventController = require('../controllers/eventController');
const { protect } = require('../middleware/authMiddleware');
const { authorize } = require('../middleware/roleMiddleware');

// Public routes
router.get('/', eventController.getAllEvents);
router.get('/:id', eventController.getEventById);

// Protected routes
router.post('/create', protect, authorize('organizer', 'admin'), eventController.createEvent);
router.put('/:id', protect, authorize('organizer', 'admin'), eventController.updateEvent);
router.delete('/:id', protect, authorize('organizer', 'admin'), eventController.deleteEvent);

// User routes
router.get('/organizer/my-events', protect, authorize('organizer', 'admin'), eventController.getOrganizerEvents);
router.get('/user/registered', protect, eventController.getUserRegisteredEvents);

module.exports = router;
```

---

## 3️⃣ Create Club System

### File: `models/clubModel.js`

Create new file:

```javascript
const mongoose = require('mongoose');

const clubSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Club name is required'],
    unique: true
  },
  description: {
    type: String,
    required: true
  },
  category: {
    type: String,
    required: true,
    enum: ['Technology', 'Arts', 'Sports', 'Business', 'Wellness', 'Entertainment', 'Other']
  },
  image: String,
  coverImage: String,
  foundedYear: Number,
  email: {
    type: String,
    required: true
  },
  website: String,
  socials: {
    instagram: String,
    discord: String,
    twitter: String
  },
  organizerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  members: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  events: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Event'
  }],
  posts: [{
    content: String,
    image: String,
    date: Date,
    likes: { type: Number, default: 0 }
  }]
}, {
  timestamps: true
});

module.exports = mongoose.model('Club', clubSchema);
```

### File: `controllers/clubController.js`

Create new file:

```javascript
const Club = require('../models/clubModel');

// GET /api/clubs - Get all clubs
exports.getAllClubs = async (req, res) => {
  try {
    const clubs = await Club.find()
      .populate('organizerId', 'name email')
      .select('-posts');  // Don't send posts in list view

    const clubsWithStats = clubs.map(club => ({
      id: club._id,
      name: club.name,
      description: club.description,
      category: club.category,
      image: club.image,
      memberCount: club.members.length,
      events: club.events.length
    }));

    res.status(200).json({
      success: true,
      count: clubsWithStats.length,
      clubs: clubsWithStats
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// GET /api/clubs/:id - Get club by ID
exports.getClubById = async (req, res) => {
  try {
    const club = await Club.findById(req.params.id)
      .populate('organizerId', 'name email')
      .populate('events')
      .populate('members', 'name email');

    if (!club) {
      return res.status(404).json({ message: 'Club not found' });
    }

    res.status(200).json({
      success: true,
      club
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// POST /api/clubs/create - Create new club
exports.createClub = async (req, res) => {
  try {
    const clubData = {
      ...req.body,
      organizerId: req.user.id,
      members: [req.user.id]  // Creator is first member
    };

    const club = await Club.create(clubData);

    // Update user's organizationId
    const User = require('../models/userModel');
    await User.findByIdAndUpdate(req.user.id, {
      organizationId: club._id
    });

    res.status(201).json({
      success: true,
      club
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// POST /api/clubs/:id/join - Join a club
exports.joinClub = async (req, res) => {
  try {
    const club = await Club.findById(req.params.id);

    if (!club) {
      return res.status(404).json({ message: 'Club not found' });
    }

    // Check if already a member
    if (club.members.includes(req.user.id)) {
      return res.status(400).json({ message: 'Already a member' });
    }

    club.members.push(req.user.id);
    await club.save();

    res.status(200).json({
      success: true,
      message: 'Successfully joined club'
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// POST /api/clubs/:id/leave - Leave a club
exports.leaveClub = async (req, res) => {
  try {
    const club = await Club.findById(req.params.id);

    if (!club) {
      return res.status(404).json({ message: 'Club not found' });
    }

    // Remove user from members
    club.members = club.members.filter(
      memberId => memberId.toString() !== req.user.id
    );
    await club.save();

    res.status(200).json({
      success: true,
      message: 'Successfully left club'
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// GET /api/clubs/:id/events - Get club events
exports.getClubEvents = async (req, res) => {
  try {
    const Event = require('../models/eventModel');
    const events = await Event.find({ clubId: req.params.id })
      .sort({ date: 1 });

    res.status(200).json({
      success: true,
      count: events.length,
      events
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// GET /api/clubs/:id/posts - Get club posts
exports.getClubPosts = async (req, res) => {
  try {
    const club = await Club.findById(req.params.id).select('posts');

    if (!club) {
      return res.status(404).json({ message: 'Club not found' });
    }

    res.status(200).json({
      success: true,
      posts: club.posts.sort((a, b) => b.date - a.date)
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

module.exports = exports;
```

### File: `routes/clubRoutes.js`

Create new file:

```javascript
const express = require('express');
const router = express.Router();
const clubController = require('../controllers/clubController');
const { protect } = require('../middleware/authMiddleware');
const { authorize } = require('../middleware/roleMiddleware');

// Public routes
router.get('/', clubController.getAllClubs);
router.get('/:id', clubController.getClubById);
router.get('/:id/events', clubController.getClubEvents);
router.get('/:id/posts', clubController.getClubPosts);

// Protected routes
router.post('/create', protect, authorize('organizer', 'admin'), clubController.createClub);
router.post('/:id/join', protect, clubController.joinClub);
router.post('/:id/leave', protect, clubController.leaveClub);

module.exports = router;
```

---

## 4️⃣ Add User Management (Admin)

### File: `controllers/userController.js`

Update or create:

```javascript
const User = require('../models/userModel');

// GET /api/users - Get all users (Admin only)
exports.getAllUsers = async (req, res) => {
  try {
    const users = await User.find().select('-password');

    const usersWithStats = await Promise.all(
      users.map(async (user) => {
        const Attendance = require('../models/attendanceModel');
        const attendanceCount = await Attendance.countDocuments({ userId: user._id });

        return {
          id: user._id,
          name: user.name,
          email: user.email,
          role: user.role,
          verified: user.verified,
          eventsAttended: attendanceCount,
          createdAt: user.createdAt
        };
      })
    );

    res.status(200).json({
      success: true,
      count: usersWithStats.length,
      users: usersWithStats
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// PUT /api/users/:id/role - Update user role (Admin only)
exports.updateUserRole = async (req, res) => {
  try {
    const { role } = req.body;

    if (!['user', 'organizer', 'admin'].includes(role)) {
      return res.status(400).json({ message: 'Invalid role' });
    }

    const user = await User.findByIdAndUpdate(
      req.params.id,
      { role },
      { new: true }
    ).select('-password');

    res.status(200).json({
      success: true,
      user
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// DELETE /api/users/:id - Delete user (Admin only)
exports.deleteUser = async (req, res) => {
  try {
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Don't allow deleting yourself
    if (user._id.toString() === req.user.id) {
      return res.status(400).json({ message: 'Cannot delete your own account' });
    }

    await user.deleteOne();

    res.status(200).json({
      success: true,
      message: 'User deleted successfully'
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

module.exports = exports;
```

### File: `routes/userRoutes.js`

Create or update:

```javascript
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const { protect } = require('../middleware/authMiddleware');
const { authorize } = require('../middleware/roleMiddleware');

// Admin only routes
router.get('/', protect, authorize('admin'), userController.getAllUsers);
router.put('/:id/role', protect, authorize('admin'), userController.updateUserRole);
router.delete('/:id', protect, authorize('admin'), userController.deleteUser);

module.exports = router;
```

---

## 5️⃣ Update Main App File

### File: `app.js`

Make sure you have CORS and all routes:

```javascript
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');
require('dotenv').config();

const app = express();

// Connect to database
connectDB();

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/events', require('./routes/eventRoutes'));
app.use('/api/tickets', require('./routes/ticketRoutes'));
app.use('/api/qr', require('./routes/qrRoutes'));
app.use('/api/attendance', require('./routes/attendanceRoutes'));
app.use('/api/users', require('./routes/userRoutes'));
app.use('/api/clubs', require('./routes/clubRoutes'));  // ADD THIS

// Error handling middleware
app.use(require('./middleware/errorHandler'));

module.exports = app;
```

---

## 6️⃣ Add Ticket Endpoints

### File: `controllers/ticketController.js`

Add:

```javascript
// GET /api/tickets/my-tickets
exports.getUserTickets = async (req, res) => {
  try {
    const Ticket = require('../models/ticketModel');
    const tickets = await Ticket.find({ userId: req.user.id })
      .populate('eventId')
      .sort({ createdAt: -1 });

    const formattedTickets = tickets.map(ticket => ({
      id: ticket._id,
      eventId: ticket.eventId._id,
      eventTitle: ticket.eventId.title,
      date: ticket.eventId.date,
      time: ticket.eventId.time,
      location: ticket.eventId.location,
      organizer: ticket.eventId.organizerName,
      qrCode: ticket.qrCode,
      status: ticket.status,
      image: ticket.eventId.image
    }));

    res.status(200).json({
      success: true,
      count: formattedTickets.length,
      tickets: formattedTickets
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
```

---

## 🔄 Quick Integration Checklist

1. **Add these files to your backend:**
   - [ ] `models/clubModel.js`
   - [ ] `controllers/clubController.js`
   - [ ] `routes/clubRoutes.js`

2. **Update these files:**
   - [ ] `controllers/authController.js` - Add getCurrentUser, confirmPasswordReset
   - [ ] `controllers/eventController.js` - Add getEventById, updateEvent, deleteEvent
   - [ ] `controllers/ticketController.js` - Add getUserTickets
   - [ ] `controllers/userController.js` - Add admin functions
   - [ ] `routes/authRoutes.js` - Add new routes
   - [ ] `routes/eventRoutes.js` - Add new routes
   - [ ] `routes/userRoutes.js` - Add new routes
   - [ ] `app.js` - Add clubRoutes and CORS

3. **Update your User model to include:**
   ```javascript
   organizationId: { type: ObjectId, ref: 'Club' }
   ```

4. **Test with Postman:**
   - Register user
   - Login
   - Create event
   - Generate ticket
   - Get my tickets

---

That's it! Your backend is now ready to work with the React frontend. 🎉
