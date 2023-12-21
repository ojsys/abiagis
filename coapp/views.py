from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views import View
from django.contrib.auth import get_user_model
from .models import Parcel, Lines
import io
import os
import re
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.template.loader import get_template
from django.template import Context

# reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image, Table, TableStyle, BaseDocTemplate, Frame
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
# ---------
################################
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
################################
from .forms import ParcelSearchForm, MergePDFForm
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
    
class MyPDFView(View):
    def get(self, request, parcel_id, *args, **kwargs):
        # Retrieve data from the database
        pdfmetrics.registerFont(TTFont('Playbill', 'Playbill.ttf'))
        parcels = Parcel.objects.filter(id=parcel_id)
        lines = Lines.objects.filter(ParcelID_id__in=parcels.values_list('OBJECTID', flat=True)).order_by('Sequence')
        time = datetime.now().strftime("%I:%M:%S %p, %A, %B %d, %Y")

        # Create a buffer to store the PDF
        buffer = BytesIO()
        def _header_footer(canvas, pdf):
            # Save the state of our canvas so we can draw on it
            canvas.saveState()
            styles = getSampleStyleSheet()

            # Header
            header = Paragraph(f'{parcel.FileNumber}', styles['Normal'])
            w, h = header.wrap(pdf.width, pdf.topMargin)
            header.drawOn(canvas, pdf.leftMargin, pdf.height + pdf.topMargin - h)

            # Footer
            footer = Paragraph(f"<font name = 'Helvetica' size = '4'><b>GENERATED BY: ABIAGIS @ { time } & GENERATED BY GIS</b></font>", styles['Normal'])
            footer_img = Image('static/images/logo1.png', width='40', height='40')
            w, h = footer.wrap(pdf.width, pdf.bottomMargin)
            footer.drawOn(canvas, pdf.leftMargin, h)
            logo_path = 'static/images/logo1.png'
            logo_img = Image(logo_path, width=40, height=40)
            logo_img.hAlign = TA_RIGHT
            elements.append(logo_img)
            elements.append(Spacer(1, -20))
            # Release the canvas
            canvas.restoreState()
        
        # Create the PDF object using the buffer
        pdf = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=10, bottomMargin=0.5, allowSplitting=1, title="Parcel Fabric")
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
        styles.add(ParagraphStyle(name='BodyText_FileNumber', fontName='Helvetica', fontSize=12, alignment=TA_CENTER))
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
            reg_no = f"<font name = 'Helvetica' size = '13'>REGISTRATION NUMBER: <b>{parcel.R_Particulars}</b></font>"             # Create a paragraph with the data
            reg_no_data = Paragraph(reg_no, styles['BodyText'])
            elements.append(reg_no_data)
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
            sur_style.leftIndent = -7
            surveyor_data = Paragraph(surveyor, sur_style)
            elements.append(surveyor_data)
            elements.append(Spacer(1, -5))
            #----
            surveyor_title = "<font name = 'Helvetica' size = '9'>SURVEYOR GENERAL</font>"
            sur_style2 = styles['BodyText_Survey2']
            sur_style2.leftIndent = 0
            surveyor_title_data = Paragraph(surveyor_title, sur_style2)
            elements.append(surveyor_title_data)
            elements.append(Spacer(1, 3))

            #----
            # class RotatePara(Paragraph):

            #     def wrap(self, availWidth, availHeight):
            #         height, width = Paragraph.wrap(self, 10, 50)
            #         return width, height
                
            #     def draw(self):
            #         self.canv.rotate(90)
            #         self.canv.drawString(50, 500, f"{parcel.FileNumber}")
            #         Paragraph.draw(self)

            # file_number = f"<font name='Helvetica' size='11'><b>{parcel.FileNumber} <br/> {parcel.R_Particulars}</b></font>"
            # file_number_style = styles['BodyText_FileNumber']
            # file_number_style.leftIndent = -530
            # file_number_style.leading = 10
            
            # file_number_data = RotatePara(file_number, file_number_style)            
            # elements.append(Spacer(10, 20))
            # elements.append(file_number_data)
            
            
            
            ################################ FILE IMAGE ################################
            image_path = f'static/images/{parcel.FileNumber.replace(":", "~")}.png'
            if image_path:
                
                img = Image(image_path, width=250, height=330)
                
                elements.append(img)
                elements.append(Spacer(1, -5))
            elif FileExistsError:
                img = Image('static/images/NoImage.png', width=250, height=330)
                errormsg = Paragraph("Please check the matching file Number in the Images Folder!")
                elements.append(errormsg)
                elements.append(img)
                elements.append(Spacer(1, -5))
            ################################END IMAGE################################


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
                table_data.append([line.Sequence, line.FromBeaconNo, line.Direction, line.Length, line.ToBeaconNo])

            # Define the table style
            table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), '#ffffff'),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1, 1)),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
                                    ('BACKGROUND', (0, 0), (-1, -1), '#ffffff'),
                                    ('LEFTPADDING', (0, 0), (-1, -1), 40),
                                    ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                                    ])

            # Create the table and apply the style
            table = Table(table_data)
            table.setStyle(table_style)
            
            elements.append(table)

            


            

            footer = f"<font name = 'Helvetica' size = '4'><b>GENERATED BY: ABIAGIS @ { time } & GENERATED BY GIS</b></font>"
            footer_style = styles['BodyText_Footer']
            footer_style.alignment = 1
            footer_data = Paragraph(footer, footer_style)
            elements.append(footer_data)
            
            def rotate_text(canvas, text, style, x, y, angle):
                canvas.saveState()
                canvas.rotate(angle)
                canvas.setFont(style.fontName, style.fontSize)
                canvas.drawString(x, y, text)
                canvas.restoreState()      
                

            texttorotate = f"{parcel.FileNumber}"
        
        # Build the PDF document
        #pdf.save()
        pdf.build(elements, onFirstPage=lambda canvas, doc: rotate_text(canvas, texttorotate, styles['Normal'], 50, 50, 90), onLaterPages=_header_footer)

        if parcel.LGA == "Aba North":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Aba_North"
        elif parcel.LGA == "Aba South":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Aba_South"
        elif parcel.LGA == "Arochukwu":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Arochukwu"
        elif parcel.LGA == "Bende":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Bende"
        elif parcel.LGA == "Ikwuano":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Ikwuano"
        elif parcel.LGA == "Isiala Ngwa North":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Isiala_Ngwa_North"
        elif parcel.LGA == "Isiala Ngwa South":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Isiala_Ngwa_South"
        elif parcel.LGA == "Isuikwuato":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Isuikwuato"
        elif parcel.LGA == "Nnochi":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Nnochi"
        elif parcel.LGA == "Obi Ngwa":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Obingwa"
        elif parcel.LGA == "Ohafia":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Ohafia"
        elif parcel.LGA == "Osisioma Ngwa":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Osisioma"
        elif parcel.LGA == "Ugwunagbo":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Ugwunagbo"
        elif parcel.LGA == "Ukwa East":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Ukwa_East"
        elif parcel.LGA == "Ukwa West":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Ukwa_West"
        elif parcel.LGA == "Umuahia North":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_North"
        elif parcel.LGA == "Umuahia South":
            pdf_directory = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_South"
        

        pdf_file_name = f"{parcel.FileNumber}.pdf"

        pdf_file_path = os.path.join(pdf_directory, pdf_file_name.replace('/', ':'))
        
        with open(pdf_file_path, 'wb') as pdf_file:
            pdf_file.write(buffer.getvalue())

        #### Merge pdf files
        def merge_pdfs(directory_path, output_path):
            #create a dictionary to store the related files
            pdf_dict = {}

            for filename in os.listdir(directory_path):
                if filename.endswith(".pdf"):
                    base_name = ''.join(filter(str.isalpha, filename))
                    pdf_dict.setdefault(base_name, []).append(os.path.join(directory_path, filename))

            # create the pdf merger
            merger = PdfMerger()
            
            #Merge pdf files with closely related names
            for base_name, pdf_paths in pdf_dict.items():
                if len(pdf_paths) > 1:
                    pdf_paths.sort()
                    for pdf_path in pdf_paths:
                        merger.append(pdf_path)

                    # Set the merged file name to the base name of one of the original documents
                    merged_filename = f"{base_name}_merged.pdf"
                    merged_filepath = os.path.join(output_path, merged_filename)   
                    merger.write(merged_filepath)
            
                    # Clear the merger for the next set of pdf files
            
                    merger.pages = []

        ################################
        if parcel.LGA == "Aba North":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Aba_North"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Aba_North/Merged"
        elif parcel.LGA == "Aba South":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Aba_South"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Aba_South/Merged"
        elif parcel.LGA == "Arochukwu":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Arochukwu"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Arochukwu/Merged"
        elif parcel.LGA == "Bende":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Bende"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Bende/Merged"
        elif parcel.LGA == "Ikwuano":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Ikwuano"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Ikwuano/Merged"
        elif parcel.LGA == "Isiala Ngwa North":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Isiala_Ngwa_North"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Isiala_Ngwa_North/Merged"
        elif parcel.LGA == "Isiala Ngwa South":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Isiala_Ngwa_South"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Isiala_Ngwa_South/Merged"
        elif parcel.LGA == "Isuikwuato":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Isuikwuato"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Isuikwuato/Merged"
        elif parcel.LGA == "Nnochi":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Nnochi"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Nnochi/Merged"
        elif parcel.LGA == "Obi Ngwa":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Obi_Ngwa"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Obi_Ngwa/Merged"
        elif parcel.LGA == "Ohafia":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Ohafia"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Ohafia/Merged"
        elif parcel.LGA == "Osisioma Ngwa":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Osisioma_Ngwa"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Osisioma_Ngwa/Merged"
        elif parcel.LGA == "Ugwunagbo":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Ugwunagbo"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Ugwunagbo/Merged"
        elif parcel.LGA == "Ukwa East":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Ukwa_East"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Ukwa_East/Merged"
        elif parcel.LGA == "Ukwa West":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Ukwa_West"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Ukwa_West/Merged"
        elif parcel.LGA == "Umuahia North":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_North"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_North/Merged"
        elif parcel.LGA == "Umuahia South":
            directory_path = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_South"
            output_path = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_South/Merged"

        merge_related_files(directory_path, output_path)




        # Set the response content type
        response = HttpResponse(content_type='application/pdf')
        # Set the content disposition for downloading
        #response['Content-Disposition'] = f'attachment; filename="{pdf_file_name}.pdf"'
        # Write the PDF to the response
        response.write(buffer.getvalue())

        return response
    

 #  We need to implement the merging of Documents from separate folders

    
            
# class MergePDFView(View):
#     template_name = 'coapp/mergepdf.html' 

#     def get(self, request, *args, **kwargs):
#         form = MergePDFForm()
#         return render(request, self.template_name, {'form': form, 'title': 'Merge PDF'})

#     def post(self, request, *args, **kwargs):
#         form = MergePDFForm(request.POST, request.FILES)

#         if form.is_valid():
#             pdf_file1 = form.cleaned_data['file1']
#             pdf_file2 = form.cleaned_data['file2']

#             # Merge PDF files
#             merged_pdf_path = self.merge_pdfs(pdf_file1, pdf_file2)

#             # Serve  the merged pdf files as response
#             with open(merged_pdf_path, 'rb') as merged_pdf_file:
#                 response = HttpResponse(merged_pdf_file.read(), content_type='application/pdf')
#                 response['Content-Disposition'] = 'inline; filename="merged_file.pdf"'
#                 return response
#         return render(request, self.template_name, {'form': form, 'title': 'Merge PDF'})

#     def merge_pdfs(self, pdf_file1, pdf_file2):

#         pdf_writer = PdfWriter()

#         # Add the pages from the first pdf file 
#         with open(pdf_file1, 'rb') as file1:
#             pdf_reader1 = PdfReader(file1)
#             for page_num in range(len(pdf_reader1.pages)):
#                 page = pdf_reader1.pages[page_num]
#                 pdf_writer.add_page(page)

#         # Add pages from the second PDF file
#         with open(pdf_file2, 'rb') as file2:
#             pdf_reader2 = PdfReader(file2)
#             for page_num in range(len(pdf_reader2.pages)):
#                 page = pdf_reader2.pages[page_num]
#                 pdf_writer.add_page(page)

#         # Write the merged PDF to the temporary file
#         merged_pdf_path = "/Users/mac/Documents/ABIAProject/parcels/Umuahia_North/merged.pdf"
#         with open(merged_pdf_path, 'wb') as merged_pdf_file:
#             pdf_writer.write(merged_pdf_file)

#         return merged_pdf_path
    
