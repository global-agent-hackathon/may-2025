# Intersectx Frontend

A modern React-based application for company analysis and research, similar to Crunchbase.

## Features

- Home page with trending news and company search
- Company Analysis page with detailed metrics and insights
- IntersectxChat for AI-powered conversations
- Research page for document analysis and company research

## Tech Stack

- React with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Router for navigation
- Headless UI for accessible components
- React Dropzone for file uploads

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

- `/src/components` - Reusable UI components
- `/src/pages` - Page components
- `/src/assets` - Static assets
- `/src/types` - TypeScript type definitions

## Development

The project uses:
- TypeScript for type safety
- Tailwind CSS for styling
- ESLint for code linting
- Prettier for code formatting

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

# Intersectx Chat Implementation

This project implements a chat interface for the Intersectx application, designed to match the Agent Chat UI style provided in the requirements.

## Features

- Modern, clean UI with a white background and minimalist design
- Supports chat messages with different message types: human, AI, and tool calls
- Toggle for hiding tool call messages 
- Loading indicators for message processing
- Support for thread management (planned for backend implementation)

## Component Structure

- `src/providers/ChatProvider.tsx` - Context provider for chat state management
- `src/components/chat/ChatContainer.tsx` - Main chat interface container
- `src/components/chat/MessageBubble.tsx` - Individual message display component
- `src/components/chat/ChatInput.tsx` - Input component for sending messages
- `src/components/ui/Switch.tsx` - Toggle switch UI component
- `src/components/ui/Label.tsx` - Label UI component

## API Integration

The implementation is ready to connect to the API endpoints defined in `API.md`, including:

- Chat threads management (GET, POST, PATCH, DELETE /chat/threads)
- Message sending (POST /chat/threads/{threadId}/messages)
- Assistant responses (GET /chat/threads/{threadId}/messages/{messageId}/response)
- File uploads (POST /files/upload/initiate, POST /files/upload/complete)

## Backend Requirements

To fully implement this chat interface, the backend needs to implement the APIs defined in `API.md`, specifically:

1. Thread management endpoints for creating and retrieving chat threads
2. Message sending and response endpoints
3. File upload processing endpoints

## Design Changes

The UI has been updated to match the Agent Chat UI provided in the requirements:

- Changed from dark, glassmorphic UI to clean, white interface
- Simplified message bubbles with appropriate colors
- Added "Hide Tool Calls" toggle
- Redesigned input area with cancel button during loading

The typeface FK Grotesk is chosen for its versatility and support for many of the world's major languages,