const express = require("express");
const cors = require("cors");
const authRoutes = require("./routes/authRoutes");
const userRoutes = require("./routes/userRoutes");
const eventRoutes = require("./routes/eventRoutes");
const qrRoutes = require("./routes/qrRoutes");
const ticketRoutes = require("./routes/ticketRoutes");
const attendanceRoutes = require("./routes/attendanceRoutes");
const errorHandler = require("./middleware/errorHandler");

const app = express();
const compression = require("compression");
app.use(compression());


// Middleware
app.use(cors());
app.use(express.json()); // ✅ No need for body-parser

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/users", userRoutes);
app.use("/api/events", eventRoutes);
app.use("/api/qr", qrRoutes);
app.use("/api/tickets", ticketRoutes);
app.use("/api/attendance", attendanceRoutes);

// Error Handling Middleware
app.use(errorHandler);

module.exports = app;
