from django.urls import path 
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('extract', views.extractText, name="extract_text"),
    path('download', views.downloadPDF, name="download_pdf"),
    path('check', views.checkStatus, name="check_status"),
    path('validate', views.validateQR, name="validate_qr"),
]