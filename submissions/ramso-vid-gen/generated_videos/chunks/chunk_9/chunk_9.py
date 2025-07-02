from manim import *

class VideoScene(Scene):
    def create_computer_icon(self):
        screen = Rectangle(width=1, height=0.6, color=BLUE)
        base = Rectangle(width=0.5, height=0.1).next_to(screen, DOWN, buff=0)
        return VGroup(screen, base)

    def construct(self):
        # Text introduction
        text = Text("So, a blockchain is a trustworthy system",
                    font_size=36, color=WHITE)
        text.to_edge(UP, buff=0.5)
        self.play(Write(text))
        
        # Visual representation using icons
        blockchain_icon = self.create_computer_icon().shift(LEFT * 2)
        computer_icon = self.create_computer_icon().shift(RIGHT * 2)
        
        math_text = MathTex("\\text{Math}")
        computer_text = MathTex("\\text{Computers}")

        # Arrange them at the center
        blockchain_icon.next_to(text, DOWN, buff=0.5)
        computer_icon.next_to(text, DOWN, buff=0.5)
        math_text.next_to(blockchain_icon, DOWN)
        computer_text.next_to(computer_icon, DOWN)

        # Display all elements
        self.play(FadeIn(blockchain_icon), FadeIn(computer_icon))
        self.play(Write(math_text), Write(computer_text))

        # Conclusion text
        conclusion_text = Text(
            "work together to keep everyone honest.", font_size=36, color=YELLOW
        )
        conclusion_text.next_to(math_text, DOWN, buff=0.8)
        self.play(Write(conclusion_text))
        
        self.wait(1)

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause