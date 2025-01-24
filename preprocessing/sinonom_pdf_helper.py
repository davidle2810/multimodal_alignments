import os
import shutil
from pdf2image import convert_from_path
import preprocessing.translate_sn2vn
import preprocessing.sort_boxes
import base64
import requests
import json

def upload_image_api(image_path):
    headers = {
    "User-Agent": "upload_image"
    }
    url_upload = "https://tools.clc.hcmus.edu.vn/api/web/clc-sinonom/image-upload"
    files = [
        (  
                'image_file',
                ('test_image.jpg', open(image_path, 'rb'),
                'image/jpeg')
        )
    ]
    headers = {
        "User-Agent": "upload_image"
    }
    response = requests.post(url_upload, headers=headers, files=files)
    data = json.loads(response.text)
    if data['is_success']:
        file_name = data['data']['file_name']
    else:
        print("error uploading image:", data['message'])
    return file_name

def ocr_image_api(image_path_server):
    headers = {
    "User-Agent": "ocr"
        }
    url_ocr = "https://tools.clc.hcmus.edu.vn/api/web/clc-sinonom/image-ocr"
    data = {
        "ocr_id": 1,
        "file_name": image_path_server
    }
 
    ocr_response = requests.post(url_ocr, headers=headers, json=data)  
    data = json.loads(ocr_response.text)
    if data['is_success']:
        ocr = data['data']['result_bbox']
 
    result = list()
    for i in ocr:
        result.append({'position':i[0],'text': i[1][0]})

    return result
def extract_pages(file_name: str) -> list:
    """
    Extracts the NS text from each page of the provided file.
    :param file_name: The path to the NS file.
    :return: A list of dictionaries, where each dictionary represents a page in the file and contains:
        - 'page_number': An integer representing the page index (starting from 0).
        - 'content': A list of dictionaries, each representing a line of text on the page. Each line dictionary contains:
            - 'bbox': A list of four tuples representing the coordinates of the bounding box for the text, in the form [[x0, y0], [x1, y1], [x2, y2], [x3, y3]].
            - 'content': The text content within the bounding box.
            - 'transliteration': The transliterated version of the text content.
    """
    # Convert PDF to images
    pages = convert_from_path(file_name, 600)  # 300 DPI for better quality
    pdf_content = list()
    output_folder='./data/images_nom'
    if os.path.exists(output_folder) and os.path.isdir(output_folder):
        os.system(f'rm -r {output_folder}')
    os.makedirs(output_folder)
    # Save each page as an image
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i}.png")  # Save as PNG
        page.save(image_path, 'PNG')
        page_content = list()
        text_lines = ocr_image_api(upload_image_api(image_path))
        transliterate_text = preprocessing.translate_sn2vn.sn_transliteration_api('\n'.join([text_line['text'] for text_line in text_lines]))        
        for line_id, text_line in enumerate(text_lines):
            page_content.append({'bbox': text_line['position'], 'content': text_line['text'], 'transliteration': transliterate_text[line_id]})
        pdf_content.append({'page_number': i, 'content': preprocessing.sort_boxes.sort(page_content)})
    shutil.rmtree(output_folder)
    return pdf_content
    