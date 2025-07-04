# Agents
This app uses `Agno` agents to do the following tasks : 
1. Categorization of emails
2. Summary of emails
3. Answering the user query 
4. Helping the user to write mails

## Setup
For the inference we use, `Groq` and here is the setup steps : 
* Go to the Groq platform and sign in 
* Create the `GROQ_API_KEY` in the dashboard and save it in `.env` file
For the memory part, we will use `Weaviate`:
* Go to the `Weaviate` platform and sign in
* Create a new cluster and fill out the form
* Save the following credentials `WEAVIATE_URL` and `WEAVIATE_API_KEY` in the `.env` file

## Endpoints
| URL | Description |
| --- | --- |
| `/api/agents/query/chat` | Endpoint for quering the agent |
| `/api/agents/writing/draft` | Endpoint for writing the draft mail |
| `/api/agents/summary/daily` | Endpoint for summarizing the draft mail |

Note that categorizing agent doesn't have direct endpoints, as this will be dealt by the `syncing` process of the app. The categorizing agent needs user information to decide the "important" or "archive" and this content is fetched in the `/me/settings/category-instruction` api endpoint of the app which can be found in `backend/users/router.py` file

## Memory 
Memory is the most important part of the agents. For this app, we use `Weaviate` a vector database for storing the mail contents in vector and which helps our agent to retrieve valuable information of the user's mails.

In this app, I implemented the `keyword` based search for retiriving the content, to add the `vector` based search, it needs `vectorizer` from `OPEN AI` or `Hugging Face` API keys. For production these keys will be helpful for large scale storage.