# pocky
A lightweight, web-scale agent that helps you find, filter, and fetch real-world PoC exploits — so you don't have to.

## Features

- Automatically searches multiple security-related websites
- Intelligently analyzes and extracts PoC code
- Automatically selects the most reliable PoC samples
- Supports collection of PoCs from multiple sources

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd pocky
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file and add the following content:
```
EXA_API_KEY=your_exa_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_api_base_url
NVD_API_KEY=your_NVD_api_key
```

## Usage

```bash
python pocky.py CVE-2023-4450
```

## Dependencies

- agno: For building intelligent agents
- exa-py: For advanced web searching
- python-dotenv: Environment variable management
- requests: HTTP requests
- flask: for WebUI

## PoCky Web UI

To start the web UI, run:

```bash
python pocky-webui.py
```

The server will start at http://127.0.0.1:5000.

## Notes

- Please ensure you have a valid Exa API key
- Some websites may require additional authentication to access
- It is recommended to perform a security assessment before using any PoC