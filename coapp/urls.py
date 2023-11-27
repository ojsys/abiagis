
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_parcel/', views.search_parcel, name='search_parcel'),
    path('search_page/', views.search_page, name='search_page'),
]
