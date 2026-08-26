import type { Metadata } from "next";
import React from "react";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { AiChatDrawer } from "@/components/dashboard/AiChatDrawer";

export const metadata: Metadata = {
  title: "Cyber Risk & Capital Allocation Platform",
  description: "Open FAIR Quantitative Risk Modeling & MILP Investment Optimizer",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 max-w-7xl w-full mx-auto">
          {children}
        </main>
        <AiChatDrawer />
      </body>
    </html>
  );
}