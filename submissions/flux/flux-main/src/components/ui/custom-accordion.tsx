"use client";

import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const Accordion = ({ 
  type, 
  collapsible, 
  className, 
  children 
}: { 
  type: "single" | "multiple"; 
  collapsible?: boolean; 
  className?: string; 
  children: React.ReactNode;
}) => {
  return (
    <div className={className}>
      {children}
    </div>
  );
};

const AccordionItem = ({ 
  value, 
  className, 
  children 
}: { 
  value: string; 
  className?: string; 
  children: React.ReactNode; 
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  return (
    <div className={cn("mb-4", className)}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            isOpen,
            onClick: () => setIsOpen(!isOpen),
          });
        }
        return child;
      })}
    </div>
  );
};

const AccordionTrigger = ({ 
  className, 
  children, 
  isOpen, 
  onClick 
}: { 
  className?: string; 
  children: React.ReactNode; 
  isOpen?: boolean; 
  onClick?: () => void; 
}) => {
  return (
    <button 
      className={cn("flex items-center justify-between w-full", className)} 
      onClick={onClick}
    >
      {children}
      <ChevronDown className={cn(
        "h-5 w-5 shrink-0 text-gray-600 transition-transform duration-300",
        isOpen && "rotate-180"
      )} />
    </button>
  );
};

const AccordionContent = ({ 
  className, 
  children, 
  isOpen 
}: { 
  className?: string; 
  children: React.ReactNode; 
  isOpen?: boolean; 
}) => {
  return isOpen ? (
    <div className={cn("overflow-hidden text-sm transition-all duration-300", className)}>
      <div className="pb-6 pt-2">{children}</div>
    </div>
  ) : null;
};

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }; 