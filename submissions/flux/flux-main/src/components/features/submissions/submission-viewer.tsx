import React from "react";
import { cn } from "@/lib/utils";

interface SubmissionViewerProps {
  data: any;
  schema: any;
}

export function SubmissionViewer({ data, schema }: SubmissionViewerProps) {
  // If no schema is provided, display raw data
  if (!schema || !schema.fields) {
    return (
      <div className="rounded-md border p-4 overflow-auto">
        <pre className="text-sm">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    );
  }

  // Display formatted data based on schema
  return (
    <div className="space-y-6">
      {schema.fields.map((field: any) => {
        // Get the field value from data
        const value = data[field.id];
        
        // Skip empty values
        if (value === undefined || value === null || value === "") {
          return null;
        }

        // Format the display value based on field type
        let displayValue;
        switch (field.type) {
          case "checkbox":
            displayValue = value ? "Yes" : "No";
            break;
          case "multiple_choice":
          case "dropdown":
          case "multi_select":
            if (Array.isArray(value)) {
              displayValue = value.join(", ");
            } else {
              displayValue = value;
            }
            break;
          case "date":
          case "time":
            displayValue = value;
            break;
          case "file":
            displayValue = "File uploaded";
            break;
          default:
            displayValue = value;
        }

        // Handle header fields (h1, h2, h3)
        if (field.type === "h1" || field.type === "h2" || field.type === "h3") {
          const Tag = field.type;
          return (
            <div key={field.id} className="border-b pb-2">
              {React.createElement(Tag, {
                className: cn(
                  field.type === "h1" && "text-xl font-bold",
                  field.type === "h2" && "text-lg font-semibold",
                  field.type === "h3" && "text-base font-medium",
                ),
                children: field.label
              })}
            </div>
          );
        }

        // Regular fields
        return (
          <div key={field.id} className="border-b pb-4">
            <div className="font-medium mb-1">{field.label}</div>
            <div className="text-gray-700 dark:text-gray-300 break-words">
              {displayValue}
            </div>
          </div>
        );
      })}
    </div>
  );
} 