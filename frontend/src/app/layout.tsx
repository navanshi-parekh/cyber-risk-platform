import type { Metadata } from "next";
import { Fira_Sans, JetBrains_Mono } from "next/font/google";
import React from "react";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { AiChatDrawer } from "@/components/dashboard/AiChatDrawer";
import { ThemeProvider } from "@/lib/theme-context";

const firaSans = Fira_Sans({ subsets: ["latin"], variable: "--font-sans", weight: ["400", "500", "600", "700"], display: "swap" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

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
    <html lang="en" className={`${firaSans.variable} ${jetbrainsMono.variable}`}>
      <body className="relative bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased min-h-screen flex flex-col font-sans transition-colors">
        <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-40 left-1/4 w-[560px] h-[560px] rounded-full bg-cyan-500/10 dark:bg-cyan-500/10 blur-[140px]" />
          <div className="absolute top-1/3 -right-40 w-[480px] h-[480px] rounded-full bg-blue-600/10 dark:bg-blue-600/10 blur-[140px]" />
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#00000005_1px,transparent_1px),linear-gradient(to_bottom,#00000005_1px,transparent_1px)] dark:bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:56px_56px]" />
        </div>
        <ThemeProvider>
          <Header />
          <main className="flex-1 max-w-7xl w-full mx-auto">
            {children}
          </main>
          <AiChatDrawer />
        </ThemeProvider>
      </body>
    </html>
  );
}