"use client";

import React from "react";
import { ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface SignupButtonProps {
  href: string;
  className?: string;
  children: React.ReactNode;
}

export function SignupButton({ href, className, children }: SignupButtonProps) {
  return (
    <Link href={href} className="block">
      <button
        className={cn(
          "group relative flex items-center justify-center gap-2.5 overflow-hidden rounded-md bg-purple-600 px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 shadow-sm hover:bg-purple-700 hover:shadow-md",
          className
        )}
      >
        <span className="relative z-10">{children}</span>
        <span className="relative z-10 flex h-6 w-6 items-center justify-center rounded-full bg-white/10 transition-all duration-200 group-hover:bg-white/20">
          <ArrowUpRight className="h-4 w-4 text-white transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
        </span>
      </button>
    </Link>
  );
} 