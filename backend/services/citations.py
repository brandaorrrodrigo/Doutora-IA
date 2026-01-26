"""
Citation management for legal documents
"""
from typing import List, Dict, Tuple
import re


class CitationManager:
    """Manages citations in legal documents with numbering and bibliography"""

    def __init__(self):
        self.citations = []
        self.citation_map = {}  # Map citation_id to number

    def add_citation(self, citation: Dict) -> int:
        """
        Add a citation and return its number

        Args:
            citation: Dict with citation data (id, tipo, titulo, texto, etc)

        Returns:
            Citation number (1-indexed)
        """
        citation_id = citation.get("id", "")

        # Check if already added
        if citation_id in self.citation_map:
            return self.citation_map[citation_id]

        # Add new citation
        number = len(self.citations) + 1
        self.citations.append(citation)
        self.citation_map[citation_id] = number

        return number

    def add_citations(self, citations: List[Dict]) -> List[int]:
        """Add multiple citations and return their numbers"""
        numbers = []
        for citation in citations:
            number = self.add_citation(citation)
            numbers.append(number)
        return numbers

    def get_citation_reference(self, citation_id: str) -> str:
        """Get formatted reference for a citation"""
        number = self.citation_map.get(citation_id, 0)
        return f"[{number}]" if number else ""

    def get_numbered_citations(self) -> List[Tuple[int, Dict]]:
        """Get all citations with their numbers"""
        return [(i + 1, cit) for i, cit in enumerate(self.citations)]

    def format_bibliography(self) -> str:
        """
        Format all citations as a bibliography section

        Returns:
            Formatted bibliography string
        """
        if not self.citations:
            return ""

        bib_lines = ["REFERÊNCIAS\n"]

        for i, citation in enumerate(self.citations):
            number = i + 1
            tipo = citation.get("tipo", "").upper()
            titulo = citation.get("titulo", "")
            orgao = citation.get("orgao", "")
            tribunal = citation.get("tribunal", "")
            data = citation.get("data", "")
            fonte_url = citation.get("fonte_url", "")

            # Format based on type
            if tipo == "LEI":
                bib_entry = f"[{number}] {titulo}. {orgao}. {data}."
            elif tipo == "SUMULA":
                bib_entry = f"[{number}] {titulo}. {tribunal}. {data}."
            elif tipo == "JURIS":
                numero = citation.get("numero", "")
                classe = citation.get("classe", "")
                bib_entry = f"[{number}] {tribunal}. {classe} {numero}. {data}."
            elif tipo == "REGULATORIO":
                bib_entry = f"[{number}] {titulo}. {orgao}. {data}."
            elif tipo == "DOUTRINA":
                bib_entry = f"[{number}] {titulo}."
            else:
                bib_entry = f"[{number}] {titulo}."

            # Add URL if available
            if fonte_url:
                bib_entry += f" Disponível em: {fonte_url}"

            bib_lines.append(bib_entry)

        return "\n".join(bib_lines)

    def format_footnotes(self) -> List[str]:
        """
        Format citations as footnotes

        Returns:
            List of formatted footnotes
        """
        footnotes = []

        for i, citation in enumerate(self.citations):
            number = i + 1
            tipo = citation.get("tipo", "").upper()
            titulo = citation.get("titulo", "")
            texto = citation.get("texto", "")[:200]  # Limit to 200 chars

            footnote = f"{number}. {titulo} - {texto}..."
            footnotes.append(footnote)

        return footnotes

    def insert_citations_in_text(self, text: str, citations: List[Dict]) -> str:
        """
        Insert citation numbers in text where citations are referenced

        This looks for citation titles or IDs in the text and replaces them with [N]

        Args:
            text: Text to process
            citations: List of citations to reference

        Returns:
            Text with citation numbers inserted
        """
        processed_text = text

        # Add citations to manager
        for citation in citations:
            number = self.add_citation(citation)
            titulo = citation.get("titulo", "")

            # Try to find references to this citation in text
            # Replace "Art. X da Lei Y" with "Art. X da Lei Y [N]"
            if titulo:
                # Escape special regex characters
                titulo_escaped = re.escape(titulo)
                pattern = f"({titulo_escaped})(?!\\s*\\[\\d+\\])"  # Don't replace if already numbered
                replacement = f"\\1 [{number}]"
                processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)

        return processed_text

    def get_citation_by_number(self, number: int) -> Dict:
        """Get citation by its number"""
        if 1 <= number <= len(self.citations):
            return self.citations[number - 1]
        return {}

    def clear(self):
        """Clear all citations"""
        self.citations = []
        self.citation_map = {}

    def get_summary(self) -> Dict:
        """Get summary of citations by type"""
        summary = {
            "total": len(self.citations),
            "by_type": {}
        }

        for citation in self.citations:
            tipo = citation.get("tipo", "unknown")
            summary["by_type"][tipo] = summary["by_type"].get(tipo, 0) + 1

        return summary
