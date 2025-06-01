"use client";

import { cn } from "@/lib/utils";
import React, { useEffect, useRef, useState } from "react";

interface AnimatedShinyTextProps {
  className?: string;
  children: React.ReactNode;
  animationDuration?: number; // Added control for animation speed
  animationDelay?: number; // Added to stagger animations
  disableAnimation?: boolean; // Option to disable animation completely
}

export function AnimatedShinyText({
  className,
  children,
  animationDuration = 5, // Default animation duration in seconds
  animationDelay = 0, // Default delay before animation starts
  disableAnimation = false, // Default to enabling animation
}: AnimatedShinyTextProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [showAnimation, setShowAnimation] = useState(false);

  // Use IntersectionObserver to only animate when element is visible
  useEffect(() => {
    if (disableAnimation) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setShowAnimation(true);
            observer.disconnect(); // Only trigger animation once
          }
        });
      },
      { threshold: 0.1 } // Start animation when 10% of element is visible
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, [disableAnimation]);

  return (
    <div
      ref={containerRef}
      className={cn("relative inline-block", className)}
    >
      {children}
      {!disableAnimation && showAnimation && (
        <div
          className="absolute inset-0 h-full w-full rounded"
          style={{
            background: "linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)",
            backgroundSize: "200% 100%",
            animation: `shiny-text ${animationDuration}s linear infinite`,
            animationDelay: `${animationDelay}s`,
          }}
        />
      )}
      <style jsx>{`
        @keyframes shiny-text {
          0% {
            background-position: 100% 50%;
          }
          100% {
            background-position: -100% 50%;
          }
        }
      `}</style>
    </div>
  );
} 