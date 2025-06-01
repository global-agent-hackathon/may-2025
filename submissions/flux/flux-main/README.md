# Flux: Superintelligent Form Builder with Agents and Memory

Flux is a next-gen form platform powered by intelligent agents, multi-step tool use, and memory. Users can describe what they want — and Flux builds the form, wires the logic, and connects responses to insights or external APIs.

## Features

- **Natural Language Form Creation**: Describe your form in plain English, and Flux builds it for you
- **Intelligent Responses**: Understands form data with context-aware agents
- **User-Friendly Interface**: Modern, clean UI built with Next.js 14, Tailwind, and Shadcn UI
- **Persistent Memory**: Remembers form evolution and adapts to your edits
- **Powerful Action System**: Connect forms to external services like Slack, Gmail, Notion, and more
- **Organization Tools**: Workspaces and favorites for efficient form management
- **30-Day Soft Delete**: Trashed forms are recoverable for 30 days before permanent deletion

## Technical Stack

- **Frontend**: Next.js 14, Tailwind CSS, Shadcn UI components
- **State Management**: Zustand for efficient state updates
- **Database**: PostgreSQL with Prisma ORM
- **Auth**: Clerk for secure authentication and user management
- **AI**: Gemini API for language understanding and response processing
- **Agent Orchestration**: Agno for agentic workflows
- **Memory Layer**: Mem0 for context persistence
- **Link Analysis**: Firecrawl for external URL understanding

## Getting Started

### Prerequisites

- Node.js 18+ or Bun
- PostgreSQL database (or use Neon.tech for serverless Postgres)
- Clerk account for authentication
- Gemini API key for AI functionality

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flux.git
   cd flux
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   bun install
   ```

3. Set up environment variables:
   ```
   # Create a .env file with the following variables
   DATABASE_URL="your-postgresql-connection-string"
   CLERK_SECRET_KEY="your-clerk-secret-key"
   CLERK_PUBLISHABLE_KEY="your-clerk-publishable-key"
   GEMINI_API_KEY="your-gemini-api-key"
   ```

4. Run the database migrations:
   ```bash
   npx prisma migrate dev
   ```

5. Start the development server:
   ```bash
   npm run dev
   # or
   bun dev
   ```

6. Open [http://localhost:3000](http://localhost:3000) to see the app.

## Architecture

Flux is built using a modern React architecture with Next.js App Router:
- **Client & Server Components**: Properly separated for optimal performance
- **API Routes**: RESTful endpoints for data operations
- **Prisma ORM**: Type-safe database access
- **ShadCN UI**: Accessible component library with Tailwind
- **Clerk Auth**: Secure user authentication and management

## Key User Flows

1. **Form Creation**:
   - User describes form needs in natural language
   - AI agent generates form structure and validation
   - User can refine with additional commands

2. **Response Analysis**:
   - Form submissions are analyzed automatically
   - Sentiment, trends, and key insights extracted
   - Custom actions triggered based on content

3. **Data Organization**:
   - Forms grouped in workspaces for easy management
   - Star forms to add them to favorites
   - Trash system provides 30-day recovery period

## Contributing

We welcome contributions to Flux! Please check out our [contribution guidelines](CONTRIBUTING.md) to get started.

## License

MIT

---

Built for the Global Agent Hackathon, showcasing agentic reasoning, persistent memory, and multi-step tool use.
