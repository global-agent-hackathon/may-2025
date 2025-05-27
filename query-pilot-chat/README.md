# Poly Tutor

A modern, AI-powered tutoring platform with real-time streaming responses and multi-subject support. Built with React, TypeScript, and Tailwind CSS.

## Features

### Intelligent Tutoring
- **Real-time Streaming**: Get instant, token-by-token responses as the AI generates them
- **Multi-Subject Support**:
  - 🔭 **Physics**: Complex physics concepts explained with visual aids
  - ⚗️ **Chemistry**: Chemical concepts and reactions
  - 📐 **Mathematics**: Step-by-step mathematical solutions
  - 🌍 **Language Learning**: Complete language tutoring system

### Language Learning Features
- **Grammar Explanations**: Detailed breakdowns of language rules
- **Vocabulary Building**: Contextual vocabulary lists
- **Pronunciation Guides**: IPA and pronunciation tips
- **Cultural Context**: Cultural insights and usage notes
- **Practice Dialogues**: Interactive conversation examples
- **Multi-Language Support**:
  - English (en)
  - French (fr)
  - Spanish (es)
  - German (de)
  - Italian (it)
  - Japanese (ja)
  - Chinese (zh)

### Smart Features
- **Subject Validation**: Automatic detection and suggestion of correct subject areas
- **Dark/Light Mode**: Automatic theme switching based on system preferences
- **Markdown Support**: Rich text formatting for explanations and examples
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

### Frontend Architecture
```
query-pilot-chat/
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components
│   │   │   ├── select.tsx
│   │   │   └── markdown.tsx
│   │   ├── ChatContainer.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   └── TutorSelect.tsx
│   ├── services/
│   │   └── api.ts        # API integration
│   └── styles/
│       └── globals.css   # Global styles
├── public/
└── config files...
```

### Core Technologies
- **React 18** with TypeScript
- **Vite** for development and building
- **TailwindCSS** for styling
- **Shadcn UI** for component library
- **Lucide React** for icons
- **React Markdown** for content rendering

### Key Dependencies
```json
{
  "react": "^18.x",
  "typescript": "^5.x",
  "tailwindcss": "^3.x",
  "lucide-react": "latest",
  "react-markdown": "latest",
  "axios": "latest"
}
```

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn or bun

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd query-pilot-chat
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
bun install
```

3. Create a `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
# or
bun dev
```

The application will be available at `http://localhost:5173`

## Component Structure

### Main Components
- **ChatContainer**: Main chat interface and state management
- **ChatMessage**: Message rendering with support for different content types
- **ChatInput**: User input handling
- **TutorSelect**: Subject and language selection

### UI Components
- **Select**: Custom select component with search
- **Markdown**: Enhanced markdown rendering with syntax highlighting

## API Integration

The `api.ts` service handles all communication with the backend:

```typescript
interface TutoringResponse {
  type: string;
  content: string;
  grammar?: string;
  vocabulary?: string;
  pronunciation?: string;
  culture?: string;
  dialogue?: string;
}

// Example API call
const response = await tutorApi.streamExplain(
  subject,
  query,
  onData,
  languageCode
);
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Guidelines

- Follow TypeScript best practices
- Use functional components with hooks
- Maintain consistent styling with Tailwind
- Write meaningful commit messages
- Keep components small and focused

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Shadcn UI for the beautiful component library
- Lucide for the icon set
- The React team for the amazing framework
