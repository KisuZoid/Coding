const Ticket = require("../models/ticketModel");
const QRCode = require("qrcode");

exports.validateTicket = async (req, res) => {
  try {
    const { qrCode } = req.body;

    // Check if QR code is provided
    if (!qrCode) {
      return res.status(400).json({ message: "❌ QR Code is required" });
    }

    // Find the ticket
    const ticket = await Ticket.findOne({ qrCode });
    
    if (!ticket) {
      return res.status(404).json({ message: "⚠️ Invalid Ticket - No matching record found" });
    }

    // Check if already scanned
    if (ticket.scanned) {
      return res.status(400).json({ message: "⚠️ Ticket already used" });
    }

    res.json({ message: "✅ Ticket is valid", ticket });
  } catch (error) {
    res.status(500).json({ message: "❌ Ticket validation failed", error: error.message });
  }
};

exports.generateTicket = async (req, res) => {
  try {
    const { eventId, userId } = req.body;

    // Validate input
    if (!eventId || !userId) {
      return res.status(400).json({ message: "❌ eventId and userId are required" });
    }

    // Generate unique QR data (you can customize this)
    const qrData = `${eventId}-${userId}-${Date.now()}`;
    
    // Generate QR Code
    const qrCodeUrl = await QRCode.toDataURL(qrData);

    // Save ticket to database
    const newTicket = new Ticket({
      eventId,
      userId,
      qrCode: qrData, // Save the raw QR data
      qrCodeUrl, // Save the QR code image URL
      scanned: false,
    });

    await newTicket.save();

    res.status(201).json({ message: "✅ Ticket generated successfully", ticket: newTicket });
  } catch (error) {
    res.status(500).json({ message: "❌ Error generating ticket", error: error.message });
  }
};