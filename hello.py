from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

my_path = '/Users/mac/Documents/ABIAProject/hello.pdf'

c = canvas.Canvas(my_path, pagesize=letter, bottomup=0)
c.setFont("Helvetica", 28)
c.drawString(30, 50, "Hello World!")
c.showPage()
c.save()