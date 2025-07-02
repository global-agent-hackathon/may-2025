"""
Video Generator Module

Handles the complete pipeline from concept to final video in 5-second chunks:
1. Generate script using Script Agent
2. Break script into 5-second chunks
3. For each chunk: Generate Manim code, voiceover, and render
4. Combine all chunks into final video
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from gtts import gTTS
from dotenv import load_dotenv
from agents import VideoScript, ManimCode, ScriptScene
import streamlit as st
import time

load_dotenv()

# Add Homebrew paths to environment for FFmpeg
os.environ['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + os.environ.get('PATH', '')

class ChunkedVideoGenerator:
    """
    Handles video generation in configurable chunks with voice synchronization.
    Generates educational videos from concepts using AI agents.
    """
    
    def __init__(self, chunk_duration: int = 3):
        """
        Initialize the chunked video generator.
        
        Args:
            chunk_duration: Duration of each chunk in seconds (default: 3)
        """
        self.chunk_duration = chunk_duration
        # Use absolute paths to prevent nesting
        self.output_dir = Path("generated_videos").resolve()
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        self.chunks_dir = self.output_dir / "chunks"
        self.chunks_dir.mkdir(exist_ok=True)
        
        self.audio_dir = self.output_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True)

    def break_script_into_chunks(self, script: str, total_duration: int = 30) -> List[Dict]:
        """
        Break script into time-based chunks for synchronized video generation.
        
        Args:
            script: The complete script text
            total_duration: Total video duration in seconds
            
        Returns:
            List of chunk dictionaries with text and timing information
        """
        # Split script into sentences
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        
        # Calculate chunks needed
        num_chunks = max(1, total_duration // self.chunk_duration)
        
        # Distribute sentences across chunks
        chunks = []
        sentences_per_chunk = max(1, len(sentences) // num_chunks)
        
        for i in range(num_chunks):
            start_idx = i * sentences_per_chunk
            end_idx = min((i + 1) * sentences_per_chunk, len(sentences))
            
            # For the last chunk, include any remaining sentences
            if i == num_chunks - 1:
                end_idx = len(sentences)
            
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = '. '.join(chunk_sentences)
            
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    'chunk_id': i + 1,
                    'text': chunk_text,
                    'start_time': i * self.chunk_duration,
                    'duration': self.chunk_duration,
                    'sentences': chunk_sentences
                })
        
        return chunks

    def generate_voiceover(self, text: str, chunk_id: int) -> str:
        """
        Generate voiceover for a text chunk using Google Text-to-Speech.
        
        Args:
            text: Text to convert to speech
            chunk_id: Unique identifier for the chunk
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save as temporary MP3 file
            temp_mp3 = self.audio_dir / f"chunk_{chunk_id}_temp.mp3"
            tts.save(str(temp_mp3))
            
            # Convert to WAV using ffmpeg for better compatibility
            audio_path = self.audio_dir / f"chunk_{chunk_id}.wav"
            
            # Try to find ffmpeg in common locations
            ffmpeg_paths = [
                '/opt/homebrew/bin/ffmpeg',
                '/usr/local/bin/ffmpeg', 
                'ffmpeg'  # System PATH
            ]
            
            ffmpeg_cmd = None
            for path in ffmpeg_paths:
                try:
                    result = subprocess.run([path, '-version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        ffmpeg_cmd = path
                        break
                except FileNotFoundError:
                    continue
            
            if ffmpeg_cmd:
                # Use ffmpeg to convert MP3 to WAV
                result = subprocess.run([
                    ffmpeg_cmd, '-i', str(temp_mp3), 
                    '-acodec', 'pcm_s16le', 
                    '-ar', '44100', 
                    '-y',  # Overwrite output file
                    str(audio_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"FFmpeg conversion warning: {result.stderr}")
                    # If conversion fails, use the MP3 file
                    audio_path = temp_mp3
                else:
                    # Remove temporary MP3 file if conversion succeeded
                    temp_mp3.unlink(missing_ok=True)
            else:
                print("FFmpeg not found, using MP3 format")
                # If FFmpeg not available, rename MP3 to final path
                final_mp3 = self.audio_dir / f"chunk_{chunk_id}.mp3"
                temp_mp3.rename(final_mp3)
                audio_path = final_mp3
            
            return str(audio_path)
            
        except Exception as e:
            print(f"Error generating voiceover for chunk {chunk_id}: {e}")
            return None

    def render_manim_chunk(self, manim_code: str, chunk_id: int, progress_callback=None) -> str:
        """
        Render a single video chunk using Manim with improved timing.
        
        Args:
            manim_code: Manim code for the chunk
            chunk_id: Unique identifier for the chunk
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to the rendered video file
        """
        try:
            if progress_callback:
                progress_callback(f"🎬 Rendering chunk {chunk_id}...")
            
            # Create chunk-specific directory
            chunk_dir = self.chunks_dir / f"chunk_{chunk_id}"
            chunk_dir.mkdir(exist_ok=True)
            
            # Fix timing issues in Manim code
            fixed_code = self.fix_manim_timing(manim_code)
            
            # Write the Manim code to a file
            manim_file = chunk_dir / f"chunk_{chunk_id}.py"
            with open(manim_file, 'w') as f:
                f.write(fixed_code)
            
            # Render the video using Manim (silent mode)
            import subprocess
            
            # Fixed command - use absolute path and correct working directory
            cmd = [
                'manim', 'render',
                f'chunk_{chunk_id}.py', 'VideoScene',  # Use relative filename
                '-q', 'm',  # Medium quality (correct flag)
                '--format', 'mp4',
                '--disable_caching'
            ]
            
            if progress_callback:
                progress_callback(f"🔄 Processing chunk {chunk_id} with Manim...")
            
            # Run from the chunk directory to avoid path issues
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(chunk_dir))
            
            if result.returncode != 0:
                print(f"Manim rendering failed for chunk {chunk_id}: {result.stderr}")
                return None
            
            # Find the generated video file in the media directory
            media_dir = chunk_dir / "media" / "videos" / f"chunk_{chunk_id}" / "720p30"
            video_files = list(media_dir.glob("*.mp4"))
            
            if video_files:
                video_path = str(video_files[0])
                if progress_callback:
                    progress_callback(f"✅ Chunk {chunk_id} rendered successfully")
                return video_path
            else:
                # Fallback: search all subdirectories for MP4 files
                video_files = list(chunk_dir.glob("**/*.mp4"))
                if video_files:
                    video_path = str(video_files[0])
                    if progress_callback:
                        progress_callback(f"✅ Chunk {chunk_id} rendered successfully")
                    return video_path
                else:
                    print(f"No video file found for chunk {chunk_id}")
                    return None
                
        except Exception as e:
            print(f"Error rendering chunk {chunk_id}: {e}")
            if progress_callback:
                progress_callback(f"❌ Failed to render chunk {chunk_id}: {str(e)}")
            return None

    def fix_manim_timing(self, manim_code: str) -> str:
        """
        Fix timing issues in Manim code and ensure proper structure.
        
        Args:
            manim_code: Original Manim code
            
        Returns:
            Fixed Manim code with proper timing and structure
        """
        # Ensure proper imports
        if 'from manim import *' not in manim_code:
            manim_code = 'from manim import *\n\n' + manim_code
        
        # Replace invalid wait(0) with wait(0.1)
        fixed_code = manim_code.replace('self.wait(0)', 'self.wait(0.1)')
        
        # Ensure minimum wait times
        import re
        
        # Find all wait() calls and ensure they have positive values
        def fix_wait_call(match):
            wait_value = match.group(1)
            try:
                value = float(wait_value)
                if value <= 0:
                    return 'self.wait(0.1)'
                return match.group(0)
            except:
                return 'self.wait(0.1)'
        
        fixed_code = re.sub(r'self\.wait\(([^)]+)\)', fix_wait_call, fixed_code)
        
        # Ensure we have a VideoScene class
        if 'class VideoScene' not in fixed_code:
            # If no VideoScene class, create a simple one with meaningful content
            simple_scene = f"""
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Simple animation for {self.chunk_duration} seconds
        title = Text("Learning in Progress...", font_size=40, color=BLUE)
        self.play(Write(title), run_time=1)
        self.wait({self.chunk_duration - 1})
"""
            return simple_scene
        
        # Add proper scene duration based on chunk duration
        if 'class VideoScene' in fixed_code and 'def construct(self):' in fixed_code:
            # Find the construct method and ensure it has proper timing
            lines = fixed_code.split('\n')
            
            # Look for the end of the construct method
            in_construct = False
            construct_indent = 0
            
            for i, line in enumerate(lines):
                if 'def construct(self):' in line:
                    in_construct = True
                    construct_indent = len(line) - len(line.lstrip())
                    continue
                
                if in_construct:
                    # Check if we're still in the construct method
                    current_indent = len(line) - len(line.lstrip()) if line.strip() else construct_indent + 4
                    
                    # If we hit a line with same or less indentation (and it's not empty), we're out of construct
                    if line.strip() and current_indent <= construct_indent:
                        # Insert timing adjustment before this line
                        timing_line = ' ' * (construct_indent + 4) + f'# Ensure total duration is {self.chunk_duration} seconds'
                        wait_line = ' ' * (construct_indent + 4) + f'self.wait(0.5)  # Final pause'
                        lines.insert(i, wait_line)
                        lines.insert(i, timing_line)
                        break
            else:
                # If we didn't find the end, add at the end of the file
                lines.append(' ' * (construct_indent + 4) + f'# Ensure total duration is {self.chunk_duration} seconds')
                lines.append(' ' * (construct_indent + 4) + f'self.wait(0.5)  # Final pause')
            
            fixed_code = '\n'.join(lines)
        
        return fixed_code

    def combine_chunks(self, video_chunks: List[str], audio_chunks: List[str], output_path: str, progress_callback=None) -> str:
        """
        Combine video and audio chunks into final video using FFmpeg.
        
        Args:
            video_chunks: List of video file paths
            audio_chunks: List of audio file paths  
            output_path: Path for the final combined video
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to the final combined video
        """
        try:
            if progress_callback:
                progress_callback("🔗 Combining video chunks...")
            
            # Find FFmpeg
            ffmpeg_paths = [
                '/opt/homebrew/bin/ffmpeg',
                '/usr/local/bin/ffmpeg', 
                'ffmpeg'  # System PATH
            ]
            
            ffmpeg_cmd = None
            for path in ffmpeg_paths:
                try:
                    result = subprocess.run([path, '-version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        ffmpeg_cmd = path
                        break
                except FileNotFoundError:
                    continue
            
            if not ffmpeg_cmd:
                raise Exception("FFmpeg not found. Please install FFmpeg to combine video chunks.")
            
            # Create temporary files list for FFmpeg
            temp_dir = self.output_dir / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            # Create file list for concatenation
            file_list_path = temp_dir / "file_list.txt"
            
            # Combine video and audio for each chunk first
            combined_chunks = []
            
            for i, (video_path, audio_path) in enumerate(zip(video_chunks, audio_chunks)):
                if not video_path or not audio_path:
                    continue
                    
                # Use absolute paths to prevent nesting
                chunk_output = temp_dir / f"combined_chunk_{i}.mp4"
                
                # Combine video and audio for this chunk
                cmd = [
                    ffmpeg_cmd, '-i', str(Path(video_path).resolve()), '-i', str(Path(audio_path).resolve()),
                    '-c:v', 'copy', '-c:a', 'aac', '-shortest',
                    '-y', str(chunk_output.resolve())
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    combined_chunks.append(str(chunk_output.resolve()))
                    if progress_callback:
                        progress_callback(f"✅ Combined chunk {i+1}/{len(video_chunks)}")
                else:
                    print(f"Warning: Failed to combine chunk {i+1}: {result.stderr}")
            
            if not combined_chunks:
                raise Exception("No chunks were successfully combined")
            
            # Create concatenation file list with absolute paths
            with open(file_list_path, 'w') as f:
                for chunk_path in combined_chunks:
                    f.write(f"file '{chunk_path}'\n")
            
            # Concatenate all chunks
            if progress_callback:
                progress_callback("🎬 Creating final video...")
            
            final_cmd = [
                ffmpeg_cmd, '-f', 'concat', '-safe', '0', '-i', str(file_list_path.resolve()),
                '-c', 'copy', '-y', str(Path(output_path).resolve())
            ]
            
            result = subprocess.run(final_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg concatenation failed: {result.stderr}")
            
            # Clean up temporary files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            if progress_callback:
                progress_callback("🎉 Final video created successfully!")
            
            return output_path
            
        except Exception as e:
            print(f"Error combining chunks: {e}")
            if progress_callback:
                progress_callback(f"❌ Failed to combine chunks: {str(e)}")
            return None

    def generate_complete_video(self, concept: str, script_agent, manim_agent, total_duration: int = 30, progress_callback=None) -> str:
        """
        Generate complete video with chunked processing and custom duration.
        
        Args:
            concept: The concept to explain
            script_agent: AI agent for script generation
            manim_agent: AI agent for Manim code generation
            total_duration: Total video duration in seconds
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to the final video file
        """
        try:
            # Update progress tracking
            def update_progress(message: str, progress: float = None):
                if progress_callback:
                    progress_callback(message, progress)
                else:
                    print(message)
            
            # Step 1: Generate script
            update_progress("📝 Generating script...", 0.1)
            script_response = script_agent.run(f"Create a {total_duration}-second educational video script explaining: {concept}")
            
            # Extract script content
            if hasattr(script_response, 'content') and hasattr(script_response.content, 'scenes'):
                # If we get a structured VideoScript response
                script_data = script_response.content
                script = f"{script_data.title}. " + " ".join([scene.narration for scene in script_data.scenes])
            elif hasattr(script_response, 'content'):
                script = str(script_response.content)
            else:
                script = str(script_response)
            
            # Step 2: Break script into chunks
            update_progress("✂️ Breaking script into chunks...", 0.2)
            chunks = self.break_script_into_chunks(script, total_duration)
            
            if not chunks:
                raise Exception("Failed to create script chunks")
            
            update_progress(f"📊 Created {len(chunks)} chunks of {self.chunk_duration}s each", 0.25)
            
            # Step 3: Process each chunk
            video_chunks = []
            audio_chunks = []
            
            for i, chunk in enumerate(chunks):
                # Fix progress calculation to stay within 0.25 to 0.85 range
                base_progress = 0.25 + (i / len(chunks)) * 0.6  # 25% to 85%
                chunk_progress = min(base_progress, 0.85)  # Ensure it doesn't exceed 85%
                
                # Generate Manim code for chunk
                update_progress(f"🎨 Generating visuals for chunk {i+1}/{len(chunks)}", chunk_progress)
                
                manim_prompt = f"""
                Create Manim code for this educational content:
                Topic: {concept}
                Content: {chunk['text']}
                Duration: {chunk['duration']} seconds
                
                Requirements:
                - Create a Scene class named 'VideoScene'
                - Create engaging visual animations using the actual content text
                - Use proper timing with self.wait() calls
                - Include text, shapes, and transitions
                - Make it educational and clear
                - Ensure total scene duration is approximately {chunk['duration']} seconds
                - Use only basic Manim primitives (no external files)
                - NEVER use the phrase "Educational Content" - use the actual content text instead
                - Display the actual chunk text: "{chunk['text']}"
                - Make the visuals relate to the specific topic: {concept}
                """
                
                manim_response = manim_agent.run(manim_prompt)
                
                # Extract Manim code
                if hasattr(manim_response, 'content') and hasattr(manim_response.content, 'python_code'):
                    manim_code = manim_response.content.python_code
                elif hasattr(manim_response, 'content'):
                    manim_code = str(manim_response.content)
                else:
                    manim_code = str(manim_response)
                
                # Generate voiceover
                voiceover_progress = min(chunk_progress + 0.03, 0.88)
                update_progress(f"🎤 Generating voiceover for chunk {i+1}", voiceover_progress)
                audio_path = self.generate_voiceover(chunk['text'], chunk['chunk_id'])
                
                if audio_path:
                    audio_chunks.append(audio_path)
                
                # Render video chunk
                render_progress = min(chunk_progress + 0.06, 0.91)
                update_progress(f"🎬 Rendering chunk {i+1}", render_progress)
                video_path = self.render_manim_chunk(manim_code, chunk['chunk_id'], update_progress)
                
                # If Manim fails, create a simple fallback video
                if not video_path:
                    update_progress(f"🔄 Creating fallback video for chunk {i+1}", render_progress)
                    video_path = self.create_fallback_video(chunk['text'], chunk['chunk_id'])
                
                if video_path:
                    video_chunks.append(video_path)
                    completion_progress = min(chunk_progress + 0.09, 0.94)
                    update_progress(f"✅ Chunk {i+1} completed", completion_progress)
                else:
                    completion_progress = min(chunk_progress + 0.09, 0.94)
                    update_progress(f"⚠️ Chunk {i+1} failed, continuing...", completion_progress)
            
            # Step 4: Combine all chunks
            if not video_chunks:
                raise Exception("No video chunks were successfully generated")
            
            update_progress("🔗 Combining all chunks into final video...", 0.95)
            
            # Create final output path
            safe_concept = "".join(c for c in concept if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = int(time.time())
            final_video_path = self.output_dir / f"{safe_concept}_{timestamp}.mp4"
            
            # Combine chunks
            combined_path = self.combine_chunks(video_chunks, audio_chunks, str(final_video_path), update_progress)
            
            if combined_path and os.path.exists(combined_path):
                update_progress("🎉 Video generation completed successfully!", 1.0)
                return combined_path
            else:
                raise Exception("Failed to combine video chunks")
                
        except Exception as e:
            update_progress(f"❌ Error: {str(e)}", 0.0)
            print(f"Video generation error: {e}")
            return None

    def create_fallback_video(self, text: str, chunk_id: int) -> str:
        """
        Create a simple fallback video for a chunk when Manim fails.
        
        Args:
            text: The text for the chunk
            chunk_id: Unique identifier for the chunk
            
        Returns:
            Path to the created fallback video file
        """
        try:
            # Create a simple text animation using the actual chunk text
            # Truncate text if too long for display and escape quotes
            display_text = text[:80] + "..." if len(text) > 80 else text
            display_text = display_text.replace('"', '\\"').replace("'", "\\'")
            
            simple_scene = f"""
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Text animation using actual content for {self.chunk_duration} seconds
        text = Text("{display_text}", font_size=32, color=WHITE)
        text.scale_to_fit_width(11)
        self.play(Write(text), run_time=1.5)
        self.wait({self.chunk_duration - 1.5})
"""
            
            # Render the simple scene
            video_path = self.render_manim_chunk(simple_scene, chunk_id)
            
            return video_path
            
        except Exception as e:
            print(f"Error creating fallback video for chunk {chunk_id}: {e}")
            return None

# Keep the old VideoGenerator for backward compatibility
VideoGenerator = ChunkedVideoGenerator 