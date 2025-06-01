from manim import *

from manim import Scene, Text, Create, FadeIn, FadeOut, VGroup, UP, YELLOW, GREEN, BLUE

class VideoScene(Scene):
    def construct(self):
        # Create text
        content_text = Text("That’s the magic behind the hype!", font_size=48, color=YELLOW)
        
        # Create blockchain-related icon using basic shapes
        block_icon = self.create_blockchain_icon(GREEN)
        
        # Position text and icon
        block_icon.next_to(content_text, UP, buff=1)
        
        # Group text and icon
        animation_group = VGroup(content_text, block_icon)
        
        # Create animation sequence
        self.play(FadeIn(animation_group))
        self.wait(2)  # Pausing for narration and emphasis
        self.play(FadeOut(animation_group))

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause
    def create_blockchain_icon(self, color):
        # Representation of a simple blockchain icon with squares connected
        square_1 = Text("█", font_size=36, color=color).shift(0.5*UP + LEFT)
        square_2 = Text("█", font_size=36, color=color).next_to(square_1, RIGHT, buff=0.2)
        link = Text("━", font_size=36, color=color).next_to(square_1, RIGHT, buff=0.05)
        
        blockchain_icon = VGroup(square_1, link, square_2)
        return blockchain_icon