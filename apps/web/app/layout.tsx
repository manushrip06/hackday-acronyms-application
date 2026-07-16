import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/Nav";
import { RoleProvider } from "@/lib/role";

export const metadata: Metadata = {
  title: "Acronym Atlas",
  description: "Team jargon dictionary from documentation — hackday MVP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@600;700;800&family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <RoleProvider>
          <Nav />
          <main>{children}</main>
        </RoleProvider>
      </body>
    </html>
  );
}
