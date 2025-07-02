"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import React, { useEffect, useId, useRef, useState, useMemo } from "react";

/**
 *  DotPattern Component Props
 *
 * @param {number} [width=16] - The horizontal spacing between dots
 * @param {number} [height=16] - The vertical spacing between dots
 * @param {number} [x=0] - The x-offset of the entire pattern
 * @param {number} [y=0] - The y-offset of the entire pattern
 * @param {number} [cx=1] - The x-offset of individual dots
 * @param {number} [cy=1] - The y-offset of individual dots
 * @param {number} [cr=1] - The radius of each dot
 * @param {string} [className] - Additional CSS classes to apply to the SVG container
 * @param {boolean} [glow=false] - Whether dots should have a glowing animation effect
 * @param {number} [maxDots=12000] - Maximum number of dots to render
 */
interface DotPatternProps extends React.SVGProps<SVGSVGElement> {
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  cx?: number;
  cy?: number;
  cr?: number;
  className?: string;
  glow?: boolean;
  maxDots?: number;
  [key: string]: unknown;
}

/**
 * DotPattern Component
 *
 * A React component that creates an animated or static dot pattern background using SVG.
 * The pattern automatically adjusts to fill its container and can optionally display glowing dots.
 *
 * @component
 *
 * @see DotPatternProps for the props interface.
 *
 * @example
 * // Basic usage
 * <DotPattern />
 *
 * // With glowing effect and custom spacing
 * <DotPattern
 *   width={20}
 *   height={20}
 *   glow={true}
 *   className="opacity-50"
 * />
 *
 * @notes
 * - The component is client-side only ("use client")
 * - Automatically responds to container size changes
 * - When glow is enabled, dots will animate with random delays and durations
 * - Uses framer-motion for animations
 * - Dots color can be controlled via the text color utility classes
 */
export function DotPattern({
  width = 16,
  height = 16,
  x = 0,
  y = 0,
  cx = 1,
  cy = 1,
  cr = 1,
  className,
  glow = false,
  maxDots = 12000,
  ...props
}: DotPatternProps) {
  const id = useId();
  const containerRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [dots, setDots] = useState<any[]>([]);
  const resizeTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Throttled resize handler
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };

    const handleResize = () => {
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
      resizeTimeoutRef.current = setTimeout(updateDimensions, 200);
    };

    // Initial measurement
    updateDimensions();
    
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (resizeTimeoutRef.current) {
        clearTimeout(resizeTimeoutRef.current);
      }
    };
  }, []);

  // Generate dots when dimensions change
  useEffect(() => {
    if (dimensions.width === 0 || dimensions.height === 0) return;
    
    const cols = Math.ceil(dimensions.width / width);
    const rows = Math.ceil(dimensions.height / height);
    
    // Limit total dots, but allow more than before
    const safeMaxDots = Math.min(maxDots, 18000);
    
    // Calculate skip factor to maintain even distribution
    const totalPossibleDots = cols * rows;
    const skipFactor = Math.max(1, Math.ceil(totalPossibleDots / safeMaxDots));
    
    const newDots = [];
    
    // Generate an evenly-spaced grid
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        // Skip dots based on calculated factor to maintain even distribution
        if (skipFactor > 1 && (row * cols + col) % skipFactor !== 0) {
          continue;
        }
        
        // Very small random offset for natural look (minimal for performance)
        const xOffset = (Math.random() * 2 - 1) * (width * 0.02);
        const yOffset = (Math.random() * 2 - 1) * (height * 0.02);
        
        // Calculate animation properties but don't animate all dots
        // Checkerboard pattern: animate only 1/4 of dots
        const isAnimated = (row % 2 === 0 && col % 2 === 0);
        
        // Group animation timings for better performance
        const animGroup = (row + col) % 4;
        
        newDots.push({
          x: col * width + cx + xOffset,
          y: row * height + cy + yOffset,
          delay: animGroup * 0.5,  // 4 delay groups
          duration: 2 + (animGroup % 2),  // 2 duration groups
          opacity: 0.4 + ((row + col) % 3) * 0.1,  // Slightly higher base opacity (0.4 instead of 0.3)
          animated: isAnimated && glow
        });
        
        if (newDots.length >= safeMaxDots) break;
      }
      if (newDots.length >= safeMaxDots) break;
    }
    
    setDots(newDots);
  }, [dimensions, width, height, cx, cy, maxDots, glow]);

  return (
    <svg
      ref={containerRef}
      aria-hidden="true"
      className={cn(
        "pointer-events-none absolute inset-0 h-full w-full",
        className,
      )}
      {...props}
    >
      <defs>
        <radialGradient id={`${id}-gradient`}>
          <stop offset="0%" stopColor="currentColor" stopOpacity="1" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
        </radialGradient>
      </defs>
      
      {/* Static dots (all dots that don't animate) */}
      {dots.filter(dot => !dot.animated).map((dot, index) => (
        <circle
          key={`static-${index}`}
          cx={dot.x}
          cy={dot.y}
          r={cr * 1.05}
          fill={glow ? `url(#${id}-gradient)` : "currentColor"}
          className="text-neutral-400/90"
          opacity={dot.opacity}
        />
      ))}
      
      {/* Animated dots (only 1/4 of all dots) */}
      {dots.filter(dot => dot.animated).map((dot, index) => (
        <motion.circle
          key={`anim-${index}`}
          cx={dot.x}
          cy={dot.y}
          r={cr * 1.05}
          fill={`url(#${id}-gradient)`}
          className="text-neutral-400/90"
          initial={{ opacity: dot.opacity, scale: 1 }}
          animate={{
            opacity: [dot.opacity, dot.opacity + 0.3, dot.opacity],
            scale: [1, 1.4, 1]
          }}
          transition={{
            duration: dot.duration,
            repeat: Infinity,
            repeatType: "reverse",
            delay: dot.delay,
            ease: "easeInOut"
          }}
        />
      ))}
    </svg>
  );
} 