"use client";

import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { useState, useEffect } from "react";
import { useUser, useClerk } from '@clerk/nextjs';
import { FluxLogo } from "@/components/ui/flux-logo";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { LogOut, User, Settings, ChevronDown } from "lucide-react";

export function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();
  
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsOpen(false); // Close mobile menu if open
  };

  const handleSignout = () => {
    signOut();
  };

  // Get user initials for avatar fallback
  const getUserInitials = () => {
    if (!user) return "U";
    return user.firstName && user.lastName
      ? `${user.firstName[0]}${user.lastName[0]}`
      : user.firstName?.[0] || user.emailAddresses[0]?.emailAddress?.[0]?.toUpperCase() || "U";
  };

  return (
    <header className={cn(
      "fixed top-0 left-0 right-0 z-50 border-b border-gray-200 transition-all duration-200",
      scrolled ? "bg-white/90" : "bg-white/30 backdrop-blur-md"
    )}>
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <FluxLogo size={32} />
              <span className="font-semibold text-xl">FLUX</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-2">
            <button 
              onClick={() => scrollToSection('features')} 
              className="relative text-sm text-gray-600 hover:text-gray-900 group px-4 py-2"
            >
              <span className="relative z-10">Features</span>
              <span className="absolute inset-0 w-full h-full bg-blue-50 rounded-md -z-10 scale-0 group-hover:scale-100 transition-transform duration-200 origin-center"></span>
            </button>
            
            <button 
              onClick={() => scrollToSection('pricing')} 
              className="relative text-sm text-gray-600 hover:text-gray-900 group px-4 py-2"
            >
              <span className="relative z-10">Pricing</span>
              <span className="absolute inset-0 w-full h-full bg-blue-50 rounded-md -z-10 scale-0 group-hover:scale-100 transition-transform duration-200 origin-center"></span>
            </button>
            
            <button 
              onClick={() => scrollToSection('faq')} 
              className="relative text-sm text-gray-600 hover:text-gray-900 group px-4 py-2"
            >
              <span className="relative z-10">FAQ</span>
              <span className="absolute inset-0 w-full h-full bg-blue-50 rounded-md -z-10 scale-0 group-hover:scale-100 transition-transform duration-200 origin-center"></span>
            </button>
          </nav>

          {/* Auth Buttons or User Menu */}
          <div className="hidden md:flex items-center space-x-2">
            {isLoaded && user ? (
              <>
                <Link href="/dashboard">
                  <span className="text-sm font-medium text-blue-600 cursor-pointer px-6 py-2 rounded-md bg-blue-50 hover:bg-blue-100 transition-colors">Dashboard</span>
                </Link>
                <DropdownMenu>
                  <DropdownMenuTrigger className="outline-none">
                    <div className="flex items-center space-x-1 cursor-pointer">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={user.imageUrl} alt={user.fullName || "User"} />
                        <AvatarFallback>{getUserInitials()}</AvatarFallback>
                      </Avatar>
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    </div>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <div className="flex items-center justify-start gap-2 p-2">
                      <div className="flex flex-col space-y-1 leading-none">
                        {user.fullName && <p className="font-medium">{user.fullName}</p>}
                        {user.emailAddresses.length > 0 && (
                          <p className="w-[200px] truncate text-sm text-gray-500">
                            {user.emailAddresses[0].emailAddress}
                          </p>
                        )}
                      </div>
                    </div>
                    <DropdownMenuSeparator />
                    <DropdownMenuGroup>
                      <DropdownMenuItem asChild>
                        <Link href="/dashboard" className="cursor-pointer">
                          <User className="mr-2 h-4 w-4" />
                          <span>Dashboard</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href="/dashboard/settings" className="cursor-pointer">
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Settings</span>
                        </Link>
                      </DropdownMenuItem>
                    </DropdownMenuGroup>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      onClick={handleSignout}
                      className="cursor-pointer text-red-600 focus:text-red-600">
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Log out</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            ) : (
              <>
                <Link href="/auth/sign-in">
                  <span className="text-sm font-medium text-gray-800 cursor-pointer px-6 py-2 rounded-md hover:bg-blue-50 hover:text-blue-600 transition-colors">Log in</span>
                </Link>
                <Link href="/auth/sign-up">
                  <div className="bg-blue-50 text-blue-600 text-sm font-medium py-2 px-6 rounded-md transition-colors border-white hover:border hover:border-blue-100">
                    Start free
                  </div>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            <svg
              className="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        <div
          className={cn(
            "md:hidden",
            isOpen ? "block" : "hidden"
          )}
        >
          <div className="px-2 pt-2 pb-3 space-y-1">
            <button
              onClick={() => scrollToSection('features')}
              className="block w-full text-left px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-blue-50 rounded-md transition-all duration-200"
            >
              Features
            </button>
            <button
              onClick={() => scrollToSection('pricing')}
              className="block w-full text-left px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-blue-50 rounded-md transition-all duration-200"
            >
              Pricing
            </button>
            <button
              onClick={() => scrollToSection('faq')}
              className="block w-full text-left px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-blue-50 rounded-md transition-all duration-200"
            >
              FAQ
            </button>
            <div className="mt-4 space-y-4">
              {isLoaded && user ? (
                <>
                  <Link href="/dashboard" className="block">
                    <span className="block text-center text-sm font-medium text-blue-600 px-6 py-2 rounded-md bg-blue-50 hover:bg-blue-100 transition-colors">Dashboard</span>
                  </Link>
                  <div className="flex items-center justify-between px-3">
                    <div className="flex items-center space-x-3">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={user.imageUrl} alt={user.fullName || "User"} />
                        <AvatarFallback>{getUserInitials()}</AvatarFallback>
                      </Avatar>
                      <div className="flex flex-col">
                        {user.fullName && <p className="font-medium text-sm">{user.fullName}</p>}
                        {user.emailAddresses.length > 0 && (
                          <p className="w-[150px] truncate text-xs text-gray-500">
                            {user.emailAddresses[0].emailAddress}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  <button 
                    onClick={handleSignout}
                    className="block w-full text-center text-sm font-medium text-red-600 px-6 py-2 rounded-md hover:bg-red-50 transition-colors"
                  >
                    Log out
                  </button>
                </>
              ) : (
                <>
                  <Link href="/auth/sign-in" className="block">
                    <span className="block text-center text-sm font-medium text-gray-800 px-6 py-2 rounded-md hover:bg-blue-50 hover:text-blue-600 transition-colors">Log in</span>
                  </Link>
                  <Link href="/auth/sign-up" className="block">
                    <div className="block text-center bg-blue-50 hover:bg-blue-100 text-blue-600 text-sm font-medium py-2 px-6 rounded-md transition-colors border border-blue-100">
                      Start free
                    </div>
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
} 