import re
from .models import OCR_data

def get_name(text, target_word):
    res = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if target_word in line:
            if i + 1 < len(lines):
                res.append(lines[i + 1].strip())
            if i + 3 < len(lines):
                res.append(lines[i + 3].strip())
            break
    return res

def extract_info(data):
        extracted = {}
        text = ""
        print("\t\tPAN DETAILS")
        print("=====================================================")
        dob = re.findall(r'\b(\d{2}/\d{2}/\d{4})', data)
        if(len(dob) > 0):
           print("Date of Birth:",dob[0])
           text += dob[0]+", "
           extracted['Date of Birth'] = dob[0]
        else:
           print("Date of Birth:",dob)

        names = get_name(data, 'Name')
        print("Name:",names[0])
        print("Father's name:",names[1])

        text += (names[0]+", "+names[1]+", ")
        extracted['Name'] = names[0]
        extracted['Father_name'] = names[1]
             
        pan_number = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]', data)
        if(len(pan_number) > 0):
            print("Pan card No:",pan_number[0])
            text += pan_number[0]+", "
            extracted['Pan No'] = pan_number[0]
        else:
            print("Pan card No:",pan_number)
        print("=====================================================")

        id_type = "Pan card"
        try:
            OCR_data.objects.create(id_type=id_type, text=text)
        except:
            print("Data unable to insert..")

        return extracted