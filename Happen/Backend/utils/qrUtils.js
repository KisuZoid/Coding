const QRCode = require("qrcode");

const generateQRCode = async (data, options = {}) => {
  try {
    return await QRCode.toDataURL(data, {
      errorCorrectionLevel: options.errorCorrection || "M",
      width: options.size || 300,
      color: {
        dark: options.darkColor || "#000000",
        light: options.lightColor || "#ffffff"
      }
    });
  } catch (error) {
    console.error("QR Code Generation Failed:", error);
    return null; // ✅ Prevents app crashes
  }
};

module.exports = { generateQRCode };
