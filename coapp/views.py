from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views import View
from django.contrib.auth import get_user_model
from .models import Parcel, Lines
import io
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.template.loader import get_template
from django.template import Context

# reportlab
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image, Table, TableStyle, BaseDocTemplate, Frame
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch
# ---------
from .forms import ParcelSearchForm
from django.core.paginator import Paginator
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa





User = get_user_model()


def render_pdf_view(request, parcel_id):
    template_path = 'coapp/generatepdf.html'

    parcels = Parcel.objects.filter(id=parcel_id)
    parcel_line_id = parcels.values_list('OBJECTID', flat=True)
    lines = Lines.objects.filter(ParcelID_id__in=parcel_line_id)
    time = datetime.now().strftime("%I:%M:%S %p, %A, %B %d, %Y")
    

    context = {'parcels': parcels, 'lines':lines, 'time': time}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



@login_required
def index(request): 
    user = request.user
    parcels = Parcel.objects.all()
    lines = Lines.objects.all()

    commercial_land = 0
    residential_land = 0
    residential_commercial = 0
    public_land = 0
    agric_land = 0
    mixed_land = 0
    educational_land = 0

    # Count null values in Landuse
    field_name = 'Landuse'
    null_filter = Q(**{f"{field_name}__isnull": True})
    not_alloted = Parcel.objects.filter(null_filter).count()
    # End null filter

    for parcel in parcels:
        if parcel.Landuse == 'Commercial':
            commercial_land += 1
        elif parcel.Landuse == 'Residential':
            residential_land += 1
        elif parcel.Landuse == 'Residential/Commercial':
            residential_commercial += 1
        elif parcel.Landuse == 'Public':
            public_land += 1
        elif parcel.Landuse == 'Agricultural':
            agric_land += 1
        elif parcel.Landuse == 'Mixed':
            mixed_land += 1
        elif parcel.Landuse == 'Educational':
            educational_land += 1
        else:
            if parcel.Landuse == '':
                not_alloted += 1

    return render(request, 'coapp/index.html', {
        'title': 'ABIAGIS', 
        'user': user, 
        'parcels': parcels, 
        'lines': lines,
        'commercial_land':commercial_land,
        'residential_land':residential_land,
        'residential_commercial':residential_commercial,
        'public_land':public_land,
        'agric_land':agric_land,
        'mixed_land':mixed_land,
        'educational_land':educational_land,
        'not_allocated':not_alloted
    })



def search_page(request):
    # file_number = request.GET.get('file_number')    
    # paginate = Paginator(Parcel.objects.all(), 1)
    # page = request.GET.get('page')
    # parcels = paginate.get_page(page)
    # lands = Parcel.objects.all()
    # if file_number:
    #     lands = lands.filter(FileNumber__icontains=file_number)
    # context = {
    #     'form': ParcelSearchForm(),
    #     'parcels': parcels,
    #     'lines': Lines.objects.all(),
    #     'lands': lands
    # }    

    form = ParcelSearchForm(request.GET)
    parcels = []
    lines = []

    if form.is_valid():
        file_number = form.cleaned_data['file_number']
        parcels = Parcel.objects.filter(FileNumber__icontains=file_number)
        parcel_line_id = parcels.values_list('OBJECTID', flat=True)
        lines = Lines.objects.filter(ParcelID_id__in=parcel_line_id)
        

    context = {
        'form':form,
        'parcels': parcels,
        'lines':lines
    }
    return render(request, 'coapp/search_page.html', context)

    
def generate_pdf(request, parcel_id):
    parcel = Parcel.objects.get(pk=parcel_id)
    lines = Lines.objects.filter(ParcelID_id=parcel.OBJECTID)

    pdf_file_path_reportlab = "output_reportlab.pdf"
    pdf_file_path_xhtml2pdf = "output_xhtml2pdf.pdf"

    

    return render(request, 'coapp/generate_pdf.html', {'pdf_file_path_reportlab':pdf_file_path_reportlab, 'pdf_file_path_xhtml2pdf':pdf_file_path_xhtml2pdf})


class MyPDFView(View):
    def get(self, request, parcel_id, *args, **kwargs):
        # Retrieve data from the database
        pdfmetrics.registerFont(TTFont('Playbill', 'Playbill.ttf'))
        parcels = Parcel.objects.filter(id=parcel_id)
        lines = Lines.objects.filter(ParcelID_id__in=parcels.values_list('OBJECTID', flat=True))
        time = datetime.now().strftime("%I:%M:%S %p, %A, %B %d, %Y")

        # Create a buffer to store the PDF
        buffer = BytesIO()

        # Create the PDF object using the buffer
        pdf = Canvas(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=10, bottomMargin=0.5, allowSplitting=1, title="Parcel Fabric")
        #pdf = Canvas(buffer, pagesize=A4)
        # Create a list to store PDF elements
        elements = []

        # Define styles for the paragraphs
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='BodyText_CENTER', fontName='Playbill', fontSize=2, alignment=TA_CENTER, leading=16))
        styles.add(ParagraphStyle(name='BodyText_Survey', fontName='Helvetica', fontSize=12, alignment=TA_LEFT, leading=16))
        styles.add(ParagraphStyle(name='BodyText_Survey2', fontName='Helvetica', fontSize=12, alignment=TA_LEFT, leading=16))
        styles.add(ParagraphStyle(name='BodyText_Image', fontName='Helvetica', fontSize=12, alignment=TA_CENTER, leading=16))
        styles.add(ParagraphStyle(name='BodyText_Footer', fontName='Helvetica', fontSize=12, alignment=TA_CENTER, leading=16))
        styles.add(ParagraphStyle(name='BodyText_FileNumber', fontName='Helvetica', fontSize=12, alignment=TA_CENTER, leading=16, angle=90))
        # Iterate through the database records and add them to the PDF
        for parcel in parcels:
            # Customize this line based on your model fields
            file_number = f"<font name = 'Helvetica' size = '13'>FILENO: <b>{parcel.FileNumber}</b></font>"             # Create a paragraph with the data
            file_number_data = Paragraph(file_number, styles['BodyText'])
            elements.append(file_number_data)
            elements.append(Spacer(1, 9))
            #----
            plot_no = f"<font name = 'Helvetica' size = '12'>PLOT DESCRIPTION: <b>{parcel.Address}</b></font>"             # Create a paragraph with the data
            plot_no_data = Paragraph(plot_no, styles['BodyText'])
            elements.append(plot_no_data)
            elements.append(Spacer(1, 9))
            #----
            lga = f"<font name = 'Helvetica' size = '13'>LGA: <b>{parcel.LGA.upper()}</b></font>"             # Create a paragraph with the data
            lga_data = Paragraph(lga, styles['BodyText'])
            elements.append(lga_data)
            elements.append(Spacer(1, 9))
            #----
            plan_no = f"<font name = 'Helvetica' size = '13'>SURVEY PLAN NUMBER: <b>{parcel.Plan_No}</b></font>"             # Create a paragraph with the data
            plan_no_data = Paragraph(plan_no, styles['BodyText'])
            elements.append(plan_no_data)
            elements.append(Spacer(1, 9))
            
            #----
            for line in lines:
                if line.FromBeaconNo == parcel.Starting_Pillar_No:    
                    pillar_ref = f"<font name = 'Helvetica' size = '12'>REFERENCE PILLAR NO/ COORDINATES: <b>{parcel.Starting_Pillar_No} ({line.Eastings}E AND {line.Northings}N)</b></font>"             # Create a paragraph with the data
                    pillar_ref_data = Paragraph(pillar_ref, styles['BodyText'])
                    elements.append(pillar_ref_data)
                    elements.append(Spacer(1, 9))
            
            #----
            land_page_line = f"<font name = 'Playbill' size = '1.6'>ABIAG ISAB IA GISA BIAGISA BIAG ISAB IA GISA BIAGISA BIAG ISABIA GISAB IAGISA BIAG ISABIA GISAB IAGISA BIAG IS ABIAG ISAB IA GISA BIAGISA BIAG ISAB IA GISA BIAGISA BIAG ISABIA GISAB IAGISA BIAG ISABIA GISAB IAGISA BIAG IS ABIAG ISAB IA GISA BIAGISA ABIAG ISAB IA GISA BIAGISA BIAG ISAB IA GISA BIAGISA BIAG ISABIA GISAB IAGISA BIAG ISABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IA GISA BIAG IS ABIA GISAB IA GISA BIAGIS ABIAG ISAB IA GISA BIAGISA BIAG ISAB IA GISA BIAGISA BIAG ISAB IA GISAB IAGISA BIAG ISABIA GISAB IAGISA BIAG ISABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IAGISA BIAG IS ABIA GISAB IA GISA BIAG IS ABIA GISAB IA GISA BIAGIS ABIAG ISAB IS</font>"             # Create a paragraph with the data
            this_style = styles['Heading4']
            this_style.alignment = 1
            landpage_data = Paragraph(land_page_line, this_style)
            elements.append(landpage_data)
            elements.append(Spacer(1, -7))
            #----
            surveyor = "<font name = 'Helvetica' size = '11'><b>N. K. C. ABARAONYE</b></font>"
            sur_style = styles['BodyText_Survey']
            sur_style.leftIndent = -5
            surveyor_data = Paragraph(surveyor, sur_style)
            elements.append(surveyor_data)
            elements.append(Spacer(1, -5))
            #----
            surveyor_title = "<font name = 'Helvetica' size = '9'>SURVEYOR GENERAL</font>"
            sur_style2 = styles['BodyText_Survey2']
            sur_style2.leftIndent = -15
            surveyor_title_data = Paragraph(surveyor_title, sur_style2)
            elements.append(surveyor_title_data)

            #----
            file_number1 = f"<font name='Helvetica' size='11'><b>{parcel.FileNumber}</b></font>"
            file_number1_style = styles['BodyText_FileNumber']
            file_number1_style.leftIndent = -320           
            file_number1_data = Paragraph(file_number1, file_number1_style)
            elements.append(file_number1_data)
            elements.append(Spacer(1, -5))            
            #----
            image_path = f'static/images/{parcel.FileNumber}.png'
            img = Image(image_path, width=250, height=330)
            elements.append(img)
            elements.append(Spacer(1, -5))

            beacon_text = "<u>BEACON READINGS</u>"
            beacon_style = styles['Heading4']
            beacon_style.alignment = 1
            beacon_style.fontSize = 9
            
            beacon_data = Paragraph(beacon_text, beacon_style)
            elements.append(beacon_data)
            elements.append(Spacer(1, -5))
            #----
            # Create a table with headers
            table_data = [['No', 'FromBeacon', 'Direction', 'Length', 'ToBeacon']]  # Header row
            for line in lines:
                # Customize this line based on your model fields
                table_data.append([line.Sequence, line.FromBeaconNo, (str(int(line.Dir1))+u"\N{DEGREE SIGN}" + " " + str(int(line.Dir2)))+"'", line.Length, line.ToBeaconNo])

            # Define the table style
            table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), '#ffffff'),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1, 1)),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
                                    ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 40),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                                    ])

            # Create the table and apply the style
            table = Table(table_data)
            table.setStyle(table_style)
            elements.append(table)

            elements.append(Spacer(1, 130))


            logo_path = f'static/images/logo1.png'
            logo_img = Image(logo_path, width=40, height=40)
            logo_img.hAlign = TA_RIGHT
            elements.append(logo_img)
            elements.append(Spacer(1, -20))

            footer = f"<font name = 'Helvetica' size = '4'><b>GENERATED BY: ABIAGIS @ { time } & GENERATED BY GIS</b></font>"
            footer_style = styles['BodyText_Footer']
            footer_style.alignment = 1
            footer_data = Paragraph(footer, footer_style)
            elements.append(footer_data)
            
          
            

        # Build the PDF document
        #pdf.save()
        pdf.build(elements)

        # Set the response content type
        response = HttpResponse(content_type='application/pdf')
        # Set the content disposition for downloading
        response['Content-Disposition'] = 'attachment; filename="data_from_database.pdf"'
        # Write the PDF to the response
        response.write(buffer.getvalue())

        return response
    
    def add_fixed_frame(self, canvas, doc):
        # Define the dimensions and position of the fixed frame (bottom right corner)
        frame_width = 100
        frame_height = 50
        frame_x = doc.width - frame_width
        frame_y = 20

        # Create a frame and draw a border around it
        frame = Frame(frame_x, frame_y, frame_width, frame_height)
        frame.drawBoundary(canvas)

        # Add content to the fixed frame (e.g., logo)
        logo_path = 'static/images/logo1.png'  # Replace with the actual path to your logo image
        logo_width = frame_width - 10  # Adjust the width of the logo
        logo_height = frame_height - 10  # Adjust the height of the logo

        canvas.drawInlineImage(logo_path, frame_x + 5, frame_y + 5, width=logo_width, height=logo_height)
    
        