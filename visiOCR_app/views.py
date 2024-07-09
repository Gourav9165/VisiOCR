import cv2, os
import pytesseract
from . import Aadhar_Extraction as aadhar
from . import Pan_Extraction as pan
from .models import OCR_store
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
import qrcode, json, base64
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def home(request):
    context = {'STATIC_VERSION': settings.STATIC_VERSION}
    return render(request, 'home.html', context)

def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return gray_image

def generateQR(data):
    try:
        json.dumps(data)
        expiry = datetime.now() + timedelta(hours=2)
        data['Expiry time'] = expiry.strftime("%Y-%m-%d %H:%M:%S")

        # Generate the QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, 
                           box_size=3, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save the QR code
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str
    except Exception as e:
        print("Failed to create QR code: %s", e)

def downloadPDF(request):
    if request.method == 'POST':
        extracted_info = request.POST.get('extracted_info')
        extracted_info_str = extracted_info.replace("'", "\"")
    
        try:
            extracted_info = json.loads(extracted_info_str)
            print("Successfully loaded..")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data.")
        
        qr_code_data = request.POST.get('qr_code')
        qr_code_image = Image.open(BytesIO(base64.b64decode(qr_code_data.split(',')[1])))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="visitor_pass.pdf"'

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 30)
        p.drawString(180, 730, "Visitor Pass")
        p.setFont("Helvetica", 12)
        y = 690
        for key, value in extracted_info.items():
            p.drawString(170, y, f"{key}: {value}")
            y -= 30

        qr_code_io = BytesIO()
        qr_code_image.save(qr_code_io, format='PNG')
        qr_code_io.seek(0)
        qr_code_reader = ImageReader(qr_code_io)
        p.drawImage(qr_code_reader, 200, y - 100, width=100, height=100)
        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        qr_code_io.close()
        response.write(pdf)
        return response
        
def extractText(request):
    if request.method == 'POST':
        card_type = request.POST.get('Card')
        image_file = request.FILES['Image']
        
        visitor_name = request.POST.get('visitor_name')
        mobile_number = request.POST.get('mobile_number')
        date_of_visiting = request.POST.get('date_of_visiting')
        duration_of_visiting = request.POST.get('duration_of_visiting')
        
        image_path = os.path.join(settings.MEDIA_ROOT, image_file.name)
        with open(image_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        image = cv2.imread(image_path)
        processed = preprocess(image)

        try:
            extracted_text = pytesseract.image_to_string(processed)
            print("Extracted Text:")
            print(extracted_text)
        except Exception as e:
            print(f"An error occurred: {e}")
        
        if card_type == 'Aadhar':
            extracted_info = aadhar.extract_info(extracted_text)
        elif card_type == 'Pan':
            extracted_info = pan.extract_info(extracted_text)

        if 'Date of Birth' in extracted_info.keys():
            x = extracted_info['Date of Birth'].split('/')
            formatted_dob = datetime(int(x[2]), int(x[1]), int(x[0]))
        else:
            formatted_dob = None
 
        qr_code = generateQR(extracted_info)

        extracted_info.update({
            'Date of Visiting': date_of_visiting,
            'Duration of Visiting': duration_of_visiting
        })

        try:
            OCR_store.objects.create(
                Name=extracted_info['Name'],
                Father_name=extracted_info.get('Father_name'),
                Gender=extracted_info.get('Gender'),
                DOB=formatted_dob,
                Pan_no=extracted_info.get('Pan No'),
                Aadhaar_no=extracted_info.get('Aadhaar No'),
                Phone_no=extracted_info.get('Phone No'),
                Expiry_time=extracted_info['Expiry time']
            )
        except:
            print("Data unable to insert..")
    
        return render(request, 'info.html', {'extracted_info': extracted_info, 'qr_code': qr_code})
    
    return HttpResponse("Extracting text..")
