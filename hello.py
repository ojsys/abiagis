from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from coapp.models import Parcel, Lines
from datetime import datetime

def generate_pdf_with_reportlab(file_path, parcel_id, data):
    parcels = Parcel.objects.filter(id=parcel_id)
    parcel_line_id = parcels.values_list('OBJECTID', flat=True)
    lines = Lines.objects.filter(ParcelID_id__in=parcel_line_id)
    time = datetime.now().strftime("%I:%M:%S %p, %A, %B %d, %Y")

    # Create a PDF document using reportlab
    pdf_canvas = canvas.Canvas(file_path)

    # Set the font and font size
    pdf_canvas.setFont("Helvetica", 16)


    for parcel in parcels:    # Add data using reportlab
        pdf_canvas.drawString(30, 800, "FILENO: " + parcel.FileNumber)
        pdf_canvas.drawString(30, 780, "PLOT DESCRIPTION" + parcel.Plot_No + " " + parcel.Address)
        pdf_canvas.drawString(30, 760, "LGA: " + parcel.LGA)
        pdf_canvas.drawString(30, 740, "SURVEY PLAN NUMBER: " + parcel.Plan_No)
        for line in lines:
            if line.ParcelID_id == parcel.OBJECTID:
                pdf_canvas.drawString(30, 720, "LINE: " + line.Line)
        

    pdf_canvas.save()

def generate_pdf_with_xhtml2pdf(file_path, html_content):
    # Convert HTML to PDF using xhtml2pdf
    with open(file_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)

# Example data
my_data = [
    {"name": "Name", "value": "John Doe"},
    {"name": "Age", "value": "30"},
    {"name": "Occupation", "value": "Engineer"},
]

# Example HTML content (replace this with your actual HTML)
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>HTML to PDF</title>
</head>
<body>
    <h1>Hello, world!</h1>
    <p>This is an example of combining xhtml2pdf and reportlab.</p>
</body>
</html>
"""

# Output file paths
pdf_file_path_reportlab = "output_reportlab.pdf"
pdf_file_path_xhtml2pdf = "output_xhtml2pdf.pdf"

# Generate PDF using reportlab
generate_pdf_with_reportlab(pdf_file_path_reportlab, my_data)

# Generate PDF using xhtml2pdf
generate_pdf_with_xhtml2pdf(pdf_file_path_xhtml2pdf, html_content)
