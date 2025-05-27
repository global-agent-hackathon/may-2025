from typing import List
from agno.utils.log import logger


class ChemistryTutorRepository:
    """
    Repository for storing and searching basic chemistry knowledge.

    This class provides a simple, keyword-based search on a predefined
    list of fundamental chemistry concepts and explanations.
    """

    def __init__(self) -> None:
        """
        Initialize the repository with a predefined chemistry knowledge base.
        """
        self.chemistry_knowledge: List[str] = [
            # Basic Chemistry Concepts
            "Atomic Structure: Atoms are composed of protons, neutrons, and electrons. The nucleus contains protons and neutrons, while electrons orbit around the nucleus.",
            "Periodic Table: Elements are arranged in order of increasing atomic number. The table shows periodic trends in properties like atomic radius, electronegativity, and ionization energy.",
            "Chemical Bonding: Atoms form bonds to achieve stable electron configurations. Types include ionic, covalent, and metallic bonds.",
            # Chemical Reactions
            "Types of Reactions: Synthesis, decomposition, single replacement, double replacement, and combustion reactions.",
            "Balancing Equations: Conservation of mass requires equal numbers of atoms on both sides of a chemical equation.",
            "Reaction Rates: Factors affecting reaction rates include temperature, concentration, surface area, and catalysts.",
            # States of Matter
            "Gas Laws: Boyle's Law, Charles's Law, and the Ideal Gas Law describe the behavior of gases.",
            "Phase Changes: Melting, freezing, vaporization, condensation, sublimation, and deposition.",
            "Solutions: Homogeneous mixtures where solute particles are evenly distributed in a solvent.",
            # Acids and Bases
            "pH Scale: Measures acidity or basicity of a solution, ranging from 0 (acidic) to 14 (basic).",
            "Acid-Base Reactions: Acids donate protons (H+), bases accept protons. Neutralization reactions produce water and salt.",
            "Buffers: Solutions that resist changes in pH when small amounts of acid or base are added.",
            # Organic Chemistry
            "Hydrocarbons: Compounds containing only carbon and hydrogen. Types include alkanes, alkenes, and alkynes.",
            "Functional Groups: Specific groups of atoms that determine the chemical properties of organic compounds.",
            "Isomerism: Different compounds with the same molecular formula but different structures.",
            # Thermodynamics
            "Enthalpy: Heat content of a system. Exothermic reactions release heat, endothermic reactions absorb heat.",
            "Entropy: Measure of disorder in a system. Spontaneous processes tend to increase entropy.",
            "Gibbs Free Energy: Predicts whether a reaction will be spontaneous at constant temperature and pressure.",
            # Electrochemistry
            "Redox Reactions: Involve transfer of electrons between species. Oxidation is loss of electrons, reduction is gain.",
            "Electrochemical Cells: Convert chemical energy to electrical energy (galvanic cells) or vice versa (electrolytic cells).",
            "Standard Reduction Potentials: Measure the tendency of a species to be reduced.",
            # Kinetics
            "Reaction Mechanisms: Step-by-step sequence of elementary reactions that make up the overall reaction.",
            "Rate Laws: Mathematical expressions showing how reaction rate depends on reactant concentrations.",
            "Catalysis: Process of increasing reaction rate without being consumed in the reaction.",
            # Nuclear Chemistry
            "Radioactivity: Spontaneous emission of radiation from unstable atomic nuclei.",
            "Nuclear Reactions: Processes that change the composition of atomic nuclei.",
            "Half-life: Time required for half of a radioactive sample to decay.",
        ]

    def search_knowledge(self, query: str) -> List[str]:
        """
        Search the chemistry knowledge base for concepts matching a query.

        This performs a simple case-insensitive substring search.

        Args:
            query (str): A keyword or phrase to search within the knowledge base.

        Returns:
            List[str]: A list of matching entries from the knowledge base.
                       If no matches are found, returns an empty list.
        """
        try:
            query = query.lower()
            return [
                knowledge
                for knowledge in self.chemistry_knowledge
                if query in knowledge.lower()
            ]
        except Exception as e:
            logger.error(f"Error in search_knowledge: {str(e)}")
            return []
