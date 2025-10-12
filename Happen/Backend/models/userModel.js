const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");

const userSchema = new mongoose.Schema(
  {
    name: { 
      type: String, 
      required: true, 
      trim: true 
    },
    email: { 
      type: String, 
      required: true, 
      unique: true, 
      lowercase: true, 
      trim: true 
    },
    password: { 
      type: String, 
      required: true, 
      minlength: 8 
    },
    role: { 
      type: String, 
      enum: ["admin", "organizer", "attendee"], 
      default: "attendee",
      lowercase: true
    },
    isVerified: { 
      type: Boolean, 
      default: false 
    }
  },
  { timestamps: true } // Auto add createdAt & updatedAt
);

// Ensure email is indexed properly
userSchema.index({ email: 1 }, { unique: true });

// Hash password before saving
userSchema.pre("save", async function (next) {
  if (!this.isModified("password")) return next();
  this.password = await bcrypt.hash(this.password, 10);
  next();
});

// Secure password comparison method
userSchema.methods.comparePassword = async function (enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

// Sanitize output to remove password field
userSchema.methods.toJSON = function () {
  const obj = this.toObject();
  delete obj.password;
  return obj;
};

// Log index creation
userSchema.on("index", (err) => {
  if (err) console.error("❌ User index creation failed:", err);
  else console.log("✅ User indexes created successfully!");
});

module.exports = mongoose.model("User", userSchema);
