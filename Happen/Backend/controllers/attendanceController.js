const Attendance = require("../models/attendanceModel");
const mongoose = require("mongoose");

exports.markAttendance = async (req, res) => {
  try {
    const { userId, eventId } = req.body;

    // Validate input
    if (!userId || !eventId) {
      return res.status(400).json({ message: "User ID and Event ID are required" });
    }

    // Ensure valid MongoDB ObjectId
    if (!mongoose.isValidObjectId(userId) || !mongoose.isValidObjectId(eventId)) {
      return res.status(400).json({ message: "Invalid User ID or Event ID" });
    }

    // Check if attendance is already marked
    const alreadyMarked = await Attendance.findOne({ userId, eventId });
    if (alreadyMarked) {
      return res.status(400).json({ message: "Attendance already marked" });
    }

    // Mark attendance
    const attendance = new Attendance({ userId, eventId });
    await attendance.save();

    res.json({ message: "✅ Attendance marked successfully!" });
  } catch (error) {
    res.status(500).json({ message: "❌ Server error", error: error.message });
  }
};

exports.getAttendance = async (req, res) => {
  try {
    const attendance = await Attendance.find()
      .populate("userId", "name email")
      .populate("eventId", "title");

    res.json(attendance);
  } catch (error) {
    res.status(500).json({ message: "❌ Server error", error: error.message });
  }
};
