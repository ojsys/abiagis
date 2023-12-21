
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_page/', views.search_page, name='search_page'),
    path('render_pdf/<int:parcel_id>/', views.render_pdf_view, name='render_pdf'),
    path('generate_pdf/<int:parcel_id>/', views.MyPDFView.as_view(), name='generate_pdf'),
    path('blackcopy/<int:parcel_id>', views.BlackCopyView.as_view(), name='blackcopy'),
]
