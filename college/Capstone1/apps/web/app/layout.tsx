import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AutoInspect-X",
  description:
    "AI-assisted vehicle damage inspection — chat, photo upload, honest machine reading of damage, and a clearly labelled result.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}