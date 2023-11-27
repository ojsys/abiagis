from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Parcel, Lines
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


User = get_user_model()

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
    if request.method == 'POST':
        searched = request.POST['q']
        return render(request, 'coapp/search_page.html', {'searched': searched})
    else:
        return render(request, 'coapp/search_page.html', {})

def view_parcel(request):
    query = request.GET.get('q')
    if not query:
        query = ''        
    parcel = Parcel.objects.filter(Q(FileNumber__icontains=query))
    return render(request, 'coapp/view_parcel.html', {'parcel':parcel})
    
    
def preview_page(request):
    
    return render(request, 'coapp/preview.html', {})

def generate_pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    textobj = p.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont('Helvetica', 14)
    
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    text = 'Hello world.'
    textobj.textLine(text)
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save() 

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')