from utils.config import config

groq_client = config.groq_client

def groq_chat(query: str):
    if not query:
        return {"error": "Query parameter is required"}
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{"role": "system", "content": "You are an AI investment assistant. You are here to help users with investment-related questions."},
                      {"role": "user", "content": query}]
        )
        
        answer = response.choices[0].message.content
        return {"question": query, "answer": answer}
    
    except Exception as e:
        return {"error": str(e)}