// src/components/LoadingIndicator.tsx
"use client";

import React, { useState, useEffect } from "react";

interface LoadingIndicatorProps {
  isLoading: boolean;
}

export default function LoadingIndicator({ isLoading }: LoadingIndicatorProps) {
  // State for cycling through loading messages
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const loadingMessages = [
    "🔍 Analyzing provided documentation...", // Search/scan
    "🧠 Understanding API endpoints and data models...", // Brain/thinking
    "🏗️ Designing optimal SDK structure for TypeScript...", // Construction/blueprint
    "⚙️ Generating core API client methods...", // Gears/processing
    "📝 Creating TypeScript type definitions...", // Memo/typing
    "🔗 Integrating request/response handling...", // Link/connection
    "✨ Optimizing code for readability and maintainability...", // Sparkles/improvement
    "📖 Generating usage examples and documentation snippets...", // Open book/documentation
    "✅ Performing final checks and packaging the SDK...", // Checkmark/completion
    "⏳ Almost there! Just a few more steps to go...", // Hourglass/waiting
  ];

  // State for cycling through "Did You Know?" facts
  const [didYouKnowIndex, setDidYouKnowIndex] = useState(0);
  const didYouKnowFacts = [
    "💡 Did you know? Type-Scribe AI leverages LLMs to infer API behavior.",
    "🌟 SDKs improve developer experience by abstracting complex API calls.",
    "💡 TypeScript adds static typing, reducing runtime errors in large apps.",
    "🌟 Type-Scribe AI supports docs from OpenAPI, Markdown, PDF, and more!",
    "💡 Our goal is to make SDK development as simple as clicking a button.",
  ];

  // Emojis for the main title animation
  const mainTitleEmojis = ["🧠", "🤖", "⚙️", "✨"]; // Brain, Robot, Gear, Sparkles
  const [mainTitleEmojiIndex, setMainTitleEmojiIndex] = useState(0);

  useEffect(() => {
    let messageInterval: NodeJS.Timeout;
    let factInterval: NodeJS.Timeout;
    let titleEmojiInterval: NodeJS.Timeout;

    if (isLoading) {
      messageInterval = setInterval(() => {
        setLoadingMessageIndex(
          (prevIndex) => (prevIndex + 1) % loadingMessages.length
        );
      }, 5000);

      factInterval = setInterval(() => {
        setDidYouKnowIndex(
          (prevIndex) => (prevIndex + 1) % didYouKnowFacts.length
        );
      }, 10000);

      titleEmojiInterval = setInterval(() => {
        setMainTitleEmojiIndex(
          (prevIndex) => (prevIndex + 1) % mainTitleEmojis.length
        );
      }, 1500);
    } else {
      setLoadingMessageIndex(0);
      setDidYouKnowIndex(0);
      setMainTitleEmojiIndex(0);
    }

    return () => {
      clearInterval(messageInterval);
      clearInterval(factInterval);
      clearInterval(titleEmojiInterval);
    };
  }, [
    isLoading,
    loadingMessages.length,
    didYouKnowFacts.length,
    mainTitleEmojis.length,
  ]);

  if (!isLoading) {
    return null; // Don't render anything if not loading
  }

  return (
    <div className="my-4 text-blue-400 text-lg text-center flex flex-col items-center w-full max-w-xl p-6 bg-gray-900 rounded-lg shadow-xl relative overflow-hidden loading-animation-bg">
      {/* Abstract background animation */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="abstract-pattern-grid"></div>
        <div className="abstract-pulse-glow"></div>
      </div>
      {/* Content */}
      <div className="relative z-10 flex flex-col items-center">
        <div className="flex items-center mb-4">
          <span className="mr-3 text-3xl animate-pulse transition-opacity duration-300">
            {mainTitleEmojis[mainTitleEmojiIndex]}
          </span>{" "}
          <span className="text-2xl font-bold text-white">
            Generating your SDK...
          </span>
          <span className="animate-spin ml-3">
            <svg
              className="h-6 w-6 text-blue-400"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </span>
        </div>

        <p
          key={`message-${loadingMessageIndex}`}
          className="text-base italic text-gray-300 mb-4 animate-fade-in"
        >
          {loadingMessages[loadingMessageIndex]}
        </p>

        <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden mb-4">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-progress-indefinite"
            style={{ animationDuration: "60s" }}
          ></div>
        </div>

        <p className="text-sm text-gray-500 mb-2">
          This process can take up to 1-2 minutes due to complex AI
          computations.
        </p>
        <p
          key={`fact-${didYouKnowIndex}`}
          className="text-xs text-gray-400 animate-fade-in"
        >
          {didYouKnowFacts[didYouKnowIndex]}
        </p>
      </div>

      {/* Styles for the animations specific to this component */}
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        .animate-fade-in {
          animation: fadeIn 0.5s ease-in-out forwards;
        }

        @keyframes progressIndefinite {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
        .animate-progress-indefinite {
          animation: progressIndefinite 2s linear infinite;
          width: 50%;
        }

        /* Abstract Grid Pattern */
        .abstract-pattern-grid {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-image: linear-gradient(
              to right,
              rgba(59, 130, 246, 0.1) 1px,
              transparent 1px
            ),
            linear-gradient(
              to bottom,
              rgba(59, 130, 246, 0.1) 1px,
              transparent 1px
            );
          background-size: 20px 20px;
          animation: grid-pulse-fade 15s infinite ease-in-out alternate;
          opacity: 0.1;
          z-index: 0;
        }

        @keyframes grid-pulse-fade {
          0%,
          100% {
            background-position: 0 0;
            opacity: 0.1;
          }
          50% {
            background-position: 20px 20px;
            opacity: 0.2;
          }
        }

        /* Abstract Pulsing Glow */
        .abstract-pulse-glow {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          width: 150px;
          height: 150px;
          background-image: radial-gradient(
            circle at center,
            rgba(168, 85, 247, 0.3) 0%,
            transparent 70%
          );
          border-radius: 50%;
          animation: glow-pulse 4s infinite ease-in-out alternate;
          z-index: 0;
        }

        @keyframes glow-pulse {
          0%,
          100% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 0.8;
          }
          50% {
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 1;
          }
        }

        .loading-animation-bg {
          background-color: #1a202c;
        }
      `}</style>
    </div>
  );
}
