"use client";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Play, Plus } from "lucide-react";
import React from 'react'; // Import React if not already

// Props for MediaPreviewInterface
interface MediaPreviewInterfaceProps {
  videoPath?: string | null; // To be passed from a parent component
  variantVideoPaths?: (string | null)[];
  onVariantClick?: (path: string | null) => void;
}

// Props for VideoPreview
interface VideoPreviewProps {
  videoPath?: string | null;
}

// Define the base URL for your backend videos.
// In a real application, this might come from an environment variable.
const BACKEND_VIDEO_BASE_URL = "http://localhost:8000"; // As requested: localhost:8000

function HeaderBar() {
  return (
    <div className="flex items-center justify-between">
      <p className="text-sm font-normal text-muted-foreground">Preview</p>
      <div className="flex items-center gap-4">
        <Button size='sm' variant="outline" onClick={() => console.log("Invite clicked")}>Invite</Button>
        <Button size="sm" onClick={() => console.log("Export clicked")}>Export</Button>
      </div>
    </div>
  );
}

function VideoPreview({ videoPath }: VideoPreviewProps) {
  let fullVideoUrl: string | null = null;

  if (videoPath && videoPath.trim() !== "") {
    // Ensure the base URL does not end with a slash if we are adding one
    const base = BACKEND_VIDEO_BASE_URL.endsWith('/')
      ? BACKEND_VIDEO_BASE_URL.slice(0, -1)
      : BACKEND_VIDEO_BASE_URL;
    // Ensure the videoPath part does not start with a slash if the base already provides it implicitly
    const path = videoPath.startsWith('/') ? videoPath.substring(1) : videoPath;
    fullVideoUrl = `${base}/${path}`;
  }

  return (
    <div className="w-full max-w-[1800px] mx-auto aspect-video bg-background rounded-2xl shadow-lg overflow-hidden flex items-center justify-center">
      {fullVideoUrl ? (
        <video
          key={fullVideoUrl} // Using fullVideoUrl as key helps React re-render correctly if the source changes
          className="w-full h-full object-contain" // 'object-contain' ensures the video fits and maintains aspect ratio
          src={fullVideoUrl} // Use the constructed full URL
          controls // Adds default video controls (play, pause, volume, etc.)
          // autoPlay // Uncomment if you want the video to play automatically (generally not recommended for UX)
          // loop // Uncomment if you want the video to loop
          // muted // Uncomment if you want the video to start muted (often required for autoplay in browsers)
        >
          Your browser does not support the video tag. {/* Fallback message */}
        </video>
      ) : (
        <p className="text-muted-foreground text-center px-4 text-lg">
          {/* Informative placeholder text */}
          . . .
        </p>
      )}
    </div>
  );
}

function VariantPreviewBoxes({ 
  variantVideoPaths, 
  onVariantClick 
}: { 
  variantVideoPaths?: (string | null)[]; 
  onVariantClick?: (path: string | null) => void; 
}) {
  const totalDisplayBoxes = 5; // We will aim for 5 boxes total for layout consistency
  
  // Ensure variantVideoPaths is an array, even if undefined or null, for consistent mapping
  const validVariantPaths = (variantVideoPaths || []).filter(path => path !== null) as string[];

  const placeholdersNeeded = Math.max(0, totalDisplayBoxes - validVariantPaths.length);

  return (
    <div className="flex items-center gap-4">
      {validVariantPaths.map((path, index) => (
        <Button
          key={`variant-${index}-${path}`} // Using path in key for better stability if order changes
          variant="outline"
          className="w-[91px] h-[92px] bg-popover border-border rounded-lg p-1 text-xs overflow-hidden flex items-center justify-center disabled:opacity-100 disabled:cursor-default"
          onClick={() => onVariantClick && path ? onVariantClick(path) : null}
          disabled={!path} // Should always be a valid path here due to filter, but good practice
          title={path ? `Load: ${path.split('/').pop()}` : "Empty variant slot"}
        >
          {path ? (
            // Simple text representation for now. Could be a thumbnail in the future.
            <span className="truncate">{`Variant ${index + 1}`}</span> // Using index + 1 for display
          ) : (
            // This case should ideally not be reached for variant paths due to filtering
            <span className="text-muted-foreground/50">...</span> 
          )}
        </Button>
      ))}
      {[...Array(placeholdersNeeded)].map((_, index) => (
         <div key={`placeholder-${index + validVariantPaths.length}`} className="w-[91px] h-[92px] bg-popover/50 border border-border/50 rounded-lg flex items-center justify-center">
           <span className="text-muted-foreground/30">...</span>
         </div>
      ))}
    </div>
  );
}

function VariantSection({ 
  variantVideoPaths, 
  onVariantClick 
}: { 
  variantVideoPaths?: (string | null)[]; 
  onVariantClick?: (path: string | null) => void; 
}) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 w-full max-w-[1800px] px-2">
        <p className="text-sm font-normal text-muted-foreground text-center">Preview all variants</p>
        <div className="flex items-center gap-4">
          <VariantPreviewBoxes variantVideoPaths={variantVideoPaths} onVariantClick={onVariantClick} />
          <Button
            variant="outline"
            size="icon"
            className="opacity-50 bg-background rounded-full w-8 h-8 p-0 flex items-center justify-center hover:bg-neutral-100" // hover:bg-muted/80 might be better for dark mode
            onClick={() => console.log("Add clicked")}
            aria-label="Add"
          >
            <Plus className="w-4 h-4 text-foreground" />
          </Button>
        </div>
      </div>
    );
  }

function FloatingPlayButton() {
  return (
    <div className="absolute bottom-8 right-8 z-10">
      <Button
        size="icon"
        className="w-16 h-16 bg-background rounded-full shadow-lg hover:bg-neutral-100"
        aria-label="Play"
        onClick={() => console.log("Play clicked")}
      >
        <Play className="w-9 h-9 text-primary" />
      </Button>
    </div>
  );
}

export default function MediaPreviewInterface({ 
  videoPath, 
  variantVideoPaths, 
  onVariantClick 
}: MediaPreviewInterfaceProps) {
  return (
    <div className="relative w-full h-full flex flex-col">
      <div className="flex-1 flex flex-col bg-muted p-4 lg:p-6 overflow-hidden rounded-2xl m-4">
        <div className="flex flex-col gap-3 max-w-[1800px] w-full mx-auto">
          <HeaderBar />
          <Separator />
        </div>
        <div className="flex-1 flex flex-col items-center justify-center gap-6 lg:gap-8 overflow-auto p-2">
          <VideoPreview videoPath={videoPath} />
          <VariantSection variantVideoPaths={variantVideoPaths} onVariantClick={onVariantClick} />
        </div>
      </div>
      <FloatingPlayButton />
    </div>
  );
}