import cv2, os
import pytesseract, numpy as np
from . import Aadhar_Extraction as aadhar
from . import Pan_Extraction as pan
from .models import OCR_store
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
import qrcode, json, base64
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def home(request):
    context = {'STATIC_VERSION': settings.STATIC_VERSION}
    return render(request, 'home.html', context)

def preprocess(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # _, binary = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return gray_image

        
def extractText(request):
    if(request.method == 'POST'):
        card_type = request.POST.get('Card')
        image_file = request.FILES["image"]
        visitor_name = request.POST.get('visitor_name')
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
        
        if(card_type == 'Aadhar'):
            extracted_info = aadhar.extract_info(extracted_text)
        elif(card_type == 'Pan'):
            extracted_info = pan.extract_info(extracted_text)
 
        qr_code = generateQR(extracted_info, date_of_visiting, duration_of_visiting)

        if 'Date of Birth' in extracted_info.keys():
            x = extracted_info['Date of Birth'].split('/')
            formatted_dob = datetime(int(x[2]), int(x[1]), int(x[0]))
        else:
            formatted_dob = None

        try:
            OCR_store.objects.create( Name=extracted_info['Name'], Father_name=extracted_info['Father_name'], 
                                       Gender=extracted_info['Gender'] if 'Gender' in extracted_info.keys() else None, 
                                        DOB=formatted_dob, 
                                        Pan_no=extracted_info['Pan No'] if 'Pan No' in extracted_info.keys() else None,
                                        Aadhaar_no=extracted_info['Aadhaar No'] if 'Aadhaar No' in extracted_info.keys() else None,
                                        Phone_no=extracted_info['Phone No'] if 'Phone No' in extracted_info.keys() else None,
                                        Expiry_time=extracted_info['Expiry time'] )
        except:
            print("Data unable to insert..")
    
        return render(request, 'info.html', {'extracted_info': extracted_info, 'qr_code': qr_code})
    
    return render(request, 'upload.html')



def generateQR(data, time, duration):
    try:
        formatted_time = datetime.strptime(time, '%Y-%m-%dT%H:%M')
        hrs = int(duration)
        expiry =  formatted_time + timedelta(hours=hrs)
        data['Expiry time'] = expiry.strftime("%Y-%m-%d %H:%M:%S")

        # Generate the QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, 
                           box_size=4, border=4)
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
        p = Canvas(buffer, pagesize=letter)

        # Registering the Montserrat font
        pdfmetrics.registerFont(TTFont('Montserrat', 'D:/PROGRAMMING/Infosys SB/VisiOCR-Project-master/visiOCR\Montserrat/static/Montserrat-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Montserrat-Bold', 'D:/PROGRAMMING/Infosys SB/VisiOCR-Project-master/visiOCR\Montserrat/static/Montserrat-Bold.ttf'))

        # Setting up the colors
        background_color = HexColor("#e8eaf6")
        text_color = HexColor("#2c3e50")
        header_background = HexColor("#91b9dc")
        qr_code_shadow_color = colors.grey

        # Draw background
        p.setFillColor(background_color)
        p.rect(0, 0, letter[0], letter[1], fill=1)

        # Draw header
        p.setFillColor(header_background)
        draw_rounded_rect(p, 0, 720, letter[0], 100, 20, fill=1)

        # Title
        p.setFont("Montserrat-Bold", 30)
        p.setFillColor(text_color)
        p.drawCentredString(letter[0] / 2, 750, "Visitor Pass")

        # Content
        p.setFont("Montserrat", 12)
        y = 690
        for key, value in extracted_info.items():
            p.drawString(170, y, f"{key}: {value}")
            y -= 30

        # QR Code
        qr_code_width = 2 * inch
        qr_code_height = 2 * inch
        qr_code_x = (letter[0] - qr_code_width) / 2
        qr_code_y = y - qr_code_height - 50

        # Draw QR code with border radius
        qr_code_io = BytesIO()
        qr_code_image.save(qr_code_io, format='PNG')
        qr_code_io.seek(0)
        qr_code_reader = ImageReader(qr_code_io)
        draw_rounded_rect(p, qr_code_x, qr_code_y, qr_code_width, qr_code_height, 10, fill=0)
        p.drawImage(qr_code_reader, qr_code_x, qr_code_y, width=qr_code_width, height=qr_code_height, mask='auto')

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        qr_code_io.close()
        response.write(pdf)
        return response











































def checkStatus(request):
    return render(request, 'validate_qr.html', {'status': -1})

def validateQR(request):
    if request.method == 'POST':
            image = request.FILES['qr-image']
            img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)

            # Decode the QR code
            decoded_objects = decode(img)
            data = None
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')

            if data:
                data = data.replace("'", "\"")
                converted_data = json.loads(data)

                expiry_time = converted_data['Expiry time']
                time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                if(current_time < time):
                   flag = 1
                   pil_img = Image.fromarray(img)
                   buffered = BytesIO()
                   pil_img.save(buffered, format="PNG")
                   img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                   converted_data["Image url"] = img_str 

                   with open('temp.json', 'w') as fp:
                     json.dump(converted_data, fp)
                else:
                    flag = 0

                return render(request, 'validate_qr.html', {'status': flag})
            else:
                return HttpResponse("No QR code found.")
            
    f = open('temp.json')
    data = json.load(f)
    f.close()
    img_str = data['Image url']
    del data['Image url']
    return render(request, 'info.html', {'extracted_info': data, 'qr_code': img_str})



def draw_rounded_rect(canvas, x, y, width, height, radius, fill=1):
    canvas.roundRect(x, y, width, height, radius, fill=fill)