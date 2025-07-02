from manim import *

class VideoScene(Scene):
    def construct(self):
        # Create text related to blockchain topic
        text = Text(
            "And cryptography—the math behind secret codes—locks the connections between blocks,\nmaking tampering nearly impossible",
            font_size=36
        )

        # Illustrate the connection with geometric shapes
        block_1 = Square(side_length=1, fill_color=BLUE, fill_opacity=0.5)
        block_2 = Square(side_length=1, fill_color=GREEN, fill_opacity=0.5)
        connection = Line(block_1.get_right(), block_2.get_left(), stroke_width=6, color=YELLOW)

        # Position the blocks
        block_1.shift(LEFT * 2 + UP * 0.5)
        block_2.next_to(block_1, RIGHT, buff=0.7)

        # Group blocks and connection
        blockchain_group = VGroup(block_1, block_2, connection)

        # Animate blockchain visualization
        self.play(Create(blockchain_group))
        self.wait(0.5)

        # Display text
        self.play(Write(text))
        self.wait(2)

        # Fade out everything
        self.play(FadeOut(blockchain_group), FadeOut(text))

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause