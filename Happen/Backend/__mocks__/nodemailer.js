//just for jest test case
module.exports = {
    createTransport: jest.fn().mockReturnValue({
      sendMail: jest.fn().mockResolvedValue({ messageId: "12345" }),
      verify: jest.fn().mockResolvedValue(true),
    }),
  };
  