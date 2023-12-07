from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def rotate_text(canvas):
    canvas.saveState()
    canvas.rotate(90)
    ptext = "Rotated Text"
    styles = getSampleStyleSheet()
    p = Paragraph(ptext, styles['BodyText'])
    p.wrapOn(canvas, 100, 500)
    p.drawOn(canvas, -100, 0)
    canvas.restoreState()

def generate_pdf():
    # doc = SimpleDocTemplate("rotate_text.pdf", pagesize=letter)
    # elements = []

    c = canvas.Canvas("rotate_text.pdf", pagesize=letter)
    rotate_text(c)
    c.showPage()
    c.save()

generate_pdf()