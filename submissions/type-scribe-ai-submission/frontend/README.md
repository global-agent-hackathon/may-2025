# Type-Scribe AI: Frontend

This repository contains the Next.js frontend application for **Type-Scribe AI**, an intelligent agent system designed to automate the creation of TypeScript API SDKs directly from existing API documentation. This frontend provides the user interface for interacting with the backend AI agents, allowing users to input documentation sources and configure the SDK generation process.


## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Environment Configuration](#3-environment-configuration)
  - [4. Connect to the Backend](#4-connect-to-the-backend)
  - [5. Run the Development Server](#5-run-the-development-server)
- [Project Structure](#project-structure)
- [Scripts Available](#scripts-available)


## Features

*   **Documentation Input**: Upload API documentation files (like READMEs) or provide a URL to online documentation.
*   **SDK Configuration**: Specify the desired SDK name, version, and base URL for the generated SDK.
*   **Live Progress**: Visual indicators and messages to keep the user informed during the SDK generation process.
*   **Generated Code Display**: View the generated TypeScript SDK code directly in the browser with syntax highlighting.
*   **Usage Example Display**: See an example of how to use the newly generated SDK.
*   **Download Functionality**: Easily download the generated SDK as a `.ts` file.
*   **Error Handling**: Clear error messages for issues during the generation process.


## Technologies Used

This frontend application is built using modern web technologies:

*   **Next.js 15.1.8**: React framework for production.
*   **React 19.x**: A JavaScript library for building user interfaces.
*   **TypeScript**: A typed superset of JavaScript that compiles to plain JavaScript.
*   **Tailwind CSS**: A utility-first CSS framework for rapidly styling the application.
*   **react-syntax-highlighter**: For elegant display of generated code.


## Prerequisites

Before running this application, ensure you have the following installed:

*   **Node.js**: Version 18.x or higher (LTS recommended).
*   **npm** or **Yarn** or **pnpm** or **bun**: A package manager for Node.js.


## Getting Started

Follow these steps to set up and run the frontend application locally:

### 1. Clone the repository

```bash
git clone https://github.com/808vita/type-scribe-ai-frontend.git
cd type-scribe-ai-frontend
```

### 2. Install Dependencies
Using npm:

```bash
npm install
```
Using yarn:

```bash
yarn install
```
Using pnpm:

```bash
pnpm install
```
Using bun:

```bash
bun install
```

### 3. Environment Configuration
Create a `.env.local` file in the root of the `type-scribe-ai-frontend` directory. This file will store environment variables specific to your local setup.

Copy the contents of `.env.example` into your new `.env.local` file:

```env
# .env.example
# Point to your FastAPI backend.
# If running locally, it's usually http://localhost:8000
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
```
Important: Ensure `NEXT_PUBLIC_BACKEND_URL` points to the correct URL of your running FastAPI backend.

### 4. Connect to the Backend
The frontend communicates with a FastAPI backend. You must have the `type-scribe-ai` backend running for this frontend to function correctly. Please refer to the backend's `README.md` for instructions on how to set it up and run it.

### 5. Run the Development Server
Once the dependencies are installed and the `.env.local` is configured, start the development server:

Using npm:

```bash
npm run dev
```
Using yarn:

```bash
yarn dev
```
Using pnpm:

```bash
pnpm dev
```
Using bun:

```bash
bun dev
```
Open `http://localhost:3000` in your web browser to see the application.

## Project Structure

`src/app/`: Contains the main Next.js pages and root layout (HomePage in `page.tsx`).

`src/components/`: Reusable React components such as `SdkGeneratorForm`, `GeneratedSdkDisplay`, and `LoadingIndicator`.

`src/lib/`: Utility functions and API interaction logic (`api.ts`).

`public/`: Static assets.

`styles/`: Global CSS and Tailwind CSS configuration.


## Scripts Available
In the project directory, you can run:

*   `npm run dev` (or `yarn dev`, `pnpm dev`, `bun dev`): Runs the application in development mode.
*   `npm run build` (or `yarn build`, `pnpm build`, `bun build`): Builds the application for production.
*   `npm run start` (or `yarn start`, `pnpm start`, `bun start`): Starts the production server (after building).
*   `npm run lint` (or `yarn lint`, `pnpm lint`, `bun lint`): Runs ESLint to check for code quality issues.
