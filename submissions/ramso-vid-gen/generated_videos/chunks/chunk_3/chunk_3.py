# Manim animation for: How is trust maintained? Enter blockchain—a distributed digital ledger
from manim import *

# Helper function: Blockchain Icon (group of blue blocks connected)
def create_blockchain_icon(block_color=BLUE_B):
    block_size = 0.4
    blocks = VGroup()
    for i in range(3):
        rect = Square(side_length=block_size, color=block_color, fill_opacity=0.7, stroke_width=2)
        rect.shift(RIGHT * (block_size + 0.15) * i)
        blocks.add(rect)
    # Connect blocks with lines
    lines = VGroup()
    for i in range(2):
        start = blocks[i].get_right()
        end = blocks[i+1].get_left()
        line = Line(start, end, color=YELLOW)
        lines.add(line)
    icon = VGroup(blocks, lines)
    icon.arrange(RIGHT, buff=0)
    return icon

# Helper function: Ledger Icon (like a book)
def create_ledger_icon():
    body = Rectangle(width=0.65, height=0.85, color=GREEN, fill_opacity=0.55, stroke_width=2)
    spine = Rectangle(width=0.12, height=0.85, color=YELLOW_D, fill_opacity=0.7, stroke_width=1.5).next_to(body, LEFT, buff=0)
    lines = VGroup()
    for y in [-0.25, 0, 0.25]:
        l = Line(start=body.get_left() + RIGHT*0.1 + UP*y, end=body.get_right() + LEFT*0.07 + UP*y, color=WHITE, stroke_width=1)
        lines.add(l)
    icon = VGroup(body, spine, lines)
    return icon

class VideoScene(Scene):
    def construct(self):
        # Content text
        title = Text(
            "How is trust maintained?",
            font_size=38,
            weight=BOLD,
            color=WHITE
        )
        subtitle = Text(
            "Enter blockchain—",
            font_size=36,
            color=BLUE_B
        )
        subtitle2 = Text(
            "a distributed digital ledger",
            font_size=30,
            color=GREEN
        )
        subtitle2.next_to(subtitle, DOWN, buff=0.15)
        subtitle.next_to(title, DOWN, buff=0.35)

        # Blockchain and ledger icons
        blockchain_icon = create_blockchain_icon().scale(1.0).next_to(subtitle, LEFT, buff=0.45)
        ledger_icon = create_ledger_icon().scale(0.68).next_to(subtitle2, RIGHT, buff=0.25)

        # Initial fade in: Question
        self.play(Write(title), run_time=0.8)
        self.wait(0.5)
        
        # Animate out question, fade in blockchain part
        self.play(FadeOut(title, shift=UP*0.7), FadeIn(subtitle, shift=DOWN*0.5), FadeIn(blockchain_icon, shift=LEFT*0.5), run_time=0.6)
        self.wait(0.32)
        # Add subtitle2 and ledger icon together
        group_sub = VGroup(subtitle, blockchain_icon)  # for visual alignment
        self.play(FadeIn(subtitle2, shift=DOWN*0.2), FadeIn(ledger_icon, shift=RIGHT*0.14), run_time=0.45)
        self.wait(0.28)
        # Final pulse to highlight 'distributed digital ledger'
        self.play(Indicate(subtitle2, scale_factor=1.09, color=YELLOW_B), ledger_icon.animate.set_color(YELLOW_B), run_time=0.33)
        self.wait(0.37)
        # Total duration: ~3.15s

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause