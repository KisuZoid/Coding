# 💳 Payment Integration Guide

## Overview

The Happen platform now supports paid events with a 5% platform commission model. Organizers can set events as free or paid, and the platform automatically handles payment processing and fee calculation.

---

## 🎯 Payment Features

### For Organizers:
- ✅ Set events as **Free** or **Paid**
- ✅ Define custom ticket prices
- ✅ View revenue breakdown (95% to organizer, 5% platform fee)
- ✅ Track paid registrations
- ✅ View payment analytics

### For Users:
- ✅ See event pricing upfront (Free/Paid badge)
- ✅ Secure payment processing
- ✅ Instant ticket generation after payment
- ✅ Payment confirmation in QR ticket

### For Platform:
- ✅ Automatic 5% commission on all paid events
- ✅ Revenue tracking
- ✅ Transaction logs
- ✅ Payment analytics

---

## 📊 Updated Data Structures

### Event Interface (App.tsx)

```typescript
export interface Event {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  organizerId: string;
  organizerName: string;
  category: string;
  image: string;
  attendees: number;
  capacity: number;
  clubId?: string;
  clubName?: string;
  isPaid: boolean;        // NEW: Indicates if event requires payment
  price?: number;         // NEW: Ticket price in USD (if isPaid is true)
}
```

### Ticket Interface (Update needed)

```typescript
export interface Ticket {
  id: string;
  userId: string;
  eventId: string;
  qrCode: string;
  status: 'active' | 'used' | 'expired';
  // NEW payment fields:
  isPaid: boolean;
  amountPaid?: number;
  platformFee?: number;
  transactionId?: string;
  paymentDate?: Date;
}
```

---

## 💰 Revenue Model

### Commission Structure:
```
Event Price:        $25.00
Platform Fee (5%):   $1.25
Organizer Receives: $23.75
Total User Pays:    $26.25
```

### Fee Calculation:
```typescript
const eventPrice = 25.00;
const platformFee = eventPrice * 0.05;  // 5%
const organizerRevenue = eventPrice * 0.95;  // 95%
const totalUserPays = eventPrice + platformFee;
```

---

## 🔧 Frontend Implementation

### 1. Login with Role Selection

**File:** `/components/Login.tsx`

**Features:**
- ✅ Dropdown to select role (User, Organizer, Admin)
- ✅ Auto-detect role from email
  - Email with "admin" → Admin role
  - Email with "organizer" → Organizer role
  - Other emails → User role
- ✅ Visual feedback showing detected role

**Usage:**
```typescript
// Auto-detect mode (default)
email: "john.organizer@college.edu" → Role: Organizer

// Manual selection
Selected: "Administrator" → Login as Admin
```

---

### 2. Event Creation with Pricing

**Files:** 
- `/components/OrganizerDashboard.tsx`
- `/components/AdminDashboard.tsx`

**Features:**
- ✅ Toggle for Paid/Free events
- ✅ Price input field (appears when paid is selected)
- ✅ Live platform fee calculation
- ✅ Shows organizer's net revenue

**Form Fields:**
```typescript
{
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  category: string;
  capacity: number;
  isPaid: boolean;      // NEW
  price: number;        // NEW (optional, required if isPaid)
}
```

---

### 3. Payment Flow (EventDetails.tsx)

**User Journey:**

```
1. User views event
   ├─ Free Event → Click "Register for Free" → Get QR Ticket
   └─ Paid Event → Click "Register ($25.00)" → Payment Dialog

2. Payment Dialog Opens
   ├─ Shows price breakdown
   ├─ Platform fee (5%)
   ├─ Total amount
   ├─ Payment form (card details)
   └─ Submit Payment

3. Payment Processing
   ├─ Validate card details
   ├─ Process payment (Stripe/Backend)
   ├─ Generate ticket
   └─ Show QR Code

4. Confirmation
   ├─ QR ticket with "Paid" badge
   └─ Payment confirmation toast
```

**Payment Dialog Components:**
- Card holder name input
- Card number input (with icon)
- Expiry date input (MM/YY)
- CVV input (secure)
- Price breakdown card
- Submit button with total

---

### 4. Event Display with Pricing

**File:** `/components/UserDashboard.tsx`

**Visual Indicators:**
- 🟢 **Free Events:** Blue "Free" badge
- 💵 **Paid Events:** Green "$25.00" badge

**Example:**
```jsx
{event.isPaid ? (
  <Badge className="bg-green-500/90 text-white">
    ${event.price?.toFixed(2)}
  </Badge>
) : (
  <Badge className="bg-blue-500/90 text-white">
    Free
  </Badge>
)}
```

---

## 🔌 Backend Integration Required

### New/Updated Endpoints

#### 1. Create Event with Pricing
```
POST /api/events/create

Request:
{
  "title": "Tech Workshop",
  "description": "...",
  "date": "2025-10-15",
  "time": "18:00",
  "location": "Room 301",
  "category": "Technology",
  "capacity": 100,
  "isPaid": true,
  "price": 25.00
}

Response:
{
  "success": true,
  "event": {
    "_id": "...",
    "title": "Tech Workshop",
    ...
    "isPaid": true,
    "price": 25.00
  }
}
```

#### 2. Process Payment
```
POST /api/payments/process

Headers:
Authorization: Bearer {jwt_token}

Request:
{
  "eventId": "event_123",
  "amount": 26.25,
  "platformFee": 1.25,
  "cardDetails": {
    "number": "4242424242424242",
    "expMonth": "12",
    "expYear": "2025",
    "cvc": "123",
    "name": "John Doe"
  }
}

Response:
{
  "success": true,
  "transactionId": "txn_abc123",
  "ticketId": "ticket_xyz789",
  "qrCode": "QR-123-ABC"
}
```

#### 3. Get Payment Analytics (Organizer)
```
GET /api/payments/organizer/analytics

Headers:
Authorization: Bearer {jwt_token}

Response:
{
  "success": true,
  "analytics": {
    "totalRevenue": 2375.00,
    "platformFeesCollected": 125.00,
    "totalTransactions": 100,
    "averageTicketPrice": 25.00
  }
}
```

#### 4. Get Platform Revenue (Admin)
```
GET /api/payments/admin/revenue

Headers:
Authorization: Bearer {jwt_token}

Response:
{
  "success": true,
  "revenue": {
    "totalPlatformFees": 15250.00,
    "totalTransactions": 5420,
    "monthlyRevenue": {
      "2025-10": 1525.00,
      "2025-09": 1350.00
    }
  }
}
```

---

## 💳 Payment Gateway Integration

### Recommended: Stripe

**Why Stripe?**
- PCI compliant (handles card data securely)
- Easy integration
- Test mode for development
- Comprehensive documentation
- Automatic fee handling

### Setup Steps:

#### 1. Install Stripe
```bash
npm install stripe
npm install @stripe/stripe-js
```

#### 2. Backend Configuration
```javascript
// backend/config/stripe.js
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

module.exports = stripe;
```

#### 3. Create Payment Intent
```javascript
// backend/controllers/paymentController.js
const stripe = require('../config/stripe');

exports.createPaymentIntent = async (req, res) => {
  try {
    const { amount, eventId } = req.body;
    
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(amount * 100), // Convert to cents
      currency: 'usd',
      metadata: {
        eventId,
        userId: req.user.id
      }
    });
    
    res.json({
      success: true,
      clientSecret: paymentIntent.client_secret
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
```

#### 4. Frontend Stripe Integration
```typescript
// frontend/services/stripe.ts
import { loadStripe } from '@stripe/stripe-js';

export const stripePromise = loadStripe(
  process.env.REACT_APP_STRIPE_PUBLIC_KEY!
);
```

---

## 🗄️ Database Schema Updates

### Event Model
```javascript
// backend/models/eventModel.js
{
  // ... existing fields
  isPaid: {
    type: Boolean,
    default: false
  },
  price: {
    type: Number,
    required: function() { return this.isPaid; },
    min: 0
  },
  revenue: {
    type: Number,
    default: 0
  },
  platformFeesCollected: {
    type: Number,
    default: 0
  }
}
```

### Payment Model (NEW)
```javascript
// backend/models/paymentModel.js
const mongoose = require('mongoose');

const paymentSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  eventId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Event',
    required: true
  },
  ticketId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Ticket',
    required: true
  },
  amount: {
    type: Number,
    required: true
  },
  platformFee: {
    type: Number,
    required: true
  },
  organizerAmount: {
    type: Number,
    required: true
  },
  transactionId: {
    type: String,
    required: true,
    unique: true
  },
  paymentMethod: {
    type: String,
    default: 'card'
  },
  status: {
    type: String,
    enum: ['pending', 'completed', 'failed', 'refunded'],
    default: 'pending'
  },
  stripePaymentIntentId: String,
  paymentDate: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Payment', paymentSchema);
```

### Ticket Model Update
```javascript
// backend/models/ticketModel.js
{
  // ... existing fields
  isPaid: {
    type: Boolean,
    default: false
  },
  paymentId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Payment'
  }
}
```

---

## 🔒 Security Considerations

### 1. Never Store Card Details
- ❌ Do NOT store full card numbers
- ❌ Do NOT store CVV codes
- ✅ Use Stripe tokens instead
- ✅ Store only last 4 digits for reference

### 2. Validate Amounts
```javascript
// Backend validation
if (amount !== event.price + (event.price * 0.05)) {
  return res.status(400).json({ 
    message: 'Payment amount mismatch' 
  });
}
```

### 3. Verify Payment Before Ticket
```javascript
// Only generate ticket after payment confirmation
const paymentIntent = await stripe.paymentIntents.retrieve(intentId);

if (paymentIntent.status === 'succeeded') {
  // Generate ticket
  const ticket = await Ticket.create({ ... });
} else {
  return res.status(400).json({ 
    message: 'Payment not completed' 
  });
}
```

### 4. Idempotency
```javascript
// Prevent duplicate charges
const existingPayment = await Payment.findOne({
  userId,
  eventId,
  status: 'completed'
});

if (existingPayment) {
  return res.status(400).json({ 
    message: 'Already registered for this event' 
  });
}
```

---

## 📈 Analytics & Reporting

### Revenue Dashboard (Admin)

**Metrics to Track:**
- Total platform fees collected
- Total transactions
- Average ticket price
- Monthly revenue trends
- Top revenue-generating events
- Top-earning organizers

### Organizer Dashboard

**Metrics to Show:**
- Total earnings (after platform fee)
- Number of paid tickets sold
- Average ticket price
- Revenue per event
- Payment history

### Frontend Implementation:
```typescript
// components/AdminDashboard.tsx - Add to analytics tab
<Card className="p-6">
  <h3 className="mb-4">Platform Revenue</h3>
  <div className="space-y-4">
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">Total Fees Collected</span>
      <span className="text-2xl font-semibold">$15,250.00</span>
    </div>
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">This Month</span>
      <span className="text-xl">$1,525.00</span>
    </div>
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">Total Transactions</span>
      <span>5,420</span>
    </div>
  </div>
</Card>
```

---

## 🧪 Testing

### Test Cards (Stripe Test Mode):

```
✅ Success:
4242 4242 4242 4242  (any future expiry, any CVC)

❌ Declined:
4000 0000 0000 0002

🕐 Requires Authentication:
4000 0025 0000 3155

💳 Insufficient Funds:
4000 0000 0000 9995
```

### Test Scenarios:

1. **Free Event Registration**
   - Create free event
   - Register without payment
   - Verify QR ticket generated

2. **Paid Event Registration**
   - Create paid event ($25.00)
   - Register with test card
   - Verify payment of $26.25 (with 5% fee)
   - Verify QR ticket shows "Paid" badge

3. **Payment Failure**
   - Use declined test card
   - Verify error handling
   - User not registered

4. **Role-Based Access**
   - Organizer can create paid events
   - User can pay for events
   - Admin can view all revenue

---

## 🚀 Deployment Checklist

### Before Production:

- [ ] Switch to Stripe live keys
- [ ] Enable HTTPS (required for Stripe)
- [ ] Set up webhook endpoints for payment confirmations
- [ ] Configure refund policy
- [ ] Test all payment flows thoroughly
- [ ] Set up payment failure notifications
- [ ] Configure email receipts
- [ ] Set up revenue reconciliation process
- [ ] Implement payout system for organizers
- [ ] Add terms of service for paid events

### Environment Variables:

```bash
# Backend
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Frontend
REACT_APP_STRIPE_PUBLIC_KEY=pk_live_...
```

---

## 📧 Email Notifications

### Payment Confirmation Email

```
Subject: Payment Received - [Event Name]

Hi [User Name],

Thank you for your payment of $26.25 for [Event Name].

Payment Details:
- Event Price: $25.00
- Platform Fee: $1.25
- Total Paid: $26.25
- Transaction ID: TXN-123456

Your QR ticket is attached. Show this at the event entrance.

Event Details:
- Date: October 15, 2025
- Time: 6:00 PM
- Location: Engineering Building, Room 301

See you there!

---
The Happen Team
```

---

## 💡 Future Enhancements

1. **Refund System**
   - Allow organizers to issue refunds
   - Partial refund support
   - Automated refund processing

2. **Discount Codes**
   - Percentage discounts
   - Fixed amount discounts
   - Limited use codes

3. **Early Bird Pricing**
   - Time-based pricing tiers
   - Automatic price updates

4. **Group Tickets**
   - Bulk purchase discounts
   - Team registration

5. **Split Payments**
   - Multiple organizers share revenue
   - Custom split percentages

6. **Recurring Events**
   - Subscription model
   - Season passes

---

## 🆘 Support

For payment integration help:
- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- PCI Compliance: https://stripe.com/docs/security

---

That's everything you need to implement payments! 💳✨
