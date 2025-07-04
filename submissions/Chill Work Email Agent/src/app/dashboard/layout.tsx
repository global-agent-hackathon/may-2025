'use client';

import AppSidebar from "@/components/sections/AppSidebar";
import React, { useState } from "react";
import { Menu } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <div className="flex min-h-screen bg-zinc-900">
            {/* Sidebar for larger screens and toggleable for mobile */}
            <div
                className={`fixed top-0 left-0 w-64 h-screen bg-zinc-950 transition-transform duration-300 ease-in-out z-50 ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"
                    } md:translate-x-0 md:w-64`}
            >
                <AppSidebar />
            </div>

            {/* Mobile menu toggle button */}
            <button
                className="md:hidden fixed top-4 right-4 z-50 text-white p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                aria-label="Toggle sidebar"
            >
                <Menu size={24} />
            </button>

            {/* Main content */}
            <main className="flex-1 p-6 max-w-7xl mx-auto w-full md:ml-64">
                <div className="min-h-[calc(100vh-3rem)] flex flex-col">{children}</div>
            </main>

            {/* Overlay for mobile sidebar */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={() => setIsSidebarOpen(false)}
                ></div>
            )}
        </div>
    );
}