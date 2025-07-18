from django.urls import path
from .views import scan_barcode, scanner_home

urlpatterns = [
    path('', scan_barcode, name='scan_barcode'),
    path('scanner/', scanner_home, name='scanner_home'),
]