# manim -pql video_scene.py VideoScene
from manim import *

# Helper for block icon

def create_block(height=0.6, width=0.9, color=BLUE):
    """
    Creates a stylized block (rectangle with a little 3D shading)
    """
    block = Rectangle(height=height, width=width, stroke_color=color, fill_color=color, fill_opacity=0.6)
    highlight = Rectangle(height=height * 0.15, width=width * 0.9,
                         fill_color=WHITE, fill_opacity=0.25, stroke_width=0)
    highlight.next_to(block.get_top(), DOWN, buff=-highlight.get_height() / 2)
    return VGroup(block, highlight)

def create_chain(num_blocks=4, block_color=BLUE):
    """Creates a group of blocks in a row connected by small lines (the 'chain')"""
    blocks = VGroup()
    connects = VGroup()
    for i in range(num_blocks):
        blk = create_block(color=block_color)
        blocks.add(blk)
    blocks.arrange(RIGHT, buff=0.25)
    for i in range(num_blocks - 1):
        start = blocks[i].get_right()
        end = blocks[i+1].get_left()
        conn = Line(start, end, stroke_color=YELLOW, stroke_width=4)
        connects.add(conn)
    return VGroup(blocks, connects)

class VideoScene(Scene):
    def construct(self):
        # 1. Display the main content text
        content_text = "Every transaction is a 'block', tightly linked into a 'chain'"
        text = Text(content_text, font_size=36, color=WHITE)
        text.to_edge(UP)
        self.play(FadeIn(text), run_time=0.7)

        # 2. Animate blocks & chain under the text
        chain = create_chain(4)
        chain.scale(1.25)
        chain.next_to(text, DOWN, buff=0.5)
        blocks, connectors = chain

        # Pulse in blocks one by one for visual clarity (educational)
        anims = []
        for blk in blocks:
            anims.append(FadeIn(blk, shift=DOWN, scale=0.9))
        self.play(*anims, run_time=0.9)
        self.play(Create(connectors, lag_ratio=0.5), run_time=0.45)

        # 3. Fade in a translucent Rectangle background for extra focus
        focus_bg = Rectangle(width=6.5, height=2, fill_color=BLACK, fill_opacity=0.3, stroke_width=0)
        focus_bg.move_to(chain.get_center())
        self.play(FadeIn(focus_bg), run_time=0.2)
        self.add(focus_bg, blocks, connectors, text)  # Ensure draw order
        
        # Slight emphasis (wiggle) on chain to imply linkage
        self.play(chain.animate.shift(0.1 * RIGHT), run_time=0.08)
        self.play(chain.animate.shift(0.08 * LEFT), run_time=0.08)
        self.play(chain.animate.shift(0.02 * RIGHT), run_time=0.04)

        # Wait for narration catch-up
        self.wait(0.5)

        # Quickly fade everything out
        self.play(
            FadeOut(VGroup(text, chain, focus_bg)),
            run_time=0.35
        )

        # Total duration: ~3.0 seconds

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause