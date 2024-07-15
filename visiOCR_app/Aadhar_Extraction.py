import re
from .models import OCR_data

def get_name(text, target_word):
    names = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if target_word in line:
            if i + 3 < len(lines):
                names.append(lines[i + 3].strip()[:-1])
            if i + 4 < len(lines):
                names.append(lines[i + 4].strip()[4:])
            break
    return names

def extract_info(data):
        extracted = {}
        text = ''
        print('\t\tDETAILS')
        print('=====================================================')
        aadhaar_number = re.findall(r'\b(\d{4}\s\d{4}\s\d{4})', data)
        if(len(aadhaar_number) > 0):
            print('Aadhaar No:',aadhaar_number[0])
            text += aadhaar_number[0]+', '
            extracted['Aadhaar No'] = aadhaar_number[0]
        else:
            print('Aadhaar No:',aadhaar_number)

        names = get_name(data, 'To')
        if(len(names) >= 1):
            print('Name:',names[0])
            print('Father name:',names[1])
            extracted['Name'] = names[0]
            extracted['Father_name'] = names[1]
            text += names[0]+', '
      
        gender = ''
        if('FEMALE' in data):
             gender = 'Female'
        else:
             gender = 'Male'
        print('Gender:',gender)
        if(len(gender) > 0):
             text += gender+', '
             extracted['Gender'] = gender

        dob = re.findall(r'\b(\d{2}/\d{2}/\d{4})', data)
        if(len(dob) > 0):
            print('Date of Birth:',dob[0])
            text += dob[0]+', '
            extracted['Date of Birth'] = dob[0]
        else:
            print('Date of Birth:',dob)

        phone_number = re.findall(r'\b(\d{10})', data)
        print('Phone No:',phone_number)
        if(len(phone_number) > 0):
             text += phone_number[0]
             extracted['Phone No'] = phone_number[0]
        print('=====================================================')

        id_type = "Aadhaar card"
        try:
            OCR_data.objects.create(id_type=id_type, text=text)
        except:
            print('Data unable to insert..')

        return extracted