import React from "react";
import { cn } from "@/lib/utils";

interface FormattedDateProps {
  date: Date | string;
  format?: "relative" | "short" | "long" | "full";
  className?: string;
}

function FormattedDate({
  date,
  format = "short",
  className,
}: FormattedDateProps) {
  if (!date) return null;
  
  const dateObj = typeof date === "string" ? new Date(date) : date;
  
  if (isNaN(dateObj.getTime())) {
    return <span className={className}>Invalid date</span>;
  }
  
  if (format === "relative") {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return <span className={cn("text-nowrap", className)}>just now</span>;
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return <span className={cn("text-nowrap", className)}>{minutes} {minutes === 1 ? "minute" : "minutes"} ago</span>;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return <span className={cn("text-nowrap", className)}>{hours} {hours === 1 ? "hour" : "hours"} ago</span>;
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400);
      return <span className={cn("text-nowrap", className)}>{days} {days === 1 ? "day" : "days"} ago</span>;
    }
  }
  
  if (format === "short") {
    return (
      <span className={className}>
        {dateObj.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        })}
      </span>
    );
  }
  
  if (format === "long") {
    return (
      <span className={className}>
        {dateObj.toLocaleDateString("en-US", {
          weekday: "short",
          month: "short",
          day: "numeric",
          year: "numeric",
        })}
      </span>
    );
  }
  
  if (format === "full") {
    return (
      <span className={className}>
        {dateObj.toLocaleDateString("en-US", {
          weekday: "long",
          month: "long",
          day: "numeric",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })}
      </span>
    );
  }
  
  return <span className={className}>{dateObj.toDateString()}</span>;
} 


export { FormattedDate }