const express = require("express");
const { createEvent, getEvents, getEventById, deleteEvent } = require("../controllers/eventController");
const {authenticateUser} = require("../middleware/authMiddleware");
const { roleCheck } = require("../middleware/roleMiddleware");
const { body, param } = require("express-validator");

const router = express.Router();

// ✅ Validation Rules
const validateEventCreation = [
  body("title").notEmpty().withMessage("Event title is required"),
  body("date").isISO8601().withMessage("Invalid date format (YYYY-MM-DD)"),
  body("location").notEmpty().withMessage("Event location is required")
];

const validateEventId = [
  param("id").isMongoId().withMessage("Invalid event ID format")
];

// ✅ Routes
router.post("/", authenticateUser, roleCheck(["organizer", "admin"]), validateEventCreation, createEvent);
router.get("/", authenticateUser, getEvents);
router.get("/:id", authenticateUser, validateEventId, getEventById);
router.delete("/:id", authenticateUser, validateEventId, roleCheck(["admin"]), deleteEvent);

module.exports = router;
