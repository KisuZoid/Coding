const express = require("express");
const { markAttendance, getAttendance } = require("../controllers/attendanceController");
const {authenticateUser} = require("../middleware/authMiddleware");
const { roleCheck } = require("../middleware/roleMiddleware");
const mongoose = require("mongoose");

const router = express.Router({ mergeParams: true });

// Validate eventId middleware
const validateEventId = (req, res, next) => {
  if (!mongoose.Types.ObjectId.isValid(req.params.eventId)) {
    return res.status(400).json({ message: "Invalid Event ID" });
  }
  next();
};

// ✅ Route: Mark Attendance (Only Attendees)
router.post(
  "/mark/:eventId",
  authenticateUser,
  validateEventId,
  roleCheck(["attendee"]), // Only attendees can mark their attendance
  markAttendance
);

// ✅ Route: Get Attendance Records (Only Admins & Organizers)
router.get(
  "/:eventId",
  authenticateUser,
  validateEventId,
  roleCheck(["admin", "organizer"]), // Only authorized roles can access attendance data
  getAttendance
);

module.exports = router;
