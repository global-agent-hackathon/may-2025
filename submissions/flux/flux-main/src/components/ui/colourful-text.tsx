"use client";
import React from "react";
import { motion } from "framer-motion";

export function ColorfulText({ text }: { text: string }) {
  // Blue-themed colors that match the UI
  const colors = [
    "rgb(37, 99, 235)",  // blue-600
    "rgb(59, 130, 246)", // blue-500
    "rgb(96, 165, 250)", // blue-400
    "rgb(59, 130, 246)", // blue-500
    "rgb(37, 99, 235)",  // blue-600
  ];

  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCount((prev) => prev + 1);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return text.split("").map((char, index) => (
    <motion.span
      key={`${char}-${count}-${index}`}
      initial={{ color: colors[0] }}
      animate={{
        color: colors[index % colors.length],
        y: [0, -2, 0],
        scale: [1, 1.01, 1],
      }}
      transition={{
        duration: 0.8,
        delay: index * 0.03,
      }}
      className="inline-block whitespace-pre font-sans tracking-tight"
    >
      {char}
    </motion.span>
  ));
} 