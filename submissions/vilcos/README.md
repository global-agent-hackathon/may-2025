# <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos.png" alt="Vilcos Logo" width="100" align="left" style="margin-right: 10px;"/> Vilcos: Your Website's AI-Powered Developer & Content Manager

&nbsp;
&nbsp;

**Vilcos transforms how you create and manage your website. Instead of a traditional CMS or a separate admin panel, your website gets its own dedicated, self-hosted AI web developer agent. Simply chat with it to build your initial site, make updates, manage content on any page, and evolve your entire project over time – all through natural language!**

<p align="center">
  <img src="https://img.shields.io/badge/Built%20with-Agno%20Framework-blue?style=for-the-badge" alt="Built with Agno Framework"/>
  <img src="https://img.shields.io/badge/AI%20Powered-OpenAI%20GPT--4-green?style=for-the-badge" alt="AI Powered by OpenAI"/>
  <img src="https://img.shields.io/badge/Self%20Hosted-Docker%20Ready-orange?style=for-the-badge" alt="Self Hosted"/>
</p>

## 🎬 Watch Vilcos in Action

[![Vilcos Demo Video](https://img.youtube.com/vi/zdjePVJt8s4/maxresdefault.jpg)](https://www.youtube.com/watch?v=zdjePVJt8s4)

<p align="center"><em>▶️ Click the image above to watch the Vilcos demo video</em></p>

<p align="center">
  <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos-demo.gif" alt="Vilcos Demo" width="80%"/>
</p>

Vilcos is an AI-powered framework that empowers you to:
-   **Create & Build:** Generate new pages and entire site structures.
-   **Edit & Update:** Modify HTML, CSS (including Tailwind CSS), JavaScript, and importantly, the content within your pages.
-   **Manage & Evolve:** Iteratively refine your website, add new sections, or change layouts, much like a CMS, but through a conversational interface with your own AI agent.

<p align="center">
  <img src="https://raw.githubusercontent.com/level09/vilcos/master/assets/vilcos-robot.gif" alt="Vilcos Robot" width="250"/>
</p>

This self-hosted agent acts as your personal web development assistant, understanding your requests and applying changes directly to your project files.

## Why Vilcos?

Traditional website builders lock you into their platforms, while CMSs require complex setup and maintenance. Vilcos bridges this gap by giving you a **self-hosted AI agent** that understands natural language and works directly with your files. Built on the **Agno framework**, it combines the power of modern AI with the flexibility of owning your own infrastructure.

**Key Innovation**: Instead of learning another interface, you simply talk to your website's AI agent in plain English. It handles the technical implementation while you focus on your content and vision.

## Features

- **AI-Powered Website Management**: Use natural language to create, edit, and manage your entire website – pages, content, and structure.
- **Live Preview**: See changes in real-time as you interact with your AI agent.
- **File Watching**: Automatic synchronization for instant feedback during development.
- **Static Publishing**: Generate optimized static sites ready for production.
- **Self-Hosted Agent**: You control the core AI agent framework.
- **Docker Deployment**: Simple deployment option available for the published static site.

## Quick Start

### Option 1: Using npx (Recommended)

The fastest way to get started with Vilcos:

```bash
# Create a new Vilcos project
npx create-vilcos-app my-website

# Or initialize in the current directory
npx create-vilcos-app

# Start the application
cd my-website  # If you specified a project name
./vilcos start
```

### Option 2: Manual Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/level09/vilcos.git
    cd vilcos
    ```

2.  **Install Dependencies:**
    *(Ensure you have Python 3.7+ and Node.js 16+ installed)*
    ```bash
    ./vilcos install
    ```

3.  **Configure OpenAI API Key:**
    Vilcos uses OpenAI GPT-4 for its AI capabilities. You can also use any OpenAI-compatible API endpoint.
    *   You can set the `OPENAI_API_KEY` environment variable before starting:
        ```bash
        export OPENAI_API_KEY='your_api_key_here'
        ```
    *   Alternatively, when you run `./vilcos start` for the first time, you will be prompted to enter your API key. This key will be saved to a local `.env` file for future use.
    
    You can obtain an API key from [OpenAI Platform](https://platform.openai.com/account/api-keys).
    
    > **Note**: Support for additional AI models (Anthropic Claude, local models, etc.) will be added in future versions.

4.  **Start the Application:**
    ```bash
    ./vilcos start
    ```

    This will automatically copy default templates to the `templates/` directory if none exist.
    The `templates/` directory is excluded from git to keep your repository clean.

Then access:
- **AI Management**: http://localhost:8000 (login: admin/password)
- **Website Preview**: http://localhost:3000

## Enhanced Features (Optional)

Vilcos integrates with cutting-edge AI services to provide advanced capabilities:

### 🧠 Persistent Memory with Mem0
Your AI agent remembers user preferences, project history, and context across sessions - creating truly personalized development experiences.

```bash
# Install package
pip install mem0ai

# Enable in .env file
ENABLE_MEM0=true
MEM0_API_KEY=your_mem0_api_key
```

### 🌐 Web Research with Firecrawl
Analyze any website for design inspiration, extract content ideas, or research competitor layouts directly through natural language commands.

```bash
# Install package  
pip install firecrawl-py

# Enable in .env file
ENABLE_FIRECRAWL=true
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### Quick Install All Enhanced Features
```bash
# Install all optional packages at once
pip install -r requirements-optional.txt

# Then enable in .env file
ENABLE_MEM0=true
MEM0_API_KEY=your_mem0_api_key
ENABLE_FIRECRAWL=true
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

## Using the Application

In the AI Management Interface, you can:
- Create new pages by clicking "🆕 Create New Page" 
- Edit existing pages with the "✏️ Edit" buttons
- Preview your website with the "🔍 Live Preview" button
- Publish your site with the "📦 Publish Website" button

### AI Chat Examples
- **Create**: "Create a new page called about.html with an about section"
- **Edit**: "Add a navigation bar to index.html"
- **Style**: "Update index.html to use a blue color scheme"
- **List**: "Show me all templates"

## Project Structure

```
vilcos/
├── app.py                 # Main Chainlit AI interface with Agno agent
├── vilcos                 # CLI script for all operations
├── start.sh               # Development startup orchestrator
├── watch-templates.js     # Template file watcher for real-time sync
├── publish.sh             # Static site generator with optimizations
├── deploy.sh              # Docker deployment script
├── force-rebuild.sh       # Clean rebuild utility
├── main.py                # Alternative entry point
├── chainlit.md            # Chainlit configuration
├── requirements.txt       # Core Python dependencies
├── requirements-optional.txt # Enhanced features (mem0, firecrawl)
├── package.json           # Node.js dependencies and scripts
├── vite.config.js         # Vite build configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── publish-functions.js   # Publishing utilities
├── post-process.js        # Build post-processing
├── CLAUDE.md              # Development guidance
├── assets/                # Static assets and branding
│   ├── vilcos.png         # Logo
│   ├── vilcos-demo.gif    # Demo animation
│   ├── vilcos-robot.gif   # Robot animation
│   └── default-templates/ # Default template files
├── templates/             # Website templates (user-editable, gitignored)
│   ├── index.html         # Main page template
│   ├── about.html         # About page template
│   ├── src/               # CSS and JS source files
│   └── dist/              # Development build (generated)
├── packages/              # NPX package for distribution
│   └── vilcos-init/       # create-vilcos-app package
├── docker-deploy/         # Docker deployment configurations
├── public/                # Production build (generated)
└── .chainlit/             # Chainlit session data
```

## Available Commands

```bash
./vilcos help      # Show available commands
./vilcos start     # Start all components
./vilcos ai        # Start Chainlit AI interface only
./vilcos dev       # Start website preview only
./vilcos watch     # Start file watcher only
./vilcos publish   # Generate static site
./vilcos deploy    # Deploy with Docker (simple, single container)
./vilcos logs      # View application logs
./vilcos clean     # Clean generated files
```

## Development Workflow

Vilcos operates in two distinct modes to support both development/editing and production deployment.

### 1. Development Mode (Edit & Preview)
1. **Develop and Edit**:
   - Use the AI-powered interface to create/edit templates
   - Files are built to `templates/dist/` for development preview
   - Preview changes in real-time at http://localhost:3000

### 2. Production Mode (Static Publishing)
1. **Publish**:
   - When satisfied, publish your site as static files: `./vilcos publish`
   - This creates optimized files in the `public/` directory with production settings
2. **Deploy**:
   - Deploy with Docker: `./vilcos deploy`
   - This creates a containerized version with Caddy web server for optimal performance and security

### 3. Cloud Deployment
Vilcos generates production-ready static files with a Docker configuration. The generated setup includes:
- Optimized static files in the `public/` directory
- Docker container with Caddy web server
- Production-ready configuration

For cloud deployment, you can use any platform that supports Docker containers or static file hosting. Always run `./vilcos publish` first to generate the latest static files.

## Understanding the Build Process

1. **Development builds** go to `templates/dist/` and are used for the preview server
2. **Production builds** go to `public/` and include additional optimizations and configurations
3. When template changes aren't reflected in deployment, use `./force-rebuild.sh` to clear the build cache

## Troubleshooting

- **Template changes not appearing**: Run `./force-rebuild.sh` followed by `./vilcos deploy`
- **OpenAI API Key**: You'll be prompted for your key when starting; get one at https://platform.openai.com/account/api-keys
- **Port Conflicts**: If ports 8000 or 3000 are in use, edit the port numbers in `start.sh`
- **Logs**: Check logs with `./vilcos logs` to diagnose issues
- **Content Security Policy**: If embedding external content (YouTube, etc.), check the CSP in `publish.sh`

## Requirements

- Python 3.7+
- Node.js 16+
- npm 8+
- OpenAI API key (or OpenAI-compatible API endpoint)

## License

MIT 