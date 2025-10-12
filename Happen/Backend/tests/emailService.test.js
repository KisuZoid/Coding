//just for jest jest case
const { sendEmail } = require("../utils/emailService");

jest.mock("nodemailer"); // Mock nodemailer

describe("Email Service", () => {
  it("should send an email successfully", async () => {
    await expect(sendEmail("test@example.com", "Test Subject", "<p>Hello</p>")).resolves.not.toThrow();
  });
});
