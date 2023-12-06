from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

from coapp.models import Parcel, Lines


def create_pdf():
    parcels = Parcel.objects.all()
    text = "Hello, I am a PDF document"
    c = canvas.Canvas("simple_pdf.pdf", pagesize=letter)
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 20)
    c.drawString(30, 750, text)

    text2 = "In this tutorial, we will demonstrate how to create a PDF document using Python and ReportLab."
    c.setFillColor(colors.blue)
    c.setFont("Helvetica", 12)
    c.drawString(30, 730, text2)

    pdfmetrics.registerFont(TTFont('Playbill', 'Playbill.ttf'))
    text3 = "ABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IA GISA BIAG IS ABIA GISAB IA GISA BIAGIS ABIAG ISAB IS"
    c.setFillColor(colors.black)
    c.setFont("Playbill", 1)
    content = c.beginText()
    content.setTextOrigin(30, 710)
    content.setCharSpace(0.1)
    content.textLines(text3)

    c.drawText(content)

    c.save()


if __name__ == "__main__":
    create_pdf()