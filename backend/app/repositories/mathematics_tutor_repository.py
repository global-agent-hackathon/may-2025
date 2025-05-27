from typing import Dict, List, Any


class MathematicsTutorRepository:
    """
    Repository containing mathematical concepts, formulas, problem-solving strategies, and common mistakes.

    This repository serves as a static knowledge base for various mathematical domains such as algebra, geometry,
    calculus, and statistics. It provides a structured collection of topics that can be used for educational purposes.
    """

    def __init__(self) -> None:
        """
        Initialize the MathematicsTutorRepository with a predefined knowledge base.

        The knowledge base is organized into sections such as algebra, geometry, calculus, and statistics,
        each containing relevant concepts and formulas.
        """
        self.math_knowledge: Dict[str, Any] = {
            "algebra": {
                "concepts": [
                    "Variables and expressions",
                    "Equations and inequalities",
                    "Functions and relations",
                    "Polynomials",
                    "Factoring",
                    "Quadratic equations",
                ],
                "formulas": [
                    "Quadratic formula: x = (-b ± √(b² - 4ac)) / 2a",
                    "Difference of squares: a² - b² = (a+b)(a-b)",
                    "Perfect square trinomial: a² + 2ab + b² = (a+b)²",
                ],
            },
            "geometry": {
                "concepts": [
                    "Points, lines, and angles",
                    "Triangles and polygons",
                    "Circles and ellipses",
                    "Area and perimeter",
                    "Volume and surface area",
                    "Coordinate geometry",
                ],
                "formulas": [
                    "Circle area: A = πr²",
                    "Triangle area: A = ½bh",
                    "Pythagorean theorem: a² + b² = c²",
                ],
            },
            "calculus": {
                "concepts": [
                    "Limits and continuity",
                    "Derivatives",
                    "Integration",
                    "Differential equations",
                    "Series and sequences",
                    "Multivariable calculus",
                ],
                "formulas": [
                    "Power rule: d/dx(x^n) = nx^(n-1)",
                    "Product rule: d/dx(uv) = u(dv/dx) + v(du/dx)",
                    "Chain rule: d/dx(f(g(x))) = f'(g(x))g'(x)",
                ],
            },
            "statistics": {
                "concepts": [
                    "Probability",
                    "Descriptive statistics",
                    "Inferential statistics",
                    "Hypothesis testing",
                    "Regression analysis",
                    "Probability distributions",
                ],
                "formulas": [
                    "Mean: μ = Σx/n",
                    "Standard deviation: σ = √(Σ(x-μ)²/n)",
                    "Normal distribution: f(x) = (1/(σ√(2π)))e^(-(x-μ)²/(2σ²))",
                ],
            },
            "problem_solving_strategies": [
                "Break down complex problems into smaller parts",
                "Draw diagrams or visual representations",
                "Look for patterns and relationships",
                "Work backwards from the solution",
                "Use known formulas and theorems",
                "Check answers for reasonableness",
            ],
            "common_mistakes": [
                "Sign errors in calculations",
                "Order of operations mistakes",
                "Incorrect application of formulas",
                "Forgetting to check domain restrictions",
                "Unit conversion errors",
                "Arithmetic calculation errors",
            ],
            "visualization_tips": [
                "Use graphs to understand functions",
                "Draw geometric figures to scale",
                "Create tables for organizing data",
                "Use number lines for inequalities",
                "Sketch diagrams for word problems",
            ],
        }
