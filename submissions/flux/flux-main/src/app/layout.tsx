import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { ThemeProvider } from '@/components/ui/theme-provider'
import { DataProvider } from '@/contexts/DataContext';
import QueryProvider from "@/components/providers/query-provider";

// Configure Inter font
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  weight: ['400', '500', '600', '700'],
  variable: '--font-inter',
})

// Use CSS variables to define Georgia font
const customFonts = `
:root {
  --font-georgia: Georgia, serif;
}
`;

export const metadata: Metadata = {
  title: "Flux",
  description: "Simple forms and surveys for everyone",
  icons: {
    icon: [
      {
        url: "/favicon.svg",
        type: "image/svg+xml",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className={`${inter.variable} font-sans`}>
        <head>
          <style dangerouslySetInnerHTML={{ __html: customFonts }} />
        </head>
        <body className="min-h-screen antialiased">
          <ThemeProvider
            attribute="class"
            defaultTheme="light"
            enableSystem
            disableTransitionOnChange
          >
            <QueryProvider>
              <DataProvider>
                {children}
              </DataProvider>
            </QueryProvider>
            <Toaster />
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
