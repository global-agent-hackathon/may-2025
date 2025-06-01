# Manim animation visualizing:
# "Each block is verified across a network of computers"

from manim import *

# Helper icon for a blockchain block
def create_blockchain_icon():
    block = Rectangle(width=0.8, height=0.5, color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.8, stroke_width=4)
    lock = ArcBetweenPoints(block.get_bottom() + 0.17 * UP + 0.15 * LEFT, block.get_bottom() + 0.17 * UP + 0.15 * RIGHT, angle=PI)
    lock.set_stroke(YELLOW, 3)
    shackle = Line(lock.get_start(), lock.get_end(), color=YELLOW, stroke_width=3)
    return VGroup(block, lock, shackle)

# Helper icon for a computer (simple monitor)
def create_computer_icon():
    monitor = Rectangle(width=0.6, height=0.4, color=GREEN_B, fill_color=GREEN_E, fill_opacity=0.75, stroke_width=3)
    base = Rectangle(width=0.25, height=0.05, color=GREY_B, fill_color=GREY_D, fill_opacity=0.8)
    stand = Rectangle(width=0.09, height=0.09, color=GREY_B, fill_color=GREY_C, fill_opacity=0.7)
    base.next_to(monitor, DOWN, buff=0.025)
    stand.next_to(base, DOWN, buff=0.01)
    return VGroup(monitor, base, stand)

class VideoScene(Scene):
    def construct(self):
        # --- 1. Title Text ---
        content_text = "Each block is verified across a network of computers"
        headline = Text(content_text, font_size=36, weight=MEDIUM, color=YELLOW_E)
        headline.to_edge(UP)
        self.play(FadeIn(headline, shift=DOWN), run_time=0.7)
        self.wait(0.3)

        # --- 2. Blockchain Block at Center ---
        block = create_blockchain_icon().scale(1.1)
        block.move_to(ORIGIN)
        self.play(FadeIn(block, scale=0.5), run_time=0.5)
        
        # --- 3. Network of computers around block ---
        computer_icons = VGroup()
        computer_positions = [
            1.6 * UP + 2.1 * LEFT,
            2 * RIGHT + 1.3 * UP,
            2.2 * RIGHT + 0.7 * DOWN,
            1.3 * DOWN + 2 * LEFT,
            2.5 * DOWN + 0.8 * RIGHT,
        ]
        for pos in computer_positions:
            comp = create_computer_icon().scale(0.7)
            comp.move_to(pos)
            computer_icons.add(comp)
        self.play(LaggedStartMap(FadeIn, computer_icons, shift=DOWN, lag_ratio=0.18), run_time=0.6)
        
        # --- 4. Animated connections (verification lines) ---
        network_lines = VGroup()
        for comp in computer_icons:
            line = Line(comp.get_center(), block.get_edge_center(direction=comp.get_center()-block.get_center()),
                        stroke_color=YELLOW_B, stroke_width=3)
            network_lines.add(line)
        self.play(Create(network_lines, lag_ratio=0.19), run_time=0.5)

        # --- 5. Verification Animation (Block glows, computers highlight)
        self.play(
            block.animate.set_color(GREEN_D).set_fill(GREEN_B, 0.90),
            computer_icons.animate.set_color(YELLOW_D),
            run_time=0.4
        )

        # Hold final result
        self.wait(0.4)  # To complete ~3s


        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause