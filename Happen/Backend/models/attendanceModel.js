const mongoose = require("mongoose");

const attendanceSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  eventId: { type: mongoose.Schema.Types.ObjectId, ref: "Event", required: true },
  timestamp: { type: Date, default: Date.now }
});

// Compound Index: Prevents duplicate attendance & optimizes queries
attendanceSchema.index({ userId: 1, eventId: 1 }, { unique: true });
attendanceSchema.index({ timestamp: 1 });

// Log index creation status
attendanceSchema.on('index', (err) => {
  if (err) console.error("❌ Attendance index creation failed:", err);
  else console.log("✅ Attendance indexes created successfully!");
});

module.exports = mongoose.model("Attendance", attendanceSchema);
