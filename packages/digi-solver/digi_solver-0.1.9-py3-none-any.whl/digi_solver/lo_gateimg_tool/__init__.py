"""
Sub-package for Logic Gate Image Generation utilities.

This sub-package includes tools for:
1. Generating K-maps and their LaTeX representations from minterms/don\'t cares.
2. Generating LaTeX representations of logic circuits from Boolean expressions.
"""

from typing import List

# Re-export key K-map functionalities (optional, for convenience)
from .kmap import (
    parse_groups,
    generate_kmap,
    kmap_to_latex,
    get_cell_positions,
    generate_tikz_code as generate_kmap_tikz_code,
    kmap_to_tikz_latex as generate_kmap_with_tikz_groups,
    generate_latex as generate_kmap_solution_latex,
    create_full_latex_document as create_kmap_latex_document
)

# Circuit generation functionality
from .digicircuit.boolean_to_circuit import generate_circuits_from_file_content


def generate_logic_diagrams(input_file_path: str, output_dir: str, scale: float = 1.0) -> List[str]:
    """
    Reads Boolean expressions from an input text file, generates LaTeX 
    source files for the corresponding logic circuit diagrams, and saves them 
    to the specified output directory.

    Each line in the input file should be a Boolean expression. 
    Lines can optionally start with a number followed by a space (e.g., "1. f = A+B"),
    which will be stripped before processing.

    Args:
        input_file_path: Path to the input file (e.g., data.txt).
        output_dir: Directory where the generated .tex files will be saved.
        scale: Scale factor for the circuit diagrams in the LaTeX output.

    Returns:
        A list of absolute paths to the generated .tex files.
        Returns an empty list if errors occur or no files are generated.
    """
    return generate_circuits_from_file_content(
        input_file_path=input_file_path, 
        output_dir=output_dir, 
        scale=scale
    )

__all__ = [
    # K-map functions
    'parse_groups',
    'generate_kmap',
    'kmap_to_latex',
    'get_cell_positions',
    'generate_kmap_tikz_code',
    'generate_kmap_with_tikz_groups',
    'generate_kmap_solution_latex',
    'create_kmap_latex_document',
    # Circuit generation functions
    'generate_logic_diagrams'
] 