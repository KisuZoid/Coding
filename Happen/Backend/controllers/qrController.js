const QRCode = require("qrcode");
const Ticket = require("../models/ticketModel");
const mongoose = require("mongoose");
const crypto = require("crypto");

exports.generateQR = async (req, res) => {
  try {
    const { userId, eventId } = req.body;

    // Validate Object IDs
    if (!mongoose.isValidObjectId(userId) || !mongoose.isValidObjectId(eventId)) {
      return res.status(400).json({ message: "❌ Invalid userId or eventId format" });
    }

    // Check if QR already exists
    const existingTicket = await Ticket.findOne({ userId, eventId });
    if (existingTicket) return res.status(400).json({ message: "⚠️ QR already generated for this user-event" });

    // Generate secure QR data
    const qrData = crypto.createHash("sha256").update(`${userId}-${eventId}`).digest("hex");
    const qrCode = await QRCode.toDataURL(qrData);

    // Save QR Code
    const newTicket = new Ticket({ userId, eventId, qrCode, scanned: false });
    await newTicket.save();

    res.json({ message: "✅ QR Code generated successfully!", qrCode });
  } catch (error) {
    res.status(500).json({ message: "❌ Error generating QR Code", error: error.message });
  }
};

//scanQR
exports.validateQR = async (req, res) => {
  try {
    const { qrCode } = req.body;
    if (!qrCode) return res.status(400).json({ message: "❌ QR Code is required" });

    const ticket = await Ticket.findOne({ qrCode });

    if (!ticket) return res.status(404).json({ message: "⚠️ Invalid QR Code" });

    if (ticket.scanned) return res.status(400).json({ message: "⚠️ QR Code already scanned" });

    ticket.scanned = true;
    await ticket.save();

    res.json({ message: "✅ QR Code scanned successfully!" });
  } catch (error) {
    res.status(500).json({ message: "❌ Error scanning QR Code", error: error.message });
  }
};
