const express = require("express");
const { generateTicket, validateTicket } = require("../controllers/ticketController");
const {authenticateUser} = require("../middleware/authMiddleware");
const { roleCheck } = require("../middleware/roleMiddleware");
const { param, body } = require("express-validator");

const router = express.Router();

// ✅ Validation Rules
const validateEventId = [
  param("eventId").isMongoId().withMessage("Invalid event ID format")
];

const validateTicketCode = [
  body("qrCode").notEmpty().withMessage("QR Code is required")
];

// ✅ Routes
router.post("/generate/:eventId", authenticateUser, roleCheck(["organizer", "admin"]), validateEventId, generateTicket);
router.post("/validate", authenticateUser, roleCheck(["organizer", "admin"]), validateTicketCode, validateTicket);

module.exports = router;
