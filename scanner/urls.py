from django.urls import path
from .views import scan_barcode

urlpatterns = [
    path('', scan_barcode, name='scan_barcode'),
]