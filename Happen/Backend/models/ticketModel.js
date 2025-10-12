const mongoose = require("mongoose");

const ticketSchema = new mongoose.Schema(
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
    },
    scanned: { 
      type: Boolean, 
      default: false 
    }
  },
  { timestamps: true } // Enable createdAt and updatedAt timestamps
);

// Unique index to prevent multiple tickets for the same user-event
ticketSchema.index({ userId: 1, eventId: 1 }, { unique: true });
ticketSchema.index({ qrCode: 1 }); // Index qrCode for faster lookup

// Prevent duplicate ticket creation
ticketSchema.pre("save", async function (next) {
  const existingTicket = await mongoose.models.Ticket.findOne({ userId: this.userId, eventId: this.eventId });
  if (existingTicket) {
    const err = new Error("Ticket already exists for this user and event.");
    return next(err);
  }
  next();
});

// Log index creation
ticketSchema.on("index", (err) => {
  if (err) console.error("❌ Ticket index creation failed:", err);
  else console.log("✅ Ticket indexes created successfully!");
});

module.exports = mongoose.model("Ticket", ticketSchema);
