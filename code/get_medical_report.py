import os
from PIL import Image
import pytesseract
import PyPDF2
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='deu') 
    return text

def extract_text_from_pdf_image(pdf_path):
    extracted_text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            if '/XObject' in page['/Resources']:
                xObject = page['/Resources']['/XObject'].get_object()
                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                        data = xObject[obj]._data
                        if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                            mode = "RGB"
                        else:
                            mode = "P"

                        if '/Filter' in xObject[obj]:
                            if xObject[obj]['/Filter'] == '/DCTDecode':
                                img = Image.open(BytesIO(data))
                                text = pytesseract.image_to_string(img, lang='deu')
                                extracted_text += text
                            elif xObject[obj]['/Filter'] == '/FlateDecode':
                                img = Image.frombytes(mode, size, data)
                                text = pytesseract.image_to_string(img, lang='deu')
                                extracted_text += text
    return extracted_text