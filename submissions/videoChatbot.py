import os
from pathlib import Path
import streamlit as st
from video_processing_utils import download_video, video_to_images, video_to_audio, audio_to_text
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from read_env import *  

# Configure Azure OpenAI LLM
llm = AzureOpenAI(
    model="gpt-35-turbo-16k",
    deployment_name=AZURE_OPENAI_DEPLOYMENT,
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION,
)
Settings.llm = llm

# Configure Azure OpenAI Embedding Model
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="supplychain-text-embedding-ada-002",
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION,
)
Settings.embed_model = embed_model

def process_video(context_name: str):
     # Set up paths
    output_video_path = "./Youtube videos/"
    output_folder = "./mixed_data/"
    filepath = os.path.join(output_video_path, context_name)
    output_audio_path = os.path.join(output_folder, "output_audio.wav")
    
    # # Ensure output directory exists
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # # --- VIDEO PROCESSING PIPELINE ---

    # Step 1: Convert video to frames (images)
    video_to_images(filepath, output_folder)

    # # Step 2: Convert video to audio
    video_to_audio(filepath, output_audio_path)

    # # Step 3: Convert audio to text using speech-to-text
    text_data = audio_to_text(output_audio_path)

    # Step 4: Save the transcribed text to a file
    transcript_file_path = os.path.join(output_folder, "output_text.txt")
    with open(transcript_file_path, "w") as file:
        file.write(text_data)

    # Step 5: Clean up intermediate audio file
    os.remove(output_audio_path)

    # --- INDEXING AND QUERYING ---

    # Step 6: Load the documents from the folder
    documents = SimpleDirectoryReader(output_folder).load_data()

    # Step 7: Build an index from the documents
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    return index

def process_video_and_query(query: str,index: VectorStoreIndex):
    """
    This function processes a video file to extract audio, convert it to text,
    build a searchable index, and answer a given natural language query.
    
    Parameters:
        query (str): The natural language query to be answered from video content.

    Returns:
        str: The answer generated from the indexed content.
    """
    query_engine = index.as_query_engine()
    answer = query_engine.query(query)

    # Optional: print debug info
    print(answer.get_formatted_sources())
    print("query was:", query)
    print("answer was:", answer)

    return str(answer)

