# Memory Dashboard

The Memory Dashboard provides users with a comprehensive interface to explore their interaction history and manage memory preferences.

## Features

### 🔍 Search Memories
- Search through stored memories and interactions
- Filter by memory type
- View memory metadata and context

### 📋 Form History
- View recent form interactions and submissions
- Track form creation, editing, and analysis activities
- See interaction timestamps and details

### ⚙️ Preferences
- Manage memory retention settings
- Configure privacy levels
- View tracked categories

## Components

### MemoryDashboard
Main dashboard component that provides:
- Tabbed interface for different memory views
- Search functionality
- Loading states and error handling
- Responsive design

## API Integration

The dashboard integrates with the backend memory service through:
- `/api/memory/search` - Search memories
- `/api/memory/form-history` - Get form interaction history
- `/api/memory/user-preferences` - Get user preferences
- `/api/memory/user-context` - Get relevant context

## Usage

The Memory Dashboard is accessible at `/dashboard/memory` and requires user authentication through Clerk.

## Backend Integration

The frontend communicates with the Flux Agent backend which uses Mem0 for persistent memory storage. The backend provides:
- Memory search and retrieval
- Form interaction tracking
- User preference management
- Context-aware responses

## Security

- All API routes require user authentication
- User data is isolated by user ID
- Memory data is stored securely through Mem0 