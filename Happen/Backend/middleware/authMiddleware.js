// JWT authentication & role-based access control
const jwt = require("jsonwebtoken");

// ✅ Authentication Middleware (JWT Verification)
const authenticateUser = (req, res, next) => {
  try {
    // Extract token from Authorization header
    const authHeader = req.header("Authorization");
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({ message: "Access Denied: No token provided or invalid format" });
    }

    const token = authHeader.split(" ")[1];
    const verified = jwt.verify(token, process.env.JWT_SECRET);

    req.user = verified; // Attach decoded user to request
    next();
  } catch (error) {
    if (error.name === "TokenExpiredError") {
      return res.status(401).json({ message: "Session expired, please log in again" });
    }
    return res.status(403).json({ message: "Invalid Token" });
  }
};

// ✅ Role-Based Access Middleware
const authorizeRoles = (...roles) => {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ message: "Access Denied: Unauthorized role" });
    }
    next();
  };
};

module.exports = { authenticateUser, authorizeRoles };


