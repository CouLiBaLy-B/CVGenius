from pdfminer.high_level import extract_text
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file at the given path.

    Args:
        pdf_path (str): Path to the PDF file to be extracted.

    Returns:
        str: The extracted text from the PDF file.
    """
    return extract_text(pdf_path)


def generate_pdf(text):
    """Generate a PDF from a given text.

    Args:
        text (str): The text to be turned into a PDF.

    Returns:
        BytesIO: A BytesIO object containing the generated PDF.
    """
    styles = getSampleStyleSheet()
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []
    for line in text.split('\n'):
        elements.append(Paragraph(line, styles['BodyText']))
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer


class ModelError(Exception):
    pass
