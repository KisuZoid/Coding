const express = require("express");
const { generateQR, validateQR } = require("../controllers/qrController");
const {authenticateUser} = require("../middleware/authMiddleware");
const { roleCheck } = require("../middleware/roleMiddleware");
const { param, body } = require("express-validator");

const router = express.Router();

// ✅ Validation Rules
const validateEventId = [
  param("eventId").isMongoId().withMessage("Invalid event ID format")
];

const validateQRCode = [
  body("qrCode").notEmpty().withMessage("QR Code is required")
];

// ✅ Routes
router.post("/generate/:eventId", authenticateUser, roleCheck(["organizer", "admin"]), validateEventId, generateQR);
router.post("/validate", authenticateUser, roleCheck(["organizer", "admin"]), validateQRCode, validateQR);

module.exports = router;
