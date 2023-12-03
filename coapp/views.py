from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Parcel, Lines
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
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
    

    context = {'parcels': parcels, 'lines':lines, 'time': datetime.now()}
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

def view_parcel(request, parcel_id):
    parcel_detail = get_object_or_404(Parcel, pk=parcel_id)
    parcels = Parcel.objects.filter(OBJECTID=parcel_detail)
    lines = Lines.objects.filter(ParcelID_id__in=parcels.values_list('OBJECTID', flat=True))
    return render(request, 'coapp/view_parcel.html', {'parcel_detail':parcel_detail, 'lines':lines})
    
    
def generate_pdf(request, parcel_id):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    textobj = p.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont('Helvetica', 14)
    
    
    parcels = Parcel.objects.all()
    lines = Lines.objects.all()
    for parcel in parcels:
        if parcel.id == parcel_id:
            lines = Lines.objects.filter(ParcelID_id=parcel.OBJECTID)
            textobj.textLine(parcel.FileNumber)
            textobj.textLine(parcel.Name_of_Allottee)
            textobj.textLine(parcel.LGA)
            textobj.textLine(parcel.Plan_No)
            textobj.textLine(parcel.Starting_Pillar_No)
            textobj.textLine(parcel.R_Particulars)
            


    p.drawText(textobj)    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save() 

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='/Users/mac/Documents/ABIAProject/hello.pdf')