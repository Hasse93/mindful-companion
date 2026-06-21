import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import NavBar from "@/components/NavBar";
import AuthGate from "@/components/AuthGate";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Mindful Companion",
  description:
    "A supportive mental-wellness companion. Not a medical device or a substitute for professional care.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${jakarta.variable} h-full antialiased`}>
      <body className="min-h-full font-sans text-ink">
        <AuthGate>
          <NavBar />
          <main className="mx-auto w-full max-w-3xl flex-1 px-4 pb-16 pt-6">
            {children}
          </main>
          <footer className="px-4 pb-8 text-center text-xs text-faint">
            Mindful Companion is a supportive tool, not therapy, diagnosis, or a
            crisis service. In an emergency, contact local emergency services.
          </footer>
        </AuthGate>
      </body>
    </html>
  );
}
