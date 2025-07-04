"use client";

import Link from "next/link";
import Image from "next/image";
import { PenLine, Inbox, Star, Send, Archive, Settings, Command, LayoutDashboard } from "lucide-react";
import { useEffect, useState } from "react";


const appName = "Email Agent";

const mainNavItems = [
    { name: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
    { name: 'Agent', icon: Command, href: '/dashboard/query-agent' },
    { name: 'Mails', icon: Inbox, href: '/dashboard/mails' },
];

const secondaryNavItems = [
    { name: 'Settings', icon: Settings, href: '/dashboard/settings' },
];

interface UserData {
    email: string;
    name: string;
    picture?: string;
}

export default function AppSidebar() {
    const [userData, setUserData] = useState<UserData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchUserData = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "";
                if (!apiBaseUrl) {
                    console.error("NEXT_PUBLIC_API_BASE_URL is not set.");
                    setError("API URL not configured.");
                    setIsLoading(false);
                    return;
                }

                const response = await fetch(`${apiBaseUrl}/get-user-data`, {
                    credentials: 'include', // Important to send session cookies
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        // User is not authenticated
                        setError("Not authenticated. Please log in.");
                        // Example: router.push('/login'); // if using next/navigation
                    } else {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || `Failed to fetch user data: ${response.statusText}`);
                    }
                } else {
                    const data: UserData = await response.json();
                    setUserData(data);
                }
            } catch (err: any) {
                setError(err.message || "An unexpected error occurred.");
                console.error("Error fetching user data:", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserData();
    }, []);

    return (
        <div className="flex h-screen w-64 flex-col bg-zinc-950 text-white">
            {/* Header */}
            <div className="flex items-center gap-2 p-4">
                <h1 className="text-xl font-bold">{appName}</h1>
            </div>
            {/* Write email button */}
            <div className="px-4 py-2 mt-4">
                <Link
                    href="/dashboard/compose"
                    className="flex w-full items-center gap-2 rounded-md bg-white px-3 py-2 text-sm font-medium hover:bg-gray-200 cursor-pointer"
                >
                    <PenLine className="h-5 w-5 text-black" />
                    <span className="text-black">Write Email</span>
                </Link>
            </div>
            {/* Main Navigation */}
            <nav className="flex-1 px-4 py-2 mt-4 overflow-y-auto">
                <div className="space-y-1">
                    {mainNavItems.map((item) => (
                        <Link href={item.href} key={item.name} className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-zinc-800">
                            <item.icon className="h-5 w-5" />
                            {item.name}
                        </Link>
                    ))}
                </div>
                {/* Secondary Navigation */}
                <div className="mt-10 space-y-1">
                    <h3 className="px-3 text-xs font-semibold uppercase text-gray-300">Others</h3>
                    {secondaryNavItems.map((item) => (
                        <Link href={item.href} key={item.name} className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-zinc-800">
                            <item.icon className="h-5 w-5" />
                            {item.name}
                        </Link>
                    ))}
                </div>
            </nav>

            {/* User Profile */}
            <div className="p-4 border-t border-zinc-800">
                {isLoading ? (
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-zinc-700 rounded-full animate-pulse"></div>
                        <div className="flex flex-col gap-1">
                            <div className="w-24 h-4 bg-zinc-700 rounded animate-pulse"></div>
                            <div className="w-32 h-3 bg-zinc-700 rounded animate-pulse"></div>
                        </div>
                    </div>
                ) : error ? (
                    <div className="text-red-400 text-sm">{error}</div>
                ) : userData ? (
                    <div className="flex items-center gap-3">
                        <Image
                            src={userData.picture || "/next.svg"}
                            alt={userData.name || "User Profile"}
                            width={40}
                            height={40}
                            className="rounded-full bg-zinc-700"
                            onError={(e) => {
                                (e.target as HTMLImageElement).src = "/next.svg";
                                (e.target as HTMLImageElement).alt = "Default Profile Picture";
                            }}
                        />
                        <div className="flex flex-col">
                            <span className="text-sm font-medium truncate max-w-[150px]" title={userData.name}>
                                {userData.name || "User Name"}
                            </span>
                            <span className="text-xs text-gray-400 truncate max-w-[150px]" title={userData.email}>
                                {userData.email || "user@example.com"}
                            </span>
                        </div>
                    </div>
                ) : (
                    <div className="text-sm text-gray-400">User not logged in.</div>
                )}
            </div>
        </div>
    );
}