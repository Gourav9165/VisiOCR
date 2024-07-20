# VisiOCR 

VisiOCR is a Django-based application that processes uploaded images to extract text information (such as name, date of birth, PAN number, and Aadhaar number), generates a QR code for the extracted information, and allows users to download this information in PDF format.

## Features 

- Upload images and extract text information using OCR (Optical Character Recognition).
- Generate QR codes for the extracted information.
- Download extracted information as a PDF file.
- Store extracted information in a MySQL database.

## Installation 

### Prerequisites 

- Python 3.x
- Django 5.x
- MySQL
- Tesseract-OCR
- OpenCV

### Setup 🔧

1. Clone the repository:

    ```bash
    git clone https://github.com/Gourav9165/visiocr_grp_B.git
    cd visiocr
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Install Tesseract-OCR:

    **Ubuntu:**

    ```bash
    sudo apt-get update
    sudo apt-get install tesseract-ocr
    ```

    **Windows:**

    Download and install Tesseract-OCR from [here](https://github.com/tesseract-ocr/tesseract).

5. Configure MySQL:

    - Create a new database named `visiocr`.
    - Update the database settings in `visiocr/settings.py`:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'visiocr',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
    ```

6. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

7. Run the development server:

    ```bash
    python manage.py runserver
    ```

    Access the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Usage 

### Upload Image 📷

- On the home page, click on "Choose File" to select an image file from your computer.
- Click on "Upload Image" to upload the selected image.

### View Extracted Information 

- After uploading, the extracted information will be displayed on the home page along with a generated QR code.

### Download PDF 📄

- If the extracted information is correct, click on "Download as PDF" to download the information as a PDF file.

## Output 📸

![Home Page](outputs/1.png)

![Create_Pass](outputs/2.png)

![Pass_info](outputs/3.png)

![Validation](outputs/4.png)

![Active_Pass](outputs/5.png)

![PDF](outputs/6.png)


## Project Structure 🗂️

```bash
visiocr/
│
├── visiocr_app/
│   ├── migrations/
    └── templates/
│       ├── home.html
        |── info.html
        |── upload.html
│       └── validate_qr.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── visiocr/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md
```


## Code Overview 

### Views
- `home`: Renders the home page.
- `upload_image`: Handles image uploads, processes the image to extract information, generates a QR code, and stores the information in the database.
- `download_pdf`: Generates a PDF file with the extracted information and allows the user to download it.

### Templates
- `home.html`: The main page where users can upload images and view the extracted information.
- `pdf_template.html`: The template used to generate the PDF file.

### Database
- `create_connection`: Establishes a connection to the MySQL database.
- `create_table`: Creates the `extracted_data` table if it does not exist.
- `insert_data`: Inserts extracted information into the `extracted_data` table.

### OCR and QR Code Generation
- `preprocess_image`: Converts the image to grayscale and applies binary thresholding.
- `extract_info`: Extracts text information from the image using Tesseract-OCR.
- `create_qr_code`: Generates a QR code for the extracted information.


## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
