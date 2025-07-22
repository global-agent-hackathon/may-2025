from dotenv import load_dotenv
load_dotenv() 

import os
import fitz
import json
import re
import requests
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import numpy as np
from bs4 import BeautifulSoup
import streamlit as st

# model
from agno.models.groq import Groq


SUPABASE_DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
HUGGINGFACEHUB_API_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY") 

# Fixed Supabase connection details
SUPABASE_URL = "https://wasxdjhtnmxyatwbwttj.supabase.co"

# Model setup
llm = Groq(id="llama-3.1-8b-instant")

# Agno imports
from agno.agent import Agent, AgentKnowledge
from agno.embedder.mistral import MistralEmbedder

from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.document.base import Document
from agno.vectordb.pgvector import PgVector, SearchType
from agno.document.chunking.agentic import AgenticChunking
from agno.document.chunking.document import DocumentChunking
from agno.tools import Toolkit

from supabase import create_client
import streamlit as st

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# Initialize components
embeddings = MistralEmbedder()

class DatabaseManager:
    """Manages database operations for storing conversations and knowledge"""
    
    def __init__(self, SUPABASE_URL: str, SUPABASE_KEY: str):
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY
        self.supabase = None
        self.connected = False
        self._init_connection()
    
    def _init_connection(self):
        """Initialize Supabase connection with error handling"""
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            # Test connection
            self.supabase.table('conversations').select('id').limit(1).execute()
            self.connected = True
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            self.connected = False
            self.supabase = None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected and self.supabase is not None
    
    def save_conversation(self, session_id: str, query: str, response: str, context: str = None):
        """Save conversation to database"""
        if not self.is_connected():
            return None
            
        try:
            conversation_data = {
                'session_id': session_id,
                'query': query,
                'response': response,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            result = self.supabase.table('conversations').insert(conversation_data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
            return None
    
    def get_conversation_history(self, session_id: str, limit: int = 10):
        """Retrieve conversation history from database"""
        if not self.is_connected():
            return []
            
        try:
            result = self.supabase.table('conversations')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def save_document_metadata(self, filepath: str, document_type: str, chunk_count: int):
        """Save document metadata to database"""
        if not self.is_connected():
            return None
            
        try:
            doc_data = {
                'filepath': filepath,
                'document_type': document_type,
                'chunk_count': chunk_count,
                'processed_at': datetime.now().isoformat()
            }
            result = self.supabase.table('document_metadata').insert(doc_data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Error saving document metadata: {str(e)}")
            return None
    
    def get_processed_documents(self):
        """Get list of processed documents"""
        if not self.is_connected():
            return []
            
        try:
            result = self.supabase.table('document_metadata')\
                .select('*')\
                .order('processed_at', desc=True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            return []

class WebSearchTool:
    """Advanced web search tool with multiple search engines and content extraction"""
    name = "web_search"
    description = "Searches the web for current information and extracts relevant content"

    def __init__(self):
        self.serpapi_key = os.environ.get("SERPAPI_KEY")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def run(self, input: Dict) -> str:
        """Perform web search and return formatted results"""
        query = input.get("query", "")
        max_results = input.get("max_results", 5)
        search_type = input.get("search_type", "general")  # general, news, academic
        
        if not query:
            return "Error: No search query provided"
        
        try:
            # Try SerpAPI first if available
            if self.serpapi_key:
                results = self._search_with_serpapi(query, max_results, search_type)
            else:
                # Fallback to DuckDuckGo search
                results = self._search_with_duckduckgo(query, max_results)
            
            if not results:
                return f"No web results found for query: {query}"
            
            # Extract and clean content from top results
            formatted_results = self._format_search_results(results, query)
            return formatted_results
            
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    def _search_with_serpapi(self, query: str, max_results: int, search_type: str) -> List[Dict]:
        """Search using SerpAPI (Google Search)"""
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.serpapi_key,
                "num": min(max_results, 10)
            }
            
            # Adjust search parameters based on type
            if search_type == "news":
                params["tbm"] = "nws"
            elif search_type == "academic":
                params["q"] = f"site:scholar.google.com OR site:arxiv.org OR site:researchgate.net {query}"
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()
            
            results = []
            organic_results = data.get("organic_results", [])
            
            for result in organic_results[:max_results]:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "source": "Google"
                })
            
            return results
            
        except Exception as e:
            print(f"SerpAPI search failed: {e}")
            return []
    
    def _search_with_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Fallback search using DuckDuckGo"""
        try:
            # DuckDuckGo instant answer API
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get("https://api.duckduckgo.com/", params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Get abstract if available
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "link": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                    "source": "DuckDuckGo"
                })
            
            # Get related topics
            for topic in data.get("RelatedTopics", [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("Text", "")[:100] + "...",
                        "link": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "DuckDuckGo"
                    })
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return []
    
    def _extract_webpage_content(self, url: str) -> str:
        """Extract clean text content from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            return text[:2000] if len(text) > 2000 else text
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return ""
    
    def _format_search_results(self, results: List[Dict], query: str) -> str:
        """Format search results for AI consumption"""
        if not results:
            return "No web search results available."
        
        formatted = f"Web search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "Untitled")
            snippet = result.get("snippet", "No description available")
            link = result.get("link", "")
            source = result.get("source", "Web")
            
            formatted += f"[{i}] {title}\n"
            formatted += f"Source: {source}\n"
            formatted += f"Summary: {snippet}\n"
            if link:
                formatted += f"URL: {link}\n"
            
            # Try to extract more content if URL is available
            if link and i <= 3:  # Only extract from top 3 results
                content = self._extract_webpage_content(link)
                if content:
                    formatted += f"Content Preview: {content[:500]}...\n"
            
            formatted += "\n---\n\n"
        
        return formatted

class ResponseFormatter:
    """Formats AI responses for better readability"""
    
    @staticmethod
    def clean_response(text: str) -> str:
        """Clean response text by removing excessive formatting"""
        if not text:
            return ""
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove markdown headers but keep the content
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove markdown bold/italic but keep content
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # Remove markdown code blocks but keep content
        text = re.sub(r'```[^\n]*\n', '', text)
        text = re.sub(r'```', '', text)
        
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Clean up bullet points
        text = re.sub(r'^[-*•]\s*', '• ', text, flags=re.MULTILINE)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Clean up line breaks
        text = text.strip()
        
        return text
    
    @staticmethod
    def format_context(context: str) -> str:
        """Format context for better display"""
        if not context:
            return ""
        
        # Remove separator lines
        context = re.sub(r'={20,}', '', context)
        
        # Clean up context markers
        context = re.sub(r'\[Context \d+\]', '', context)
        
        # Format source information
        context = re.sub(r'Source: ([^\n]+)', r'📄 Source: \1', context)
        
        # Clean up relevance scores
        context = re.sub(r'Relevance: [\d.]+', '', context)
        
        return ResponseFormatter.clean_response(context)

class DocumentProcessor:
    """Enhanced document processing with multiple format support"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md', '.docx']
        self.chunker = AgenticChunking()
    
    def process_file(self, filepath: str) -> List[Document]:
        """Process different file types and return document chunks"""
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if file_path.suffix.lower() == '.pdf':
            return self._process_pdf(filepath)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            return self._process_text(filepath)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _process_pdf(self, filepath: str) -> List[Document]:
        """Process PDF files"""
        try:
            doc = fitz.open(filepath)
            full_text = ""
            
            for page in doc:
                full_text += page.get_text() + "\n"
            
            doc.close()
            
            # Create document
            document = Document(content=full_text)
            # Add metadata safely
            metadata = {"source": filepath, "type": "pdf"}
            if hasattr(document, 'metadata'):
                document.metadata = metadata
            elif hasattr(document, 'meta'):
                document.meta = metadata
            
            chunks = self.chunker.chunk(document)
            
            # Add metadata to chunks
            for chunk in chunks:
                if hasattr(chunk, 'metadata'):
                    chunk.metadata = metadata
                elif hasattr(chunk, 'meta'):
                    chunk.meta = metadata
            
            return chunks
        except Exception as e:
            raise Exception(f"Error processing PDF {filepath}: {str(e)}")
    
    def _process_text(self, filepath: str) -> List[Document]:
        """Process text files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document
            document = Document(content=content)
            metadata = {"source": filepath, "type": "text"}
            if hasattr(document, 'metadata'):
                document.metadata = metadata
            elif hasattr(document, 'meta'):
                document.meta = metadata
            
            chunks = self.chunker.chunk(document)
            
            # Add metadata to chunks
            for chunk in chunks:
                if hasattr(chunk, 'metadata'):
                    chunk.metadata = metadata
                elif hasattr(chunk, 'meta'):
                    chunk.meta = metadata
            
            return chunks
        except Exception as e:
            raise Exception(f"Error processing text file {filepath}: {str(e)}")

class MemoryGraph:
    """Simple in-memory knowledge graph for relationships"""
    
    def __init__(self):
        self.entities = {}
        self.relationships = []
    
    def add_entity(self, entity_id: str, entity_type: str, properties: Dict):
        """Add an entity to the knowledge graph"""
        self.entities[entity_id] = {
            "type": entity_type,
            "properties": properties,
            "created_at": datetime.now().isoformat()
        }
    
    def add_relationship(self, source: str, target: str, relation_type: str, properties: Dict = None):
        """Add a relationship between entities"""
        self.relationships.append({
            "source": source,
            "target": target,
            "type": relation_type,
            "properties": properties or {},
            "created_at": datetime.now().isoformat()
        })
    
    def get_related_entities(self, entity_id: str) -> List[Dict]:
        """Get entities related to a given entity"""
        related = []
        for rel in self.relationships:
            if rel["source"] == entity_id:
                if rel["target"] in self.entities:
                    related.append({
                        "entity": self.entities[rel["target"]],
                        "relationship": rel["type"],
                        "entity_id": rel["target"]
                    })
            elif rel["target"] == entity_id:
                if rel["source"] in self.entities:
                    related.append({
                        "entity": self.entities[rel["source"]],
                        "relationship": rel["type"],
                        "entity_id": rel["source"]
                    })
        return related

class InMemoryDocumentStore:
    """In-memory document storage with similarity search"""
    
    def __init__(self):
        self.documents = {}  # filepath -> list of chunks
        self.embeddings_cache = {}  # chunk_id -> embedding
        
    def store_document(self, filepath: str, chunks: List[Document], embeddings_list: List[List[float]] = None):
        """Store document chunks and their embeddings"""
        self.documents[filepath] = chunks
        
        if embeddings_list:
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                chunk_id = f"{filepath}_{i}"
                self.embeddings_cache[chunk_id] = embedding
    
    def search_similar(self, query_embedding: List[float], max_results: int = 5) -> List[Dict]:
        """Search for similar content using cosine similarity"""
        results = []
        
        for filepath, chunks in self.documents.items():
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filepath}_{i}"
                if chunk_id in self.embeddings_cache:
                    similarity = self._cosine_similarity(query_embedding, self.embeddings_cache[chunk_id])
                    
                    # Get metadata
                    metadata = {}
                    if hasattr(chunk, 'metadata') and chunk.metadata:
                        metadata = chunk.metadata
                    elif hasattr(chunk, 'meta') and chunk.meta:
                        metadata = chunk.meta
                    
                    results.append({
                        'content': chunk.content,
                        'similarity': similarity,
                        'source': filepath,
                        'metadata': metadata,
                        'chunk_id': chunk_id
                    })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

class DocumentEmbedder:
    """Document embedding tool that works with or without database"""
    name = "embed_documents"
    description = "Embeds documents for semantic search"

    def __init__(self, memory_graph: MemoryGraph, db_manager: DatabaseManager = None):
        self.processor = DocumentProcessor()
        self.memory_graph = memory_graph
        self.db_manager = db_manager
        self.document_store = InMemoryDocumentStore()
        self.vector_db = None
        
        # Try to initialize vector database if possible
        if db_manager and db_manager.is_connected():
            self._init_vector_db()

    def _init_vector_db(self):
        """Initialize vector database connection"""
        try:
            # Get database credentials from environment
            db_password = os.environ.get("SUPABASE_DB_PASSWORD")
            if not db_password:
                print("⚠️  SUPABASE_DB_PASSWORD not set, using in-memory storage only")
                return
            
            # Extract the project reference from SUPABASE_URL
            # Format: https://PROJECT_ID.supabase.co
            project_id = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
            
            # URL encode the password to handle special characters
            from urllib.parse import quote_plus
            encoded_password = quote_plus(db_password)
            
            # Construct the correct PostgreSQL connection URL
            # Format: postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
            postgres_url = f"postgresql://postgres:{encoded_password}@db.{project_id}.supabase.co:5432/postgres"
            
            print(f"🔗 Connecting to: postgresql://postgres:***@db.{project_id}.supabase.co:5432/postgres")
            
            self.vector_db = PgVector(
                table_name="memorypal_documents",
                db_url=postgres_url,
                embedder=embeddings,
                search_type=SearchType.hybrid
            )
            print("✅ Vector database initialized")
        except Exception as e:
            print(f"❌ Vector database initialization failed: {str(e)}")
            print(f"🔍 Check your SUPABASE_DB_PASSWORD environment variable")
            self.vector_db = None

    def run(self, input: Dict) -> str:
        """Process and embed documents - FIXED: Added missing run method"""
        filepath = input.get("path") or input.get("filepath")
        document_type = input.get("document_type", "general")
        
        if not filepath:
            return "Error: No file path provided"
        
        try:
            chunks = self.processor.process_file(filepath)
            
            # Generate embeddings
            embeddings_list = []
            for chunk in chunks:
                try:
                    # Get embedding for the chunk content
                    embedding = embeddings.get_embedding([chunk.content])[0]
                    # Convert to list if it's a numpy array
                    if hasattr(embedding, 'tolist'):
                        embedding = embedding.tolist()
                    embeddings_list.append(embedding)
                except Exception as e:
                    print(f"Error generating embedding for chunk: {e}")
                    embeddings_list.append(None)
            
            # Store in memory
            valid_embeddings = [emb for emb in embeddings_list if emb is not None]
            if valid_embeddings:
                self.document_store.store_document(filepath, chunks, valid_embeddings)
            
            # Try to store in vector database if available
            db_success = False
            if self.vector_db:
                try:
                    # Add metadata to chunks before inserting
                    for i, chunk in enumerate(chunks):
                        metadata = {
                            "document_type": document_type,
                            "chunk_id": f"{filepath}_{i}",
                            "timestamp": datetime.now().isoformat(),
                            "word_count": len(chunk.content.split()),
                            "source": filepath
                        }
                        
                        # Set metadata based on chunk's attribute structure
                        if hasattr(chunk, 'metadata'):
                            if chunk.metadata is None:
                                chunk.metadata = {}
                            chunk.metadata.update(metadata)
                        elif hasattr(chunk, 'meta'):
                            if chunk.meta is None:
                                chunk.meta = {}
                            chunk.meta.update(metadata)
                        else:
                            # Create metadata attribute if it doesn't exist
                            chunk.metadata = metadata
                    
                    self.vector_db.insert(chunks)
                    db_success = True
                    print("✅ Documents stored in vector database")
                except Exception as e:
                    print(f"❌ Error storing in vector database: {e}")
            
            # Update memory graph
            doc_id = f"doc_{Path(filepath).stem}"
            self.memory_graph.add_entity(
                doc_id,
                "document",
                {
                    "filepath": filepath,
                    "document_type": document_type,
                    "chunk_count": len(chunks),
                    "processed_at": datetime.now().isoformat(),
                    "stored_in_db": db_success
                }
            )
            
            # Save metadata to database if available
            if self.db_manager and self.db_manager.is_connected():
                self.db_manager.save_document_metadata(filepath, document_type, len(chunks))
            
            storage_info = "vector database and memory" if db_success else "memory only"
            return f"Successfully embedded {len(chunks)} chunks from {Path(filepath).name} (stored in {storage_info})"
            
        except Exception as e:
            return f"Error processing {Path(filepath).name}: {str(e)}"

    def process_document(self, filepath: str, document_type: str = "general") -> str:
        """Alternative method name for backward compatibility"""
        return self.run({"path": filepath, "document_type": document_type})

class HybridRetriever:
    """Enhanced retriever that combines document search with web search"""
    name = "hybrid_search"
    description = "Searches both documents and web to provide comprehensive information"

    def __init__(self, memory_graph: MemoryGraph, document_embedder: DocumentEmbedder, web_search: WebSearchTool):
        self.memory_graph = memory_graph
        self.document_embedder = document_embedder
        self.web_search = web_search

    def run(self, input: Dict) -> str:
        """Retrieve relevant context from both documents and web"""
        query = input["query"]
        max_doc_results = input.get("max_doc_results", 3)
        max_web_results = input.get("max_web_results", 3)
        search_web = input.get("search_web", True)
        
        results = []
        
        # 1. Search documents first
        doc_context = self._search_documents(query, max_doc_results)
        if doc_context:
            results.append(f"📚 DOCUMENT KNOWLEDGE:\n{doc_context}")
        
        # 2. Search web for current information
        if search_web:
            web_context = self._search_web(query, max_web_results)
            if web_context:
                results.append(f"🌐 WEB KNOWLEDGE:\n{web_context}")
        
        if not results:
            return "No relevant information found in documents or web."
        
        # 3. Combine and format results
        combined_context = "\n\n" + "="*50 + "\n\n".join(results)
        
        # 4. Add decision guidance
        decision_prompt = f"""
        
📊 ANALYSIS INSTRUCTION:
Based on the above information from both documents and web sources:
1. Compare and contrast the information from both sources
2. Identify any contradictions or confirmations
3. Determine which source is more current/reliable for this specific query
4. Provide a synthesized answer that leverages the best of both sources
5. Clearly indicate when information comes from documents vs. web sources

Query: {query}
        """
        
        return combined_context + decision_prompt
    
    def _search_documents(self, query: str, max_results: int) -> str:
        """Search document knowledge base"""
        try:
            # Try vector database first
            if self.document_embedder.vector_db:
                try:
                    results = self.document_embedder.vector_db.search(query, limit=max_results)
                    if results:
                        return self._format_doc_results(results, "vector database")
                except Exception as e:
                    print(f"Vector database search failed: {e}")
            
            # Fallback to in-memory search
            try:
                query_embedding = embeddings.get_embedding([query])[0].tolist()
                results = self.document_embedder.document_store.search_similar(query_embedding, max_results)
                if results:
                    return self._format_doc_results(results, "memory search")
            except Exception as e:
                print(f"Memory search failed: {e}")
            
            return ""
            
        except Exception as e:
            print(f"Document search error: {e}")
            return ""
    
    def _search_web(self, query: str, max_results: int) -> str:
        """Search web for current information"""
        try:
            web_results = self.web_search.run({
                "query": query,
                "max_results": max_results,
                "search_type": "general"
            })
            return web_results
        except Exception as e:
            print(f"Web search error: {e}")
            return ""
    
    def _format_doc_results(self, results: List[Dict], search_method: str) -> str:
        """Format document search results"""
        if not results:
            return ""
        
        context_pieces = []
        for i, chunk in enumerate(results, 1):
            source = Path(chunk.get('source', 'Unknown')).name
            content = chunk.get('content', '')
            similarity = chunk.get('similarity', 0)
            
            context_piece = f"[Doc {i}] Source: {source}\n"
            context_piece += f"Content: {content}\n"
            if similarity > 0:
                context_piece += f"Relevance: {similarity:.3f}\n"
            
            context_pieces.append(context_piece)
        
        result = "\n---\n".join(context_pieces)
        print(f"Retrieved {len(results)} document results using {search_method}")
        return result

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.history = []
        self.context_window = 10
        self.db_manager = db_manager
    
    def add_exchange(self, query: str, response: str, context: str = None, session_id: str = None):
        """Add a conversation exchange"""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "context": context
        }
        self.history.append(exchange)
        
        if len(self.history) > self.context_window:
            self.history = self.history[-self.context_window:]
        
        # Save to database if manager is available
        if self.db_manager and self.db_manager.is_connected() and session_id:
            self.db_manager.save_conversation(session_id, query, response, context)
    
    def get_context_string(self, max_exchanges: int = 5) -> str:
        """Get formatted conversation history for context"""
        if not self.history:
            return ""
        
        recent_history = self.history[-max_exchanges:]
        context_parts = []
        
        for exchange in recent_history:
            context_parts.append(f"Human: {exchange['query']}")
            context_parts.append(f"Assistant: {exchange['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    def get_relevant_history(self, current_query: str, max_results: int = 3) -> List[Dict]:
        """Get conversation history relevant to current query"""
        if not self.history:
            return []
        
        # Simple keyword matching for relevance
        query_words = set(current_query.lower().split())
        relevant_exchanges = []
        
        for exchange in self.history:
            exchange_words = set((exchange['query'] + ' ' + exchange['response']).lower().split())
            common_words = query_words.intersection(exchange_words)
            
            if common_words:
                relevance = len(common_words) / len(query_words)
                relevant_exchanges.append({
                    **exchange,
                    'relevance': relevance
                })
        
        # Sort by relevance and return top results
        relevant_exchanges.sort(key=lambda x: x['relevance'], reverse=True)
        return relevant_exchanges[:max_results]

class RAGAgent:
    """Main RAG agent that combines all components"""
    
    def __init__(self):
        # Initialize core components
        self.db_manager = DatabaseManager(SUPABASE_URL, SUPABASE_KEY)
        self.memory_graph = MemoryGraph()
        self.conversation_memory = ConversationMemory(self.db_manager)
        
        # Initialize tools
        self.web_search = WebSearchTool()
        self.document_embedder = DocumentEmbedder(self.memory_graph, self.db_manager)
        self.hybrid_retriever = HybridRetriever(self.memory_graph, self.document_embedder, self.web_search)
        
        # Initialize AI agent
        self.agent = Agent(
            model=llm,
            # tools=[self.document_embedder, self.hybrid_retriever, self.web_search],
            instructions=self._get_agent_instructions(),
            show_tool_calls=False,
            markdown=False
        )
        
        self.formatter = ResponseFormatter()
        
    def _get_agent_instructions(self) -> str:
        """Get comprehensive instructions for the AI agent"""
        return """
        You are MemoryPal, an advanced AI assistant with access to documents, web search, and conversation memory.
        
        CORE CAPABILITIES:
        1. Document Processing: Analyze PDFs, text files, and other documents
        2. Web Search: Access current information from the internet
        3. Memory Management: Remember conversations and build knowledge relationships
        4. Hybrid Retrieval: Combine document knowledge with web information
        
        RESPONSE GUIDELINES:
        1. Always search for relevant information before answering complex questions
        2. Clearly distinguish between document-based and web-based information
        3. Provide source citations for all information
        4. Synthesize information from multiple sources when available
        5. Ask clarifying questions when the query is ambiguous
        6. Be conversational but informative
        
        TOOL USAGE:
        - Use embed_documents to process new documents
        - Use hybrid_search for comprehensive information retrieval
        - Use web_search for current events or when documents lack information
        
        MEMORY INTEGRATION:
        - Remember key facts and relationships from conversations
        - Build connections between different pieces of information
        - Refer to previous conversations when relevant
        
        Always strive to provide accurate, helpful, and well-sourced responses.
        """
    

    def process_document(self, filepath: str, document_type: str = "general") -> str:
        """Process and embed a document - FIXED"""
        try:
            # Use the run method with proper input format
            result = self.document_embedder.run({
                "path": filepath,
                "document_type": document_type
            })
            return result
        except Exception as e:
            return f"Error processing document: {str(e)}"
        
    def chat(self, query: str, session_id: str = "default", use_web: bool = True) -> Dict[str, Any]:
        """Main chat interface"""
        try:
            # Get conversation context
            conversation_context = self.conversation_memory.get_context_string()
            relevant_history = self.conversation_memory.get_relevant_history(query)
            
            # Enhance query with context
            enhanced_query = self._enhance_query_with_context(query, conversation_context, relevant_history)
            
            # Get response from agent
            response = self.agent.run(enhanced_query)
            
            # Clean and format response
            clean_response = self.formatter.clean_response(str(response.content))
            
            # Extract context used
            context_used = ""
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    if hasattr(tool_call, 'result'):
                        context_used += str(tool_call.result) + "\n"
            
            # Save conversation
            self.conversation_memory.add_exchange(query, clean_response, context_used, session_id)
            
            # Update memory graph
            self._update_memory_graph(query, clean_response)
            
            return {
                "response": clean_response,
                "context": self.formatter.format_context(context_used),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "sources_used": self._extract_sources(context_used)
            }
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            return {
                "response": error_msg,
                "context": "",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "sources_used": []
            }
    
    def _enhance_query_with_context(self, query: str, conversation_context: str, relevant_history: List[Dict]) -> str:
        """Enhance query with conversation context"""
        enhanced_parts = [query]
        
        if conversation_context:
            enhanced_parts.append(f"\nRecent conversation context:\n{conversation_context}")
        
        if relevant_history:
            history_context = "\nRelevant previous discussions:\n"
            for item in relevant_history:
                history_context += f"- {item['query'][:100]}...\n"
            enhanced_parts.append(history_context)
        
        return "\n".join(enhanced_parts)
    
    def _update_memory_graph(self, query: str, response: str):
        """Update memory graph with new information"""
        try:
            # Extract entities and relationships (simplified)
            query_id = f"query_{datetime.now().timestamp()}"
            
            self.memory_graph.add_entity(
                query_id,
                "conversation",
                {
                    "query": query,
                    "response": response[:200],  # Truncate for storage
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            print(f"Error updating memory graph: {e}")
    
    def _extract_sources(self, context: str) -> List[str]:
        """Extract source information from context"""
        sources = []
        
        # Extract document sources
        doc_sources = re.findall(r'Source: ([^\n]+)', context)
        sources.extend([f"📄 {source}" for source in doc_sources])
        
        # Extract web sources
        web_sources = re.findall(r'URL: ([^\n]+)', context)
        sources.extend([f"🌐 {source}" for source in web_sources])
        
        return list(set(sources))  # Remove duplicates
    
    def get_processed_documents(self) -> List[Dict]:
        """Get list of processed documents"""
        return self.db_manager.get_processed_documents()
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history"""
        return self.db_manager.get_conversation_history(session_id, limit)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        return {
            "database_connected": self.db_manager.is_connected(),
            "vector_db_available": self.document_embedder.vector_db is not None,
            "web_search_available": self.web_search.serpapi_key is not None,
            "documents_in_memory": len(self.document_embedder.document_store.documents),
            "entities_in_graph": len(self.memory_graph.entities),
            "relationships_in_graph": len(self.memory_graph.relationships),
            "conversation_history_length": len(self.conversation_memory.history)
        }

# Streamlit UI Application
def create_streamlit_app():
    """Create Streamlit interface for the RAG system"""
    
    st.set_page_config(
        page_title="MemoryPal - Advanced RAG Assistant",
        page_icon="🧠",
        layout="wide"
    )
    
    # Initialize session state
    if 'rag_agent' not in st.session_state:
        with st.spinner("Initializing MemoryPal..."):
            st.session_state.rag_agent = RAGAgent()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().timestamp()}"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.title("🧠 MemoryPal")
        st.markdown("Advanced RAG Assistant with Memory")
        
        # System status
        st.subheader("System Status")
        status = st.session_state.rag_agent.get_system_status()
        
        for key, value in status.items():
            if isinstance(value, bool):
                icon = "✅" if value else "❌"
                st.write(f"{icon} {key.replace('_', ' ').title()}")
            else:
                st.write(f"📊 {key.replace('_', ' ').title()}: {value}")
        
        st.divider()
        
        # Document upload
        st.subheader("📄 Document Upload")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'md'],
            help="Upload PDF, text, or markdown files"
        )
        
        document_type = st.selectbox(
            "Document Type",
            ["general", "technical", "research", "legal", "medical"]
        )
        
        if uploaded_file is not None:
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    # Save uploaded file
                    file_path = f"temp_{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process document
                    result = st.session_state.rag_agent.process_document(file_path, document_type)
                    st.success(result)
                    
                    # Clean up
                    os.remove(file_path)
        
        st.divider()
        
        # Processed documents
        st.subheader("📚 Processed Documents")
        docs = st.session_state.rag_agent.get_processed_documents()
        for doc in docs[:5]:  # Show latest 5
            st.write(f"• {Path(doc['filepath']).name}")
    
    # Main chat interface
    st.title("💬 Chat with MemoryPal")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.write(source)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = st.session_state.rag_agent.chat(
                    prompt, 
                    st.session_state.session_id
                )
                
                st.markdown(response_data["response"])
                
                # Show sources if available
                if response_data["sources_used"]:
                    with st.expander("Sources Used"):
                        for source in response_data["sources_used"]:
                            st.write(source)
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["response"],
                    "sources": response_data["sources_used"]
                })

# Main execution
if __name__ == "__main__":
    # Check if running in Streamlit
    try:
        create_streamlit_app()
    except ImportError:
        print("Streamlit not available. Running basic CLI interface...")
        
        # Basic CLI interface
        rag_agent = RAGAgent()
        print("MemoryPal RAG System initialized!")
        print("Type 'quit' to exit, 'status' for system status, or ask any question.")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'status':
                status = rag_agent.get_system_status()
                for key, value in status.items():
                    print(f"{key}: {value}")
            elif user_input:
                response = rag_agent.chat(user_input)
                print(f"\nMemoryPal: {response['response']}")
                
                if response['sources_used']:
                    print("\nSources:")
                    for source in response['sources_used']:
                        print(f"  {source}")
        
        print("Goodbye!")