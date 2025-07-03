# For Judges and Testers

> **Important**: You must start the server first before setting up the Chrome extension!

### Step 1: Start the Superwizard Server

1. Clone the repository:
   ```bash
   git clone https://github.com/amirulhamizan12/superwizard-demo.git
   cd superwizard-demo
   ```

2. Navigate to the server directory and start the server:
   ```bash
   cd server
   ./setup.sh
   ```

3. Configure the OpenRouter API key in the `.env` file:
   ```bash
   # Open the .env file and add the provided API key
   nano .env
   ```
   
   **For Judges**: Use this provided API key:
   ```
   OPENROUTER_API_KEY=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
   ```

4. Start the server:
   ```bash
   ./start.sh
   ```

   The server will be running on `http://localhost:7777`. For detailed server setup instructions, see [server/README.md](server/README.md).

### Step 2: Build and Install the Chrome Extension

5. Return to the project root and install dependencies:
   ```bash
   cd ..  # Go back to project root
   yarn install
   ```

6. Build the extension:
   ```bash
   yarn build
   ```

7. Load the extension in Chrome:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `build` folder from the project directory

8. Configure Extension API Keys (Optional):
   - If you want to use additional features, get your API keys from:
     - OpenAI: https://platform.openai.com/account/api-keys
   - Click the extension icon and open settings to add your API keys
   - **Note**: The server API key is already configured in Step 3

## Development Setup

### For Development Work:

1. **First, start the Superwizard server** (see Step 1 above)

2. **Then start the Chrome extension development server**:
   ```bash
   yarn start
   ```

3. The extension will auto-reload as you make changes to the code

> **Note**: The server must be running for the extension to function properly. Keep both the server (`http://localhost:7777`) and the extension development server running during development.

## 🎮 Usage

1. Press `Cmd+K` (Mac) or `Ctrl+K` (Windows) to open the Superwizard side panel
2. Type your natural language command
3. Watch as Superwizard executes the actions automatically
