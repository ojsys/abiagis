from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from io import BytesIO

def create_pdf(file_path):
    # Create the PDF document
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    # Create a list to store PDF elements
    elements = []

    # Define styles for the paragraphs
    styles = getSampleStyleSheet()

    # Add a rotated paragraph
    rotated_text = "This is rotated text."
    paragraph_style = styles['Normal']

    # Set the rotation angle and position
    angle = 45
    x, y = 100, 500

    # Build the PDF document
    pdf.build(elements, onFirstPage=lambda canvas, doc: draw_rotated_text(canvas, rotated_text, paragraph_style, x, y, angle))

    # Save the PDF to a file or return it as needed
    with open(file_path, 'wb') as file:
        file.write(pdf_buffer.getvalue())

# Function to draw rotated text on the canvas
def draw_rotated_text(canvas, text, style, x, y, angle):
    canvas.saveState()
    canvas.rotate(angle)
    canvas.setFont(style.fontName, style.fontSize)
    canvas.drawText(x, y, text)
    canvas.restoreState()

# Example usage
create_pdf("rotated_paragraph.pdf")
