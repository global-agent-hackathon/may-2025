"""
Example usage of Ramso agents
Demonstrates how to generate educational video content programmatically
"""

from agents import get_script_agent, get_manim_agent
from video_generator import VideoGenerator
import json

def generate_script_example():
    """Example of generating a script for a concept"""
    print("📝 Script Generation Example")
    print("=" * 50)
    
    # Get the script agent
    script_agent = get_script_agent()
    
    # Define a concept to explain
    concept = "how does RSA encryption work"
    
    print(f"Concept: {concept}")
    print("\nGenerating script...")
    
    # Generate the script
    response = script_agent.run(f"""
    Create a 2-minute educational video script explaining: {concept}
    
    Make sure to:
    1. Start with an engaging hook
    2. Break down the concept into digestible parts
    3. Use visual metaphors and analogies
    4. Include specific scenes with timing
    5. End with a practical takeaway
    """)
    
    print("\n✅ Script generated!")
    print("\n📄 Generated Script:")
    print("-" * 50)
    print(response.content)
    print("-" * 50)
    
    return response.content

def generate_manim_code_example(script_content):
    """Example of converting script to Manim code"""
    print("\n🎨 Manim Code Generation Example")
    print("=" * 50)
    
    # Get the manim agent
    manim_agent = get_manim_agent()
    
    print("Converting script to Manim animation code...")
    
    # Generate Manim code
    response = manim_agent.run(f"""
    Convert this educational video script to Manim animation code:
    
    {script_content}
    
    Requirements:
    1. Create a Scene class called 'RSAEncryptionScene'
    2. Implement each scene described in the script
    3. Use appropriate mathematical visualizations
    4. Include timing that matches the narration
    5. Use 3Blue1Brown color scheme and style
    6. Add comments explaining each animation section
    """)
    
    print("\n✅ Manim code generated!")
    print("\n💻 Generated Manim Code:")
    print("-" * 50)
    print(response.content)
    print("-" * 50)
    
    return response.content

def save_outputs(script_content, manim_code, concept):
    """Save the generated content to files"""
    print("\n💾 Saving outputs...")
    
    # Create output directory
    import os
    os.makedirs("example_output", exist_ok=True)
    
    # Save script
    script_file = f"example_output/{concept.replace(' ', '_')}_script.md"
    with open(script_file, 'w') as f:
        f.write(script_content)
    print(f"📄 Script saved to: {script_file}")
    
    # Save Manim code
    manim_file = f"example_output/{concept.replace(' ', '_')}_animation.py"
    with open(manim_file, 'w') as f:
        f.write(manim_code)
    print(f"💻 Manim code saved to: {manim_file}")
    
    print(f"\n🎬 To render the video, run:")
    print(f"manim -pql {manim_file} RSAEncryptionScene")

def complete_pipeline_example():
    """Example of running the complete video generation pipeline"""
    print("\n🚀 Complete Pipeline Example")
    print("=" * 50)
    
    # Initialize video generator
    video_gen = VideoGenerator("example_output")
    
    # Get agents
    script_agent = get_script_agent()
    manim_agent = get_manim_agent()
    
    # Define concept
    concept = "how neural networks learn"
    
    print(f"Generating complete video for: {concept}")
    print("This will take several minutes...")
    
    # Generate complete video
    video_path = video_gen.generate_complete_video(concept, script_agent, manim_agent)
    
    if video_path:
        print(f"\n🎉 Video generated successfully!")
        print(f"📹 Video saved to: {video_path}")
    else:
        print("\n❌ Video generation failed")

def main():
    """Run examples"""
    print("🎬 Ramso Agent Examples")
    print("=" * 60)
    
    # Example 1: Generate script only
    script_content = generate_script_example()
    
    # Example 2: Generate Manim code from script
    manim_code = generate_manim_code_example(script_content)
    
    # Example 3: Save outputs
    save_outputs(script_content, manim_code, "how does RSA encryption work")
    
    # Ask user if they want to run complete pipeline
    print("\n" + "=" * 60)
    user_input = input("\n🤔 Would you like to run the complete video generation pipeline? (y/n): ")
    
    if user_input.lower() in ['y', 'yes']:
        complete_pipeline_example()
    else:
        print("\n✅ Examples completed!")
        print("\n🚀 To run the full Streamlit app: streamlit run app.py")

if __name__ == "__main__":
    main() 