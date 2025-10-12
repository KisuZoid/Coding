const mongoose = require("mongoose");

// Helper function to capitalize each word in title
const toTitleCase = (str) => str.replace(/\b\w/g, (char) => char.toUpperCase());

const eventSchema = new mongoose.Schema(
  {
    title: { 
      type: String, 
      required: true, 
      set: toTitleCase 
    },
    date: { 
      type: Date, 
      required: true, 
      validate: {
        validator: (value) => value >= new Date(), 
        message: "Event date must be in the future."
      }
    },
    location: { type: String, required: true },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true }
  },
  { timestamps: true }
);

// Indexes for optimized querying
eventSchema.index({ title: 1 });
eventSchema.index({ date: 1 });

// Log index creation status
eventSchema.on("index", (err) => {
  if (err) console.error("❌ Event index creation failed:", err);
  else console.log("✅ Event indexes created successfully!");
});

module.exports = mongoose.model("Event", eventSchema);
