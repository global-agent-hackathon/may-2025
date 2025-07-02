import os
from functools import lru_cache
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoConnectionDetails(BaseModel):
    host: str = Field(..., description="Host name for the database")
    user: str = Field(..., description="Username to use for connecting")
    password: str = Field(..., description="Password to connect to the db")
    port: int = Field(..., description="Database port to use")
    dbname: str = Field(..., description="Database name")

    def get_connection_string(self):
        return f"mongodb+srv://{self.user}:{self.password}@{self.host}/"

    def __str__(self):
        return self.get_connection_string()


class StorageConfig(BaseModel):
    cloud_name: str = Field(..., description="Cloudinary cloud name")
    api_key: str = Field(..., description="Cloudinary API key")
    api_secret: str = Field(..., description="Cloudinary API secret")


class LLMConfig(BaseModel):
    api_key: str = Field(..., description="API key for the LLM service")
    api_base: str = Field(..., description="Base URL for the LLM service")
    api_version: str = Field(..., description="API version for the LLM service")
    llm_deployment_name: str = Field(
        ..., description="LLM deployment name for the LLM service"
    )


class VectorStoreConfig(BaseModel):
    mongo_collection: str = Field(..., description="MongoDB collection name")
    embedding_model: str = Field(..., description="Embedding model to use")
    base_url: str = Field(..., description="Base URL for the embedding model")
    api_key: str = Field(..., description="API key for the embedding model")


class SonarConfig(BaseModel):
    base_url: str = Field(..., description="Perplexity base URL")
    api_key: str = Field(..., description="Sonar API Key")


class JWTConfig(BaseModel):
    secret_key: str = Field(..., description="Secret key for JWT")
    algorithm: str = Field(..., description="Algorithm for JWT")
    expire_after: int = Field(..., description="Validity for the JWT token in minutes")


class NetlifyConfig(BaseModel):
    site_id: str = Field(..., description="Netlify site ID")
    auth_token: str = Field(..., description="Netlify personal access token")


class AppSettings(BaseSettings):
    db_config: MongoConnectionDetails = Field(
        ..., description="MongoDB connection details"
    )
    llm_config: LLMConfig = Field(..., description="LLM configuration details")
    sonar_config: SonarConfig = Field(..., description="Sonar configuration details")
    jwt_config: JWTConfig = Field(..., description="JWT configuration details")
    storage_config: StorageConfig = Field(
        ..., description="Storage configuration details"
    )
    vector_store_config: VectorStoreConfig = Field(
        ..., description="Vector store configuration details"
    )
    netlify_config: NetlifyConfig = Field(
        ..., description="Netlify deployment configuration"
    )
    local_user_email: Optional[str] = Field(None, description="Local user mail id")
    local: bool = Field(False, description="Local mode")
    mcp_url: str = Field(..., description="MCP server URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        yaml_file="config.yaml",
        extra="ignore",
    )

    @classmethod
    def get_from_config(cls, config_path: str = "../config.yaml"):
        with open(config_path) as file:
            yaml_data = yaml.safe_load(file)
            return cls(**yaml_data)

    @classmethod
    def get_from_env(cls):
        return cls(
            db_config=MongoConnectionDetails(
                host=os.environ.get("DB__HOST"),
                dbname=os.environ.get("DB__DBNAME"),
                port=os.environ.get("DB__PORT"),
                user=os.environ.get("DB__USER"),
                password=os.environ.get("DB__PASSWORD"),
            ),
            llm_config=LLMConfig(
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                api_base=os.environ.get("AZURE_OPENAI_API_BASE"),
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
                llm_deployment_name=os.environ.get("OPENAI_LLM_DEPLOYMENT_NAME"),
            ),
            sonar_config=SonarConfig(
                base_url=os.environ.get("SONAR_BASE_URL"),
                api_key=os.environ.get("SONAR_API_KEY"),
            ),
            storage_config=StorageConfig(
                cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
                api_key=os.environ.get("CLOUDINARY_API_KEY"),
                api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
            ),
            vector_store_config=VectorStoreConfig(
                mongo_collection=os.environ.get("VECTOR_MONGO_COLLECTION"),
                embedding_model=os.environ.get("EMBEDDING_MODEL"),
                base_url=os.environ.get("AZURE_OPENAI_API_BASE"),
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            ),
            jwt_config=JWTConfig(
                secret_key=os.environ.get("JWT_SECRET_KEY"),
                algorithm=os.environ.get("JWT_ALGORITHM"),
                expire_after=os.environ.get("JWT_TOKEN_EXPIRY_MINUTES"),
            ),
            netlify_config=NetlifyConfig(
                site_id=os.environ.get("NETLIFY_SITE_ID"),
                auth_token=os.environ.get("NETLIFY_AUTH_TOKEN"),
            ),
            local_user_email=os.environ.get("LOCAL_USER_EMAIL"),
            local=os.environ.get("LOCAL"),
            mcp_url=os.environ.get("MCP_URL"),
        )


@lru_cache
def get_app_settings():
    return AppSettings.get_from_env()
