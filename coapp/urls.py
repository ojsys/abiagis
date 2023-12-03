
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('view_parcel/<int:parcel_id>', views.view_parcel, name='view_parcel'),
    path('search_page/', views.search_page, name='search_page'),
    path('render_pdf/<int:parcel_id>/', views.render_pdf_view, name='render_pdf'),
]
