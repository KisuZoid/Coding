const User = require("../models/userModel");

exports.getUserProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select("-password"); // Exclude password
    if (!user) {
      return res.status(404).json({ message: "⚠️ User not found" });
    }
    res.json(user);
  } catch (error) {
    res.status(500).json({ message: "❌ Error fetching profile", error: error.message });
  }
};

// ✅ Securely Get All Users
exports.getAllUsers = async (req, res) => {
  try {
    const users = await User.find({}, "name email role isVerified");
    res.json(users);
  } catch (error) {
    res.status(500).json({ message: "❌ Error fetching users", error: error.message });
  }
};

// ✅ Securely Update User Role
exports.updateUserRole = async (req, res) => {
  try {
    const { userId, role } = req.body;

    // Check if valid role
    const validRoles = ["admin", "user", "organizer"];
    if (!validRoles.includes(role)) {
      return res.status(400).json({ message: "❌ Invalid role specified" });
    }

    // Find user
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: "⚠️ User not found" });
    }

    // Prevent redundant updates
    if (user.role === role) {
      return res.status(400).json({ message: "⚠️ User already has this role" });
    }

    user.role = role;
    await user.save();

    res.json({ message: "✅ User role updated successfully" });
  } catch (error) {
    res.status(500).json({ message: "❌ Error updating role", error: error.message });
  }
};
