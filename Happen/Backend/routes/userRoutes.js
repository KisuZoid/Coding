const express = require("express");
const { getUserProfile, updateUserRole } = require("../controllers/userController");
const { authenticateUser }= require("../middleware/authMiddleware");
const { roleCheck } = require("../middleware/roleMiddleware");
const { param } = require("express-validator");

const router = express.Router();

// ✅ Validation Rule
const validateUserId = [
  param("userId").isMongoId().withMessage("Invalid user ID format")
];

// ✅ Routes
router.get("/profile", authenticateUser, getUserProfile);
router.put("/update-role/:userId", authenticateUser, roleCheck(["admin"]), validateUserId, updateUserRole);

module.exports = router;
