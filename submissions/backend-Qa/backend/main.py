from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from agents.agent_router import AgentRouter
import uvicorn
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import asyncio
from concurrent.futures import TimeoutError
import os
import traceback
import shutil
import re
from utils.file_processor import extract_text_from_file

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Request models
class GenerateRequest(BaseModel):
    requirement: str
    agentType: str
    featureName: Optional[str] = None
    testName: Optional[str] = None
    language: Optional[str] = None
    iterations: Optional[int] = 2
    chunkInput: Optional[bool] = False
    chunkSize: Optional[int] = 4000  # Default chunk size in characters

# Initialize agent router
agent_router = AgentRouter()

def chunk_text_by_sections(text: str, max_chunk_size: int = 4000) -> List[str]:
    """Split text into chunks by sections or headers"""
    # Try to split by common section headers in requirements docs
    section_patterns = [
        r'#+\s+[\w\s]+',  # Markdown headers (# Header, ## Subheader)
        r'\d+\.\s+[\w\s]+',  # Numbered sections (1. Section)
        r'[A-Z][\w\s]+:',  # Title case sections with colon (Requirements:)
        r'\*\*[\w\s]+\*\*',  # Bold sections (**Section**)
        r'\n\n'  # Double newlines as fallback
    ]
    
    # If text is small enough, return as is
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    for pattern in section_patterns:
        # Try to split by current pattern
        if re.search(pattern, text):
            sections = re.split(f'({pattern})', text)
            current_chunk = ""
            
            # Reconstruct sections with their headers
            i = 0
            while i < len(sections):
                section_text = sections[i]
                
                # If this is a header pattern match
                if i + 1 < len(sections) and re.match(pattern, sections[i+1]):
                    header = sections[i+1]
                    i += 2  # Skip the header in next iteration
                    
                    # If adding this section would exceed chunk size, save current chunk and start new one
                    if len(current_chunk) + len(section_text) + len(header) > max_chunk_size:
                        if current_chunk:  # Only add if not empty
                            chunks.append(current_chunk)
                        current_chunk = header + section_text
                    else:
                        current_chunk += section_text + header
                else:
                    # If adding this section would exceed chunk size, save current chunk and start new one
                    if len(current_chunk) + len(section_text) > max_chunk_size:
                        if current_chunk:  # Only add if not empty
                            chunks.append(current_chunk)
                        
                        # If the section itself is too large, split it further
                        if len(section_text) > max_chunk_size:
                            # Simple character-based chunking as fallback
                            for j in range(0, len(section_text), max_chunk_size):
                                chunks.append(section_text[j:j+max_chunk_size])
                            current_chunk = ""
                        else:
                            current_chunk = section_text
                    else:
                        current_chunk += section_text
                    
                    i += 1
            
            # Add the last chunk if not empty
            if current_chunk:
                chunks.append(current_chunk)
                
            # If we successfully chunked the text, return the chunks
            if chunks:
                return chunks
    
    # Fallback: simple character-based chunking
    return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        print(f"Received request: {request}")
        request_data = request.dict()
        
        # Check if input should be chunked
        should_chunk = request_data.get('chunkInput', False)
        chunk_size = request_data.get('chunkSize', 4000)
        requirement = request_data.get('requirement', '')
        
        # If chunking is enabled and requirement is large, process in chunks
        if should_chunk and len(requirement) > chunk_size:
            print(f"Chunking large input ({len(requirement)} chars) into sections")
            chunks = chunk_text_by_sections(requirement, chunk_size)
            print(f"Split into {len(chunks)} chunks")
            
            # Process each chunk and aggregate results
            all_content = []
            token_debug_info = {
                'chunks': [],
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'any_input_truncated': False,
                'any_output_truncated': False
            }
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                
                # Create a copy of the request data with just this chunk
                chunk_request = request_data.copy()
                chunk_request['requirement'] = chunk
                
                # Add chunk info to the request
                chunk_request['chunkInfo'] = {
                    'isChunk': True,
                    'chunkNumber': i+1,
                    'totalChunks': len(chunks)
                }
                
                try:
                    # Call the appropriate agent with timeout for this chunk
                    chunk_response = await asyncio.wait_for(
                        asyncio.to_thread(agent_router.route_request, chunk_request),
                        timeout=60.0
                    )
                    
                    # Skip failed chunks but continue processing
                    if chunk_response.get('status') != 'success':
                        print(f"Chunk {i+1} processing failed: {chunk_response.get('message')}")
                        continue
                    
                    # Collect content from this chunk
                    chunk_content = chunk_response.get('content', '')
                    all_content.append(chunk_content)
                    
                    # Collect token debug info if available
                    if 'token_debug' in chunk_response:
                        token_debug = chunk_response['token_debug']
                        token_debug_info['chunks'].append({
                            'chunk': i+1,
                            'input_tokens': token_debug.get('input_tokens', 0),
                            'output_tokens': token_debug.get('output_tokens', 0),
                            'input_truncated': token_debug.get('input_truncated', False),
                            'output_truncated': token_debug.get('output_truncated', False)
                        })
                        
                        # Update aggregated stats
                        token_debug_info['total_input_tokens'] += token_debug.get('input_tokens', 0)
                        token_debug_info['total_output_tokens'] += token_debug.get('output_tokens', 0)
                        token_debug_info['any_input_truncated'] = token_debug_info['any_input_truncated'] or token_debug.get('input_truncated', False)
                        token_debug_info['any_output_truncated'] = token_debug_info['any_output_truncated'] or token_debug.get('output_truncated', False)
                        
                except TimeoutError:
                    print(f"Chunk {i+1} processing timed out")
                    continue
                except Exception as e:
                    print(f"Error processing chunk {i+1}: {str(e)}")
                    continue
            
            # If no chunks were processed successfully
            if not all_content:
                return JSONResponse(
                    status_code=500,
                    content={
                        'status': 'error',
                        'message': 'Failed to process any chunks of the input'
                    }
                )
            
            # Combine all content
            combined_content = "\n\n".join(all_content)
            
            # Save the combined content to a file
            feature_name = request_data.get('featureName')
            if not feature_name:
                feature_name = f"feature_{int(time.time())}.feature"
            elif not feature_name.endswith('.feature'):
                feature_name += '.feature'
                
            os.makedirs('features', exist_ok=True)
            feature_file = os.path.join('features', feature_name)
            with open(feature_file, 'w') as f:
                f.write(combined_content)
            
            # Return combined results
            return JSONResponse(
                status_code=200,
                content={
                    'status': 'success',
                    'content': combined_content,
                    'feature_file': feature_file,
                    'filename': feature_name,
                    'message': f'Generated from {len(chunks)} chunks of input',
                    'token_debug': token_debug_info
                }
            )
        
        # Process normally if not chunking
        try:
            # Call the appropriate agent with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(agent_router.route_request, request_data),
                timeout=60.0
            )
        except TimeoutError:
            return JSONResponse(
                status_code=408,
                content={
                    'status': 'error',
                    'message': 'Taking too long to generate. Please try with a simpler request or fewer scenarios.'
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    'status': 'error',
                    'message': f'Unexpected error: {str(e)}'
                }
            )

        # Handle error from agent
        if response.get('status') == 'error':
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'error',
                    'message': response.get('message', 'Agent returned an error')
                }
            )

        # Handle successful response
        content = response.get('content', '')
        filename = response.get('filename', '')
        feature_file = response.get('feature_file', '')
        message = response.get('message', 'Generated successfully')

        # Always return a JSON response with content
        response_data = {
            'status': 'success',
            'content': content,
            'message': message
        }
        
        # Add filename if a feature file was created
        if feature_file and os.path.exists(feature_file) and filename:
            response_data['filename'] = filename
            
        # Add token debug info if available
        if 'token_debug' in response:
            response_data['token_debug'] = response['token_debug']
            
        return JSONResponse(
            status_code=200,
            content=response_data
        )

    except Exception as e:
        print(f"Exception in generate endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    return {"message": "QA Test Generation API is running 🚀"}

@app.post("/generate-with-file")
async def generate_with_file(
    file: UploadFile = File(...),
    agentType: str = Form(...),
    requirement: Optional[str] = Form(None),
    featureName: Optional[str] = Form(None),
    testName: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    iterations: Optional[int] = Form(2),
    chunkInput: Optional[bool] = Form(True),  # Default to True for file uploads
    chunkSize: Optional[int] = Form(4000)    # Default chunk size
):
    try:
        print(f"Received file upload: {file.filename}")
        
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from the file
        try:
            file_text = extract_text_from_file(file_path)
            if not file_text:
                return JSONResponse(
                    status_code=400,
                    content={
                        'status': 'error',
                        'message': f'Could not extract text from file: {file.filename}. Please check the file format.'
                    }
                )
                
            print(f"Extracted {len(file_text)} characters from file")
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    'status': 'error',
                    'message': f'Error extracting text from file: {str(e)}'
                }
            )
            
        # Combine file text with any additional requirement text
        combined_requirement = ""
        if requirement:
            combined_requirement = f"{requirement}\n\nFile Content:\n{file_text}"
        else:
            # If no additional requirement, just use the file content as the requirement
            combined_requirement = f"GENERATE GHERKIN FEATURE FILE BASED ON THESE USER STORIES:\n{cleaned_text}"
        
        # Prepare request data
        request_data = {
            "requirement": combined_requirement,
            "agentType": agentType,
            "featureName": featureName,
            "testName": testName,
            "language": language,
            "iterations": iterations,
            "chunkInput": chunkInput,
            "chunkSize": chunkSize
        }
        
        # Use the same generate endpoint logic to handle chunking
        generate_request = GenerateRequest(**request_data)
        return await generate(generate_request)

    except Exception as e:
        print(f"Exception in generate_with_file endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/download/{filename}")
async def download_file(filename: str):
    # Check in features directory first
    features_dir = os.path.join(os.path.dirname(__file__), 'features')
    file_path = os.path.join(features_dir, filename)
    
    # If not found in features, check in test_cases directory
    if not os.path.exists(file_path):
        test_cases_dir = os.path.join(os.path.dirname(__file__), 'test_cases')
        test_cases_path = os.path.join(test_cases_dir, filename)
        
        if os.path.exists(test_cases_path):
            file_path = test_cases_path
        else:
            # Check if file exists in current directory (fallback)
            current_dir_path = os.path.join(os.path.dirname(__file__), filename)
            if os.path.exists(current_dir_path):
                file_path = current_dir_path
            else:
                raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    # Determine media type based on file extension
    media_type = 'text/plain'
    if filename.endswith('.csv'):
        media_type = 'text/csv'
    elif filename.endswith('.feature'):
        media_type = 'text/plain'
    elif filename.endswith('.py'):
        media_type = 'text/x-python'
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
