import os
import groq

class Config:
    def __init__(self):
        self.required_vars = {
            "GROQ_API_KEY": "GROQ API key",
            "GEMINI_API_KEY": "GEMINI API key", 
            "EXA_API_KEY": "EXA API key",
            "REDIS_URL": "REDIS URL",
            "NEWS_API_KEY": "NEWS API key"
        }
        
        self._load_env_vars()
        self._validate_vars()
        
        # Initialize clients after validation
        self.groq_client = groq.Client(api_key=self.GROQ_API_KEY)
    
    def _load_env_vars(self):
        """Load environment variables into class attributes"""
        for var_name in self.required_vars:
            setattr(self, var_name, os.getenv(var_name))
    
    def _validate_vars(self):
        """Validate that all required environment variables are present"""
        missing_vars = []
        for var_name, description in self.required_vars.items():
            if not getattr(self, var_name):
                missing_vars.append(f"{description} ({var_name})")
        
        if missing_vars:
            error_msg = "Missing required environment variables:\n" + "\n".join(f"- {var}" for var in missing_vars)
            raise ValueError(error_msg)

# Initialize config
config = Config()
