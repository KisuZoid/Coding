const Event = require("../models/eventModel");

exports.createEvent = async (req, res) => {
  try {
    const { name, date, location } = req.body;

    // Validate input
    if (!name || !date || !location) {
      return res.status(400).json({ message: "All fields (name, date, location) are required" });
    }

    // Ensure valid date format
    if (isNaN(Date.parse(date))) {
      return res.status(400).json({ message: "Invalid date format" });
    }

    const newEvent = new Event({ name, date, location });
    await newEvent.save();

    res.status(201).json({ message: "✅ Event created successfully", event: newEvent });
  } catch (error) {
    res.status(500).json({ message: "❌ Error creating event", error: error.message });
  }
};

exports.getEvents = async (req, res) => {
  try {
    const events = await Event.find();

    if (events.length === 0) {
      return res.status(404).json({ message: "No events found" });
    }

    res.json(events);
  } catch (error) {
    res.status(500).json({ message: "❌ Error fetching events", error: error.message });
  }
};

// ✅ Get a single event by ID
exports.getEventById = async (req, res) => {
  try {
    const { eventId } = req.params;

    // Validate event ID
    if (!eventId.match(/^[0-9a-fA-F]{24}$/)) {
      return res.status(400).json({ message: "Invalid event ID format" });
    }

    const event = await Event.findById(eventId);
    if (!event) {
      return res.status(404).json({ message: "⚠️ Event not found" });
    }

    res.json(event);
  } catch (error) {
    res.status(500).json({ message: "❌ Error fetching event", error: error.message });
  }
};

// ✅ Delete an event by ID
exports.deleteEvent = async (req, res) => {
  try {
    const { eventId } = req.params;

    // Validate event ID
    if (!eventId.match(/^[0-9a-fA-F]{24}$/)) {
      return res.status(400).json({ message: "Invalid event ID format" });
    }

    const deletedEvent = await Event.findByIdAndDelete(eventId);
    if (!deletedEvent) {
      return res.status(404).json({ message: "⚠️ Event not found" });
    }

    res.json({ message: "✅ Event deleted successfully" });
  } catch (error) {
    res.status(500).json({ message: "❌ Error deleting event", error: error.message });
  }
};
