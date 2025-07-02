
from manim import *

class VideoScene(Scene):
    def construct(self):
        # Simple animation that exactly matches audio duration: 7.4 seconds
        
        # Create main text (actual chunk content)
        main_text = Text("That’s blockchain—a secure, transparent chain of records, trusted by everyone", font_size=28, color=WHITE)
        main_text.scale_to_fit_width(11)
        
        # Create simple visual elements
        title = Text("Blockchain Technology", font_size=24, color=BLUE)
        title.to_edge(UP)
        
        # Simple blockchain visualization
        block1 = Square(side_length=0.8, color=BLUE, fill_opacity=0.7)
        block2 = Square(side_length=0.8, color=GREEN, fill_opacity=0.7)
        block3 = Square(side_length=0.8, color=YELLOW, fill_opacity=0.7)
        
        blocks = VGroup(block1, block2, block3).arrange(RIGHT, buff=0.3)
        blocks.next_to(title, DOWN, buff=1)
        
        # Position main text
        main_text.next_to(blocks, DOWN, buff=1)
        
        # Animation sequence with exact timing
        self.play(Write(title), run_time=1.0)
        self.play(Create(blocks), run_time=1.5)
        self.play(Write(main_text), run_time=2.0)
        
        # Wait for the remaining time to match audio duration exactly
        remaining_time = max(0.5, 7.4 - 4.5)
        self.wait(remaining_time)
