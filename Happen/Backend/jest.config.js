module.exports = {
    testEnvironment: "node",
    setupFiles: ["dotenv/config"],
    moduleNameMapper: {
      "^nodemailer$": "<rootDir>/__mocks__/nodemailer.js"
    }
  };
  