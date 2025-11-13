"""
Rowan v2 API: MSA (Multiple Sequence Alignment) Workflow
Generate multiple sequence alignments for protein sequences.
"""

from typing import Annotated
import rowan
import json


def submit_msa_workflow(
    initial_protein_sequences: Annotated[str, "JSON string list of protein sequences (e.g., '[\"MKLLV...\", \"MAHQR...\"]')"],
    output_formats: Annotated[str, "JSON string list of output formats (e.g., '[\"a3m\", \"sto\"]')"],
    name: Annotated[str, "Workflow name for identification and tracking"] = "MSA Workflow",
    folder_uuid: Annotated[str, "UUID of folder to organize this workflow. Empty string uses default folder"] = "",
    max_credits: Annotated[int, "Maximum credits to spend on this calculation. 0 for no limit"] = 0
):
    """Submit a multiple sequence alignment (MSA) workflow using Rowan v2 API.

    Args:
        initial_protein_sequences: JSON string list of protein sequences (amino acid strings)
        output_formats: JSON string list of desired output formats (e.g., '["a3m", "sto", "fas"]')
        name: Workflow name for identification and tracking
        folder_uuid: UUID of folder to organize this workflow. Empty string uses default folder.
        max_credits: Maximum credits to spend on this calculation. 0 for no limit.

    Generates multiple sequence alignments for protein sequences using advanced
    alignment algorithms. Useful for:
    - Protein structure prediction
    - Evolutionary analysis
    - Homology modeling
    - Coevolution studies

    Common output formats:
    - 'a3m': A3M format (used by HHpred, HHblits)
    - 'sto': Stockholm format (used by Pfam)
    - 'fas': FASTA format
    - 'a2m': A2M format

    Returns:
        Workflow object representing the submitted workflow

    Examples:
        # Single protein sequence alignment
        result = submit_msa_workflow(
            initial_protein_sequences='["MKLLVLGLLLAAAVPGTRAAQMSFKLIGTEYFTLQIRGRERFEMFRELN"]',
            output_formats='["a3m", "sto"]',
            name="Insulin MSA"
        )

        # Multiple protein sequences
        result = submit_msa_workflow(
            initial_protein_sequences='["MKTAYIAKQRQISFVKSHFSRQ", "MKTAYIAKQRQISFVKSHF"]',
            output_formats='["a3m", "fas"]',
            name="Multi-protein MSA"
        )

        # Full format output
        result = submit_msa_workflow(
            initial_protein_sequences='["GSTLGRIADRDLLELDTLAAKVPSDGAKDLVTDIVNRQIYDG"]',
            output_formats='["a3m", "sto", "fas", "a2m"]',
            name="Complete MSA Output"
        )

    This workflow can take 10-30 minutes depending on sequence length.
    """

    # Parse initial_protein_sequences (always a string in MCP)
    try:
        parsed_sequences = json.loads(initial_protein_sequences)
    except (json.JSONDecodeError, ValueError):
        # Try comma-separated
        if ',' in initial_protein_sequences:
            parsed_sequences = [s.strip() for s in initial_protein_sequences.split(',') if s.strip()]
        else:
            parsed_sequences = [initial_protein_sequences.strip()]

    # Parse output_formats
    try:
        parsed_formats = json.loads(output_formats)
    except (json.JSONDecodeError, ValueError):
        # Try comma-separated
        if ',' in output_formats:
            parsed_formats = [f.strip() for f in output_formats.split(',') if f.strip()]
        else:
            parsed_formats = [output_formats.strip()]

    result = rowan.submit_msa_workflow(
        initial_protein_sequences=parsed_sequences,
        output_formats=parsed_formats,
        name=name,
        folder_uuid=folder_uuid if folder_uuid else None,
        max_credits=max_credits if max_credits > 0 else None
    )

    # Make workflow publicly viewable
    result.update(public=True)

    return result
