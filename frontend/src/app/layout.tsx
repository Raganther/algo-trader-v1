import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Strategy Lab",
  description: "Algo trading strategy reference dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-[#0a0a0a] text-white min-h-screen antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
