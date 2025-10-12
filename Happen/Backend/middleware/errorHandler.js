const errorHandler = (err, req, res, next) => {
    const statusCode = err.statusCode || 500;
    const environment = process.env.NODE_ENV || "development";

    // Log error in development mode
    if (environment === "development") {
        console.error(`❌ Error: ${err.message}`);
        console.error(err.stack);
    }

    res.status(statusCode).json({
        success: false,
        message: err.message || "Internal Server Error",
        ...(environment === "development" && { stack: err.stack }), // Show stack trace only in dev mode
    });
};

module.exports = errorHandler; // ✅ Properly export the function
