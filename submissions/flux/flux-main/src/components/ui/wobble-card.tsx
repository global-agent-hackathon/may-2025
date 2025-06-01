"use client";
import React, { useState } from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import { ArrowUpRight } from "lucide-react";

export const WobbleCard = ({
  children,
  containerClassName,
  className,
  onClick,
}: {
  children: React.ReactNode;
  containerClassName?: string;
  className?: string;
  onClick?: () => void;
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseMove = (event: React.MouseEvent<HTMLElement>) => {
    const { clientX, clientY } = event;
    const rect = event.currentTarget.getBoundingClientRect();
    const x = (clientX - (rect.left + rect.width / 2)) / 20;
    const y = (clientY - (rect.top + rect.height / 2)) / 20;
    setMousePosition({ x, y });
  };
  return (
    <motion.section
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => {
        setIsHovering(false);
        setMousePosition({ x: 0, y: 0 });
      }}
      style={{
        transform: isHovering
          ? `translate3d(${mousePosition.x}px, ${mousePosition.y}px, 0) scale3d(1, 1, 1)`
          : "translate3d(0px, 0px, 0) scale3d(1, 1, 1)",
        transition: isHovering ? "transform 0.08s cubic-bezier(0.4,0,0.2,1)" : "transform 0.18s cubic-bezier(0.4,0,0.2,1)",
        willChange: "transform",
      }}
      className={cn(
        "mx-auto w-full bg-indigo-800 relative rounded-2xl overflow-hidden",
        containerClassName
      )}
    >
      <div
        className="relative h-full min-h-[220px] sm:min-h-[280px] md:min-h-[320px] [background-image:radial-gradient(88%_100%_at_top,rgba(255,255,255,0.5),rgba(255,255,255,0))] sm:mx-0 sm:rounded-2xl overflow-hidden flex items-center justify-center"
        style={{
          boxShadow:
            "0 10px 32px rgba(34, 42, 53, 0.12), 0 1px 1px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(34, 42, 53, 0.05), 0 4px 6px rgba(34, 42, 53, 0.08), 0 24px 108px rgba(47, 48, 55, 0.10)",
        }}
      >
        <motion.div
          style={{
            transform: isHovering
              ? `translate3d(${-mousePosition.x}px, ${-mousePosition.y}px, 0) scale3d(1.03, 1.03, 1)`
              : "translate3d(0px, 0px, 0) scale3d(1, 1, 1)",
            transition: isHovering ? "transform 0.08s cubic-bezier(0.4,0,0.2,1)" : "transform 0.18s cubic-bezier(0.4,0,0.2,1)",
            willChange: "transform",
          }}
          className={cn("h-full w-full px-4 py-10 sm:px-10 flex items-center justify-center", className)}
        >
          <Noise />
          {children}
        </motion.div>
      </div>
    </motion.section>
  );
};

const Noise = () => {
  return (
    <div
      className="absolute inset-0 w-full h-full scale-100 transform opacity-10 [mask-image:radial-gradient(#fff,transparent,75%)] pointer-events-none select-none"
      style={{
        backgroundImage: "url(/noise.webp)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        objectFit: "cover",
      }}
    ></div>
  );
};

export function WobbleCardDemo() {
  return (
    <div className="w-full flex justify-center">
      <WobbleCard
        containerClassName="bg-[#1E41B2] min-h-[220px] sm:min-h-[280px] md:min-h-[320px] max-w-3xl w-full flex items-center justify-center mx-auto"
      >
        <div className="flex flex-col lg:flex-row items-center justify-between w-full gap-8 px-4">
          {/* Left: Text */}
          <div className="max-w-xl text-center lg:text-left">
            <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-4">
              Build forms, analyze responses, and unlock AI-powered insights instantly.
            </h2>
            <p className="text-base md:text-lg text-neutral-200 mb-0">
              Superintelligent, beautiful, and fast. Try it free and see the difference.
            </p>
          </div>
          {/* Right: Button */}
          <div className="flex flex-col items-center lg:items-end gap-3">
            <a
              href="/auth/sign-up"
              className="rounded-md bg-blue-50 text-blue-600 text-base font-semibold py-2 px-6 transition-colors border border-blue-100 hover:bg-blue-100 flex items-center justify-center min-w-[140px] max-w-[180px] cursor-pointer"
            >
              Start Now
            </a>
          </div>
        </div>
      </WobbleCard>
    </div>
  );
}