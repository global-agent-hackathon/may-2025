from manim import *

# Helper function for emojized text
def emojized_text(text, font_size=36, color=WHITE):
    return Text(text, font_size=font_size, color=color)

# Blockchain icon built from rectangles and lines
def create_blockchain_icon(scale=1.0):
    block1 = Square(side_length=0.5*scale, color=BLUE, fill_opacity=0.4)
    block2 = Square(side_length=0.5*scale, color=YELLOW, fill_opacity=0.4).shift(RIGHT*0.7*scale)
    block3 = Square(side_length=0.5*scale, color=GREEN, fill_opacity=0.4).shift(RIGHT*1.4*scale)
    link1 = Line(block1.get_right(), block2.get_left(), color=GRAY)
    link2 = Line(block2.get_right(), block3.get_left(), color=GRAY)
    return VGroup(block1, block2, block3, link1, link2)

# Lock icon for security, built from shapes
def create_lock_icon():
    lock_body = Rectangle(width=0.36, height=0.36, color=WHITE, fill_opacity=1, fill_color=GREEN_C).shift(DOWN*0.07)
    lock_shackle = Arc(radius=0.18, start_angle=PI, angle=PI, color=WHITE).shift(UP*0.14)
    keyhole = Dot(radius=0.055, color=BLACK).shift(DOWN*0.07)
    return VGroup(lock_body, lock_shackle, keyhole)

# Eye icon for transparency, built from shapes
def create_eye_icon():
    eye_outline = Ellipse(width=0.4, height=0.18, color=YELLOW)
    pupil = Dot(radius=0.066, color=YELLOW).shift(RIGHT*0)
    return VGroup(eye_outline, pupil)

class VideoScene(Scene):
    def construct(self):
        # Main blockchain icon
        blockchain_icon = create_blockchain_icon(scale=1.05).to_edge(UP).shift(DOWN*0.3)
        
        # Security icons
        lock_icon = create_lock_icon().scale(0.66).next_to(blockchain_icon, LEFT, buff=0.2)
        eye_icon = create_eye_icon().scale(0.85).next_to(blockchain_icon, RIGHT, buff=0.22)
        
        # Main text
        content_text = Text(
            "Because it's decentralized and encrypted, blockchain is both secure and transparent, revolutionizing trust in digital spaces",
            font_size=34, color=WHITE, t2c={
                "decentralized": BLUE,
                "encrypted": BLUE_B,
                "secure": GREEN,
                "transparent": YELLOW_E,
                "trust": YELLOW
            }
        ).shift(DOWN*1)
        
        # Intro animations
        self.play(
            FadeIn(blockchain_icon, shift=UP, scale=0.8),
            FadeIn(lock_icon, shift=LEFT),
            FadeIn(eye_icon, shift=RIGHT),
            run_time=0.7
        )
        self.wait(0.2)
        
        # Fade in the text smoothly
        self.play(Write(content_text), run_time=1.4)
        
        # Emphasize security and transparency visually
        self.play(
            lock_icon.animate.set_fill(GREEN, opacity=0.7),
            eye_icon.animate.set_fill(YELLOW, opacity=0.6),
            run_time=0.4
        )
        self.wait(0.3)
        
        # Fade out everything smoothly
        self.play(
            FadeOut(blockchain_icon, shift=UP),
            FadeOut(lock_icon, shift=LEFT),
            FadeOut(eye_icon, shift=RIGHT),
            FadeOut(content_text, shift=DOWN),
            run_time=0.4
        )
        self.wait(0.1)

        # Ensure total duration is 3 seconds
        self.wait(0.5)  # Final pause