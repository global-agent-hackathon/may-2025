from manim import *

# Helper: simple bank icon (rectangle + columns)
def create_bank_icon():
    bank_body = Rectangle(width=1.2, height=0.6, color=WHITE, fill_opacity=1, fill_color=GRAY_E)
    column1 = Rectangle(width=0.1, height=0.5, color=WHITE, fill_opacity=1, fill_color=WHITE).shift(LEFT*0.3)
    column2 = Rectangle(width=0.1, height=0.5, color=WHITE, fill_opacity=1, fill_color=WHITE)
    column3 = Rectangle(width=0.1, height=0.5, color=WHITE, fill_opacity=1, fill_color=WHITE).shift(RIGHT*0.3)
    roof = Polygon(
        LEFT*0.7 + UP*0.3,
        RIGHT*0.7 + UP*0.3,
        ORIGIN + UP*0.6,
        color=WHITE,
        fill_opacity=1,
        fill_color=WHITE
    )
    return VGroup(bank_body, column1, column2, column3, roof)

# Helper: simple blockchain icon (row of colored blocks w/ arrows)
def create_blockchain_icon(num_blocks=3):
    blocks = []
    arrows = []
    colors = [BLUE, YELLOW, GREEN]
    for i in range(num_blocks):
        block = Square(side_length=0.5, color=colors[i%3], fill_opacity=1, fill_color=colors[i%3])
        block.shift(RIGHT*i*0.7)
        blocks.append(block)
        if i > 0:
            arrow = Arrow(
                blocks[i-1].get_right(),
                blocks[i].get_left(),
                buff=0.05,
                stroke_width=3,
                color=WHITE,
                max_tip_length_to_length_ratio=0.4
            )
            arrows.append(arrow)
    icons = [blocks[0]]
    for i in range(1, num_blocks):
        icons.append(arrows[i-1])
        icons.append(blocks[i])
    return VGroup(*icons)

class VideoScene(Scene):
    def construct(self):
        # 1. Show headline text
        text = Text(
            "Imagine a world where digital transactions happen without a bank’s oversight",
            font_size=38,
            t2c={
                "digital transactions": YELLOW,
                "without a bank’s oversight": RED_E
            },
            line_spacing=1.2
        ).to_edge(UP)

        self.play(Write(text), run_time=1.0)

        # 2. Visual: Bank icon fading out, blockchain icon appearing
        bank_icon = create_bank_icon().scale(0.95).next_to(text, DOWN, buff=0.8)
        blockchain_icon = create_blockchain_icon(num_blocks=4).scale(0.95).next_to(text, DOWN, buff=0.8)
        blockchain_icon.set_opacity(0)

        self.play(FadeIn(bank_icon, shift=DOWN), run_time=0.5)
        self.wait(0.3)
        self.play(
            FadeOut(bank_icon, shift=DOWN),
            blockchain_icon.animate.set_opacity(1),
            run_time=0.8
        )
        self.wait(0.4)

        # Animate transaction dots moving along the blockchain
        dots = []
        for i in range(4):
            dot = Dot(point=blockchain_icon[2*i].get_center(), color=YELLOW, radius=0.09)
            dots.append(dot)
            self.add(dot)
        # Animate the dots moving right to symbolize transaction transfer
        anims = [dot.animate.shift(RIGHT*0.7) for dot in dots[:-1]]
        self.play(*anims, run_time=0.6)

        # Wait briefly before fade out
        self.wait(0.2)
        self.play(FadeOut(text), FadeOut(blockchain_icon), *[FadeOut(dot) for dot in dots], run_time=0.3)
        # Scene total ≈ 3 seconds

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause