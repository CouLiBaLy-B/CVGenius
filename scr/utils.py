from pdfminer.high_level import extract_text
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def generate_pdf(text):
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
