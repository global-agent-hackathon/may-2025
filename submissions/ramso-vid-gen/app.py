"""
Ramso - AI Video Generation System
A Streamlit app that generates educational videos from concepts using AI agents.
"""

import streamlit as st
import os
import time
from pathlib import Path

# Import our modules
from agents import get_script_agent, get_manim_agent
from video_generator import ChunkedVideoGenerator

# Page configuration
st.set_page_config(
    page_title="Ramso - AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4ECDC4;
    }
    .stProgress > div > div > div > div {
        background-color: #4ECDC4;
    }
    .chunk-info {
        background: #e8f4fd;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎬 Ramso AI Video Generator</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 How it works")
        st.markdown("""
        1. **📝 Script Generation**: AI creates a structured 2-minute educational script
        2. **✂️ Chunking**: Script is broken into 5-second segments for better sync
        3. **🎨 Animation**: Each chunk gets custom Manim animations
        4. **🎙️ Voiceover**: Professional voice narration for each segment
        5. **🎥 Rendering**: High-quality video rendering per chunk
        6. **🔗 Assembly**: All chunks combined into final video
        """)
        
        st.markdown("### ✨ Features")
        st.markdown("""
        - 🎯 **Chunked Generation**: 5-second segments for perfect sync
        - 🎨 **Custom Icons**: Built-in geometric icons (no external files)
        - 📊 **Real-time Progress**: Live updates on generation status
        - 🎙️ **Voice Sync**: Audio perfectly matched to visuals
        - 🤖 **OpenAI Powered**: GPT-4o for script and animation generation
        """)
    
    # Initialize concept input value from session state or default
    if 'selected_concept' not in st.session_state:
        st.session_state.selected_concept = ""
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💡 Enter a concept to explain")
        
        # Duration controls
        st.markdown("#### ⏱️ Video Settings")
        duration_cols = st.columns(2)
        
        with duration_cols[0]:
            video_duration = st.selectbox(
                "📹 Total Video Duration",
                options=[30, 60, 90, 120],
                index=0,  # Default to 30 seconds for testing
                format_func=lambda x: f"{x} seconds",
                help="Choose total video length (shorter = faster generation)"
            )
        
        with duration_cols[1]:
            chunk_duration = st.selectbox(
                "✂️ Chunk Duration", 
                options=[3, 5, 10],
                index=0,  # Default to 3 seconds for testing
                format_func=lambda x: f"{x} seconds per chunk",
                help="Smaller chunks = more precise sync but longer generation"
            )
        
        # Show estimated chunks
        estimated_chunks = max(1, video_duration // chunk_duration)
        st.info(f"📊 This will create approximately **{estimated_chunks} chunks** to render")
        
        # Example concepts buttons (placed before text input)
        st.markdown("#### 🌟 Popular concepts to try:")
        example_cols = st.columns(4)
        
        examples = [
            "🔗 Blockchain Technology",
            "🤖 Machine Learning Basics", 
            "⚛️ Quantum Computing",
            "🧬 DNA Replication"
        ]
        
        for i, example in enumerate(examples):
            with example_cols[i]:
                if st.button(example, key=f"example_{i}"):
                    # Extract the concept from the example (remove emoji and first word)
                    concept_text = example.split(" ", 1)[1] if " " in example else example
                    st.session_state.selected_concept = concept_text
                    st.rerun()
        
        # Text input with value from session state
        concept = st.text_input(
            "What would you like to create a video about?",
            value=st.session_state.selected_concept,
            placeholder="e.g., How does blockchain work?, What is machine learning?, Quantum computing basics...",
            key="concept_input"
        )
        
        # Update session state when text input changes
        if concept != st.session_state.selected_concept:
            st.session_state.selected_concept = concept
    
    with col2:
        st.markdown("### 🎬 Generate Video")
        generate_button = st.button(
            "🚀 Start Generation",
            disabled=not concept.strip() if concept else True,
            use_container_width=True,
            type="primary"
        )
    
    # Video generation logic
    if generate_button and concept:
        generate_video(concept.strip(), video_duration, chunk_duration)
    
    # Display previous videos
    display_previous_videos()

def generate_video(concept: str, video_duration: int = 30, chunk_duration: int = 3):
    """Generate video with real-time progress updates and custom durations"""
    
    # Initialize progress tracking
    if 'progress_bar' not in st.session_state:
        st.session_state.progress_bar = st.progress(0)
    
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        st.markdown("### 🎬 Generating Your Video")
        progress_bar = st.progress(0, "🚀 Initializing video generation...")
        st.session_state.progress_bar = progress_bar
        
        # Live status updates
        status_placeholder = st.empty()
        chunk_info_placeholder = st.empty()
    
    def update_progress_callback(message: str, progress: float = None):
        """Callback function for progress updates"""
        try:
            if progress is not None:
                progress_bar.progress(progress, message)
            else:
                # Just update the status message
                status_placeholder.info(message)
        except Exception as e:
            print(f"Progress update error: {e}")
    
    try:
        # Initialize agents and generator
        with status_container:
            status_placeholder.info("🤖 Loading AI agents...")
        
        script_agent = get_script_agent()
        manim_agent = get_manim_agent()
        
        # Create video generator with custom settings
        video_generator = ChunkedVideoGenerator()
        video_generator.chunk_duration = chunk_duration  # Set custom chunk duration
        
        # Start generation with progress tracking
        start_time = time.time()
        
        with status_container:
            status_placeholder.info(f"🎯 Generating {video_duration}s video for: **{concept}** (chunks: {chunk_duration}s each)")
        
        # Generate the video with custom duration and progress callback
        video_path = video_generator.generate_complete_video(
            concept, script_agent, manim_agent, 
            total_duration=video_duration,
            progress_callback=update_progress_callback
        )
        
        # Final results
        elapsed_time = time.time() - start_time
        
        if video_path and os.path.exists(video_path):
            progress_bar.progress(1.0, "✅ Video generation complete!")
            
            with status_container:
                status_placeholder.success(f"🎉 Video generated successfully in {elapsed_time:.1f} seconds!")
                
                # Display the video
                st.markdown("### 🎥 Your Generated Video")
                st.video(video_path)
                
                # Video details
                video_file = Path(video_path)
                file_size = video_file.stat().st_size / (1024 * 1024)  # Size in MB
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📁 File Size", f"{file_size:.2f} MB")
                with col2:
                    st.metric("⏱️ Generation Time", f"{elapsed_time:.1f}s")
                with col3:
                    st.metric("🎬 Duration", f"{video_duration}s")
                with col4:
                    st.metric("✂️ Chunks", f"{chunk_duration}s each")
                
                # Download button
                with open(video_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Video",
                        data=file.read(),
                        file_name=f"{concept.replace(' ', '_')}_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
        else:
            progress_bar.progress(0.0, "❌ Video generation failed")
            with status_container:
                status_placeholder.error("❌ Failed to generate video. Please try again or check the logs.")
                
    except Exception as e:
        progress_bar.progress(0.0, "❌ Error occurred")
        with status_container:
            status_placeholder.error(f"❌ An error occurred: {str(e)}")
        
        # Show error details in expander
        with st.expander("🔍 Error Details"):
            st.code(str(e))
    
    finally:
        # Clean up progress tracking
        if 'progress_bar' in st.session_state:
            del st.session_state.progress_bar

def display_previous_videos():
    """Display previously generated videos"""
    output_dir = Path("output")
    
    if output_dir.exists():
        video_files = list(output_dir.glob("*_final.mp4"))
        
        if video_files:
            st.markdown("### 📹 Previously Generated Videos")
            
            # Sort by modification time (newest first)
            video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            cols = st.columns(min(3, len(video_files)))
            
            for i, video_file in enumerate(video_files[:6]):  # Show max 6 videos
                with cols[i % 3]:
                    # Extract concept name from filename
                    concept_name = video_file.stem.replace("_final", "").replace("_", " ").title()
                    
                    st.markdown(f"#### {concept_name}")
                    
                    # Show video thumbnail/preview
                    try:
                        st.video(str(video_file))
                        
                        # File info
                        file_size = video_file.stat().st_size / (1024 * 1024)
                        mod_time = time.ctime(video_file.stat().st_mtime)
                        
                        st.caption(f"📁 {file_size:.1f} MB • 📅 {mod_time}")
                        
                        # Download button
                        with open(video_file, "rb") as file:
                            st.download_button(
                                label="📥 Download",
                                data=file.read(),
                                file_name=video_file.name,
                                mime="video/mp4",
                                key=f"download_{i}",
                                use_container_width=True
                            )
                            
                    except Exception as e:
                        st.error(f"Error loading video: {str(e)}")

if __name__ == "__main__":
    main() 