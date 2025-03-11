from markdown_pdf import MarkdownPdf, Section
import os

def store_pdf(text, id):
  pdf = MarkdownPdf(toc_level=3)
  pdf.add_section(Section(text, toc=False))
  path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'public', 'output', str(id), 'systematic_review.pdf'))
  os.makedirs(os.path.dirname(path), exist_ok=True)
  pdf.save(path)