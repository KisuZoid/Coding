const express = require("express");
const { register, login, verifyEmail, resetPassword, requestPasswordReset } = require("../controllers/authController");
const { body } = require("express-validator");
const rateLimit = require("express-rate-limit");

const router = express.Router();

// ✅ Rate Limiting (Prevent Brute Force)
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  message: "Too many login attempts. Please try again later."
});

// ✅ Input Validation
const validateRegister = [
  body("name").notEmpty().withMessage("Name is required"),
  body("email").isEmail().withMessage("Invalid email"),
  body("password").isLength({ min: 6 }).withMessage("Password must be at least 6 characters long")
];

const validateLogin = [
  body("email").isEmail().withMessage("Invalid email"),
  body("password").notEmpty().withMessage("Password is required")
];

const validateEmail = [body("email").isEmail().withMessage("Invalid email")];

const validatePasswordReset = [
  body("token").notEmpty().withMessage("Token is required"),
  body("newPassword").isLength({ min: 6 }).withMessage("Password must be at least 6 characters long")
];

// ✅ Routes
router.post("/register", validateRegister, register);
router.post("/login", loginLimiter, validateLogin, login);
router.post("/verify-email", validateEmail, verifyEmail); // 🔄 Changed to POST for security
router.post("/request-password-reset", validateEmail, requestPasswordReset);
router.post("/reset-password", validatePasswordReset, resetPassword); // 🔄 Changed to POST with token in body

module.exports = router;
