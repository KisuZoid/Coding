const mongoose = require("mongoose");

const qrSchema = new mongoose.Schema(
  {
    userId: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: "User", 
      required: true 
    },
    eventId: { 
      type: mongoose.Schema.Types.ObjectId, 
      ref: "Event", 
      required: true 
    },
    qrCode: { 
      type: String, 
      required: true, 
      unique: true, 
      validate: {
        validator: function (value) {
          return value.length <= 500; // Prevent extremely large QR codes
        },
        message: "QR Code is too large.",
      }
    }
  },
  { timestamps: true }
);

// Unique index to prevent multiple QR codes for the same user-event
qrSchema.index({ userId: 1, eventId: 1 }, { unique: true });
qrSchema.index({ qrCode: 1 }); // Index qrCode for faster search

// Prevent duplicate QR code creation before saving
qrSchema.pre("save", async function (next) {
  const existingQR = await mongoose.models.QR.findOne({ userId: this.userId, eventId: this.eventId });
  if (existingQR) {
    const err = new Error("QR Code already exists for this user and event.");
    return next(err);
  }
  next();
});

// Log index creation
qrSchema.on("index", (err) => {
  if (err) console.error("❌ QR index creation failed:", err);
  else console.log("✅ QR indexes created successfully!");
});

module.exports = mongoose.model("QR", qrSchema);
