import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "microDify",
  description: "A lightweight AI Agent platform for internal teams.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
