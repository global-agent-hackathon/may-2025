from manim import *

def create_ledger_icon():
    return Rectangle(width=1.5, height=2, color=BLUE).add(Text("Ledger", font_size=24).move_to(
        np.array([0, 0, 0])))

def create_blockchain_icon():
    block = Rectangle(width=1, height=0.5, color=YELLOW)
    link = Line(LEFT, RIGHT, color=GREEN)
    blockchain = VGroup(*[block.copy().shift(RIGHT*i) for i in range(3)], *[link.copy().shift(RIGHT*i + RIGHT*0.5) for i in range(2)])
    return blockchain

class BlockchainExplainer(Scene):
    def construct(self):
        self.introduction_scene()
        self.anatomy_of_a_block_scene()
        self.chains_and_security_scene()
        self.decentralization_scene()

    def introduction_scene(self):
        # Introduction to Blockchain
        ledger = create_ledger_icon()  # Create a digital ledger icon
        people = [Circle(radius=0.2, color=BLUE).shift(RIGHT*i) for i in range(-2, 3, 2)]
        ledger.move_to(people[0])
        people_group = VGroup(*people)

        self.play(Write(people_group)) # Show people
        self.play(FadeIn(ledger)) # Show the ledger
        self.wait(1)
        for i in range(len(people) - 1):
            self.play(ledger.animate.move_to(people[i + 1].get_center()), run_time=0.8) # Pass ledger
        self.wait(2)

    def anatomy_of_a_block_scene(self):
        # Anatomy of a Block
        block_data = Rectangle(width=2, height=1, color=BLUE).add(Text("Data", font_size=24).move_to(ORIGIN))
        block_hash = Rectangle(width=2, height=1, color=YELLOW).add(Text("Hash", font_size=24).move_to(ORIGIN))
        block_prev_hash = Rectangle(width=2, height=1, color=GREEN).add(Text("Prev. Hash", font_size=24).move_to(ORIGIN))

        block = VGroup(block_data, block_hash, block_prev_hash).arrange(DOWN, buff=0.2)

        train = VGroup()
        for _ in range(3):
            train.add(block.copy().shift(RIGHT * len(train) * 3))
        train.arrange(RIGHT, buff=0.5)

        self.play(FadeIn(train))
        self.wait(2)

    def chains_and_security_scene(self):
        # Chains and Security
        original_chain = create_blockchain_icon().to_edge(LEFT)
        altered_block = Rectangle(width=1, height=0.5, color=RED)

        self.play(Write(original_chain))
        self.wait(1)
        self.play(Transform(original_chain[1].copy(), altered_block), run_time=2)
        alert = Text("REJECTED!", color=RED).next_to(altered_block, UP)
        self.play(Write(alert))
        self.wait(2)

    def decentralization_scene(self):
        # Decentralization: The Core
        documents = [Rectangle(width=1.5, height=1, color=GREEN).add(Text("Copy", font_size=24).move_to(ORIGIN)) for _ in range(6)]
        participants = [Circle(radius=0.2, color=BLUE) for _ in range(6)]
        positions = [ORIGIN + 2*RIGHT*i for i in range(-3, 3)]

        for i, doc in enumerate(documents):
            doc.move_to(positions[i])
            participants[i].move_to(positions[i] + DOWN)

        doc_group = VGroup(*documents)
        participants_group = VGroup(*participants)

        self.play(Write(participants_group))
        self.wait(1)
        self.play(FadeIn(doc_group))
        self.wait(2)