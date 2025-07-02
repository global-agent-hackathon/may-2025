"use client";

import Image from "next/image";
import { cn } from "@/lib/utils";

interface FluxLogoProps {
  size?: number;
  className?: string;
  variant?: "default" | "dashboard";
}

export function FluxLogo({ size, className, variant = "default" }: FluxLogoProps) {
  // Use larger size for dashboard variant to match text size
  const logoSize = size || (variant === "dashboard" ? 30 : 32);
  
  return (
    <Image 
      src="/logo.png" 
      alt="FLUX Logo" 
      width={logoSize} 
      height={logoSize} 
      className={cn("rounded", className)} 
      priority
    />
  );
} 