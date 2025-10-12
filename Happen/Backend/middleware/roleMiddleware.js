// Middleware for role-based permissions
exports.roleCheck = (roles) => {
    return (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ message: "Unauthorized: User not authenticated" });
        }

        if (!roles.includes(req.user.role)) {
            if (process.env.NODE_ENV === "development") {
                console.warn(`🚨 Access Denied: User ${req.user.id} with role '${req.user.role}' attempted unauthorized access`);
            }
            return res.status(403).json({ success: false, message: "Forbidden: Insufficient permissions" });
        }

        next();
    };
};
