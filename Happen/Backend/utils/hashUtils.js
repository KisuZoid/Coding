const bcrypt = require("bcryptjs");

// ✅ Use configurable salt rounds
const SALT_ROUNDS = parseInt(process.env.SALT_ROUNDS) || 10;

// ✅ Hash password with dynamic salt rounds
const hashPassword = async (password) => {
  const salt = await bcrypt.genSalt(SALT_ROUNDS);
  return bcrypt.hash(password, salt);
};

// ✅ Directly return the result of password comparison
const comparePassword = (password, hashedPassword) => {
  return bcrypt.compare(password, hashedPassword);
};

module.exports = { hashPassword, comparePassword };
