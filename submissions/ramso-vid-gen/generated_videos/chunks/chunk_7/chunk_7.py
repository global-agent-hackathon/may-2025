from manim import *

from manim import Scene, Text, VGroup, FadeIn, FadeOut, Create, UP, DOWN, LEFT, RIGHT, GREEN, BLUE, YELLOW, Line, Arrow, Circle, Square

class VideoScene(Scene):
    def construct(self):
        # Title of the scene
        title = Text("Blockchain Technology", font_size=48, color=BLUE)
        title.to_edge(UP)
        
        # Main text content
        content_text = Text("To alter a record, you’d need to change not just one page,", font_size=24)
        content_text.to_edge(UP)
        content_text.shift(DOWN)

        content_text2 = Text("but every copy on every computer at once", font_size=24)
        content_text2.next_to(content_text, DOWN)

        # Computer representation as squares
        computers = VGroup(
            Square().scale(0.5),
            Square().scale(0.5),
            Square().scale(0.5),
        ).arrange(RIGHT, buff=1.5).shift(2*DOWN)

        # Arrows representing connections between computers
        connections = VGroup(
            Arrow(computers[0].get_center() + UP*0.5, computers[1].get_center() + UP*0.5, buff=0.3),
            Arrow(computers[1].get_center() + UP*0.5, computers[2].get_center() + UP*0.5, buff=0.3)
        )

        # Blockchain icon - A chain of circles representing blocks
        blockchain = VGroup(*[Circle(radius=0.2, color=GREEN).shift(i*RIGHT*0.4) for i in range(5)])
        blockchain.move_to(computers[1]).shift(UP*1.5)

        # Animations
        self.play(FadeIn(title))
        self.wait(0.5)
        self.play(Write(content_text))
        self.play(Write(content_text2))
        self.play(Create(computers), Create(connections))
        self.play(Create(blockchain))

        # Represent the change in all computers by flashing
        self.play(computers.animate.set_fill(YELLOW, opacity=0.5), run_time=0.5)
        self.play(computers.animate.set_fill(GREEN, opacity=0.5), run_time=0.5)
        
        # Pause for viewers to absorb the information
        self.wait(1)

        # Fade out everything at the end
        self.play(FadeOut(VGroup(title, content_text, content_text2, computers, connections, blockchain)))

        # Total pause to ensure the animation lasts approximately 3 seconds
        self.wait(0.5)

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause