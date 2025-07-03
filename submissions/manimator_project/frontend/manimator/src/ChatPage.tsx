// App.tsx or ChatPage.tsx
import React, { useState, useCallback } from 'react'; // Import useState and useCallback
import './App.css';
import ChatSidePanel from './SideChatBar';
import MediaPreviewInterface from './VideoCanvas';

const MAX_VARIANTS_DISPLAY = 5; // Maximum number of variants to store and display

// Default export for the App component
export default function ChatPage() {
  // 1. State for the video path, initialized to null or a default
  const [currentVideoPath, setCurrentVideoPath] = useState<string | null>(null);
  const [variantVideoPaths, setVariantVideoPaths] = useState<(string | null)[]>([]); // Initialize as an empty array

  // 2. Function to update the video path, to be passed to ChatSidePanel
  const handleVideoSelect = useCallback((newPath: string | null) => {
    setCurrentVideoPath(newPath);

    if (newPath) { // Only add valid, non-null paths
      setVariantVideoPaths(prevPaths => {
        // Remove the new path if it already exists, to move it to the front.
        const filteredPaths = prevPaths.filter(p => p && p !== newPath); // Ensure p is not null before comparing
        // Add the new path to the beginning of the array.
        const updatedPaths = [newPath, ...filteredPaths];
        // Limit to MAX_VARIANTS_DISPLAY.
        return updatedPaths.slice(0, MAX_VARIANTS_DISPLAY);
      });
    }
    // If newPath is null (e.g., error in generation), currentVideoPath becomes null.
    // We don't add null to variantVideoPaths, existing variants remain.
  }, []); // Empty dependency array ensures the function is created only once

  const handleVariantClick = useCallback((variantPath: string | null) => {
    if (variantPath) {
      setCurrentVideoPath(variantPath);
    }
  }, []);

  return (
    <div className="flex w-screen h-screen bg-background text-foreground">
      {/* 3. Pass the handler function to ChatSidePanel */}
      <ChatSidePanel onVideoSelect={handleVideoSelect} />
      <div className="flex-1 overflow-auto flex">
        {/* 4. Pass the currentVideoPath state and variant data to MediaPreviewInterface */}
        <MediaPreviewInterface 
          videoPath={currentVideoPath} 
          variantVideoPaths={variantVideoPaths}
          onVariantClick={handleVariantClick}
        />
      </div>
    </div>
  );
}