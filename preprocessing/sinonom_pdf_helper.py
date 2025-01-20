import os
import shutil
from pdf2image import convert_from_path
import preprocessing.translate_sn2vn
import preprocessing.sort_boxes
import base64
import requests
TOKEN = "677596f6-bc67-472b-a46d-c5bc6d49012d"
EMAIL = "ngthach3110@gmail.com"

def encode_image_to_base64(image_path):
    """
    Converts an image file to a base64-encoded string.
    :param image_path: Path to the image file
    :return: Base64-encoded string
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def kandian_ocr_api(
    token,
    email,
    image_base64,
    det_mode="auto",
    char_ocr=False,
    image_size=0,
    return_position=False,
    return_choices=False
):
    """
    Calls the Kandian Ancient Books OCR API with the specified parameters.
    :param token: API token
    :param email: Registered email
    :param image_base64: Base64-encoded image string
    :param det_mode: Text content layout style ('auto', 'sp', 'hp')
    :param char_ocr: Detect and recognize single characters only (Boolean)
    :param image_size: Image size adjustment before recognition (Integer)
    :param return_position: Return text line and character coordinate info (Boolean)
    :param return_choices: Return alternative candidate words for each character (Boolean)
    :return: Response from the API
    """
    url = "https://ocr.kandianguji.com/ocr_api"

    payload = {
        "token": token,
        "email": email,
        "image": image_base64,
        "det_mode": det_mode,
        "char_ocr": char_ocr,
        "image_size": image_size,
        "return_position": return_position,
        "return_choices": return_choices,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"HTTP {response.status_code}: {response.text}"}

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
        image_base64 = encode_image_to_base64(image_path)
        page_content = list()
        # Call the API
        result = kandian_ocr_api(
                token=TOKEN,
                email=EMAIL,
                image_base64=image_base64,
                det_mode="auto",
                char_ocr=False,
                image_size=0,
                return_position=True,
                return_choices=False,
            )
        text_lines=result['data']['text_lines']
        transliterate_text = preprocessing.translate_sn2vn.sn_transliteration_api('\n'.join([text_line['text'] for text_line in text_lines]))        
        for line_id, text_line in enumerate(text_lines):
            page_content.append({'bbox': text_line['position'], 'content': text_line['text'], 'transliteration': transliterate_text[line_id]})
        pdf_content.append({'page_number': i, 'content': preprocessing.sort_boxes.sort(page_content)})
    shutil.rmtree(output_folder)
    return pdf_content
    