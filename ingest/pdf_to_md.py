"""
Convert PDF legal documents to markdown
"""
import os
import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    text_content = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)

    return "\n\n".join(text_content)


def pdf_to_markdown(pdf_path: str, output_path: str = None):
    """
    Convert PDF to markdown

    Args:
        pdf_path: Path to PDF file
        output_path: Optional output path for markdown file
    """
    # Extract text
    text = extract_text_from_pdf(pdf_path)

    # Determine output path
    if output_path is None:
        output_path = pdf_path.replace(".pdf", ".md")

    # Write markdown
    with open(output_path, "w", encoding="utf-8") as f:
        # Add metadata header
        f.write("---\n")
        f.write(f"source: {os.path.basename(pdf_path)}\n")
        f.write("type: legal_document\n")
        f.write("---\n\n")

        # Add content
        f.write(text)

    print(f"✓ Converted {pdf_path} to {output_path}")
    return output_path


def batch_convert_pdfs(input_dir: str, output_dir: str = None):
    """
    Convert all PDFs in a directory to markdown

    Args:
        input_dir: Directory containing PDF files
        output_dir: Optional output directory for markdown files
    """
    if output_dir is None:
        output_dir = input_dir

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all PDFs
    pdf_files = list(Path(input_dir).glob("**/*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")

    # Convert each PDF
    for pdf_path in pdf_files:
        try:
            output_path = os.path.join(
                output_dir,
                pdf_path.stem + ".md"
            )
            pdf_to_markdown(str(pdf_path), output_path)
        except Exception as e:
            print(f"✗ Error converting {pdf_path}: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_to_md.py <pdf_file_or_directory>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        pdf_to_markdown(path)
    elif os.path.isdir(path):
        batch_convert_pdfs(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)
