const nodemailer = require("nodemailer");

const transporter = nodemailer.createTransport({
  host: "sandbox.smtp.mailtrap.io",
  port: 2525,
  auth: {
    user: "cb4ee56459aaf9",
    pass: "2786f6369c0cdc"
  }
});

transporter.verify((error, success) => {
  if (error) {
    console.error("Email Service Error:", error);
  } else {
    console.log("✅ Email Service Ready");
  }
});

// ✅ Generic Email Sending Function
const sendEmail = async (to, subject, html) => {
  try {
    const mailOptions = {
      from: `"Event Manager" <${process.env.EMAIL_USER}>`,
      to,
      subject,
      html,
    };

    const info = await transporter.sendMail(mailOptions);
    console.log(`📩 Email sent to ${to}: ${info.messageId}`);
  } catch (error) {
    console.error(`❌ Email Sending Failed: ${error.message}`);
    throw new Error("Email sending failed, please try again later.");
  }
};

// ✅ Verification Email Function
const sendVerificationEmail = async (email, verificationToken) => {
  const verificationLink = `${process.env.BASE_URL}/api/auth/verify/${verificationToken}`;
  
  const emailHtml = `
    <p>Click the link below to verify your email:</p>
    <a href="${verificationLink}">${verificationLink}</a>
    <p>If the above link doesn't work, copy and paste it into your browser.</p>
    <p>Verification Token: <strong>${verificationToken}</strong></p>
  `;

  await sendEmail(email, "Verify Your Email", emailHtml);
};


// ✅ Password Reset Email Function
const sendPasswordResetEmail = async (email, resetToken) => {
  const resetLink = `${process.env.BASE_URL}/api/auth/reset-password/${resetToken}`;
  
  const emailHtml = `
    <p>Click the link below to reset your password:</p>
    <a href="${resetLink}">${resetLink}</a>
    <p>If the above link doesn't work, copy and paste it into your browser.</p>
    <p>Reset Token: <strong>${resetToken}</strong></p>
  `;

  await sendEmail(email, "Reset Your Password", emailHtml);
};


// ✅ Export All Functions
module.exports = { sendEmail, sendVerificationEmail, sendPasswordResetEmail };
