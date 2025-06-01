from manim import *

# Helper: emojized_text (Manim version 0.18+)
def emojized_text(text, **kwargs):
    return MarkupText(text, **kwargs)

# Helper: create_blockchain_icon
# Visualizes a simple blockchain: 3 blocks connected by arrows
# All with Manim geometric primitives.
def create_blockchain_icon(block_width=1.2, block_height=0.7, block_spacing=1.5):
    blocks = VGroup()
    arrows = VGroup()
    for i in range(3):
        block = Rectangle(width=block_width, height=block_height, color=BLUE, fill_color=BLUE_E, fill_opacity=0.7)
        block.shift(RIGHT * block_spacing * i)
        # Add small square as 'hash' at top left of each block
        hash_sq = Square(side_length=0.18, color=YELLOW, fill_color=YELLOW, fill_opacity=0.8)
        hash_sq.move_to(block.get_corner(UL) + DOWN * 0.18 + RIGHT * 0.18)
        block_group = VGroup(block, hash_sq)
        blocks.add(block_group)
        if i > 0:
            # Connect from previous to current block
            arrow = Arrow(start=blocks[i-1].get_right() + RIGHT*0.12, end=block.get_left() + LEFT*0.12, buff=0, color=GREEN_D, stroke_width=5)
            arrows.add(arrow)
    blockchain_icon = VGroup(blocks, arrows)
    # Center first block at (0,0)
    blockchain_icon.move_to(ORIGIN)
    return blockchain_icon

class VideoScene(Scene):
    def construct(self):
        # Introduction Text
        title_text = Text("Understanding Blockchain Technology in 30 Seconds",
                         font_size=38, color=YELLOW).to_edge(UP)
        
        # Blockchain icon
        blockchain_icon = create_blockchain_icon()
        blockchain_icon.scale(1.1)
        blockchain_icon.next_to(title_text, DOWN, buff=0.6)
        
        # Step 1: Fade in title quickly
        self.play(FadeIn(title_text, shift=DOWN), run_time=0.6)
        
        # Step 2: Animate blockchain icon appearing with slight pop
        self.play(FadeIn(blockchain_icon, scale=0.8), run_time=0.7)
        
        # Step 3: Pulse the middle block (to suggest 'transaction')
        blocks = blockchain_icon[0]
        mid_block = blocks[1]
        self.play(mid_block.animate.set_fill(GREEN, opacity=1.0).set_stroke(width=6, color=WHITE),
                  run_time=0.35)
        self.play(mid_block.animate.set_fill(BLUE_E, opacity=0.7).set_stroke(width=2, color=BLUE),
                  run_time=0.25)
        
        # Remain on screen briefly
        self.wait(0.7)
        
        # Fade out all
        self.play(FadeOut(title_text), FadeOut(blockchain_icon), run_time=0.3)
        
        # Hold end
        self.wait(0.2)

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause