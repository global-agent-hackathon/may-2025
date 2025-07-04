# Backend
The backend of the app is entirely written with `FastAPI`. 

This app is splitted into following sections : 
1. Agents - `Agno` agents implementation for writing, quering, summarizing and categorizing mails
2. Auth - Authenticating the user via Google OAuth
3. Core - Settings, Security and Memory tools are implemented
4. Database - Supabase database to store and retreive mails 
5. Mails - To sync the gmails and to send the mails to users via `MailTrap`

## Setup
This project is created with `uv` package manager. With a single command, packages are ready to be executed
```bash
uv sync
```
### Packages
| Package Name | Description | 
| --- | --- |
| Agno | To build the AI Agents | 
| Fast API | Web framework for building APIs | 
| Cryptography | For encrypting and decrypting the mails from the database |
| Google API | To read the Gmail | 
| Google OAuth | To authenticate the user |
| Groq | To inference the Agent's LLM|
| HTTPX | HTTP client library |
| Python Dot Env | To load the environmental variables from `.env` file|
| SQL Model | To interact with Postgres in Supabase |
| Uvicorn | ASGI web server for python |
| Weaviate | Vector Database for AI Agents |