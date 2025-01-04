import os
import shutil
from pdf2image import convert_from_path
import preprocessing.translate_sn2vn
import cv2
import base64
import json
import requests
TOKEN = "677596f6-bc67-472b-a46d-c5bc6d49012d"
EMAIL = "ngthach3110@gmail.com"

def enhance_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (21, 21), 0)
    normalized_image = cv2.subtract(gray_image, blurred_image)
    enhanced_image = cv2.equalizeHist(normalized_image)
    threshold_image = cv2.adaptiveThreshold(enhanced_image, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    denoised = cv2.morphologyEx(threshold_image, cv2.MORPH_CLOSE, kernel)
    inverted_image = cv2.bitwise_not(denoised)
    return inverted_image

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


def stringToStringSorted(res: list):
    
    size = len(res)
    quickSort(res, 0, size - 1)
    return json.dumps(res)


def partition(arr: list, low: int, high: int):
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        if arr[j][0] >= pivot[0]:
            i = i + 1
            (arr[i], arr[j]) = (arr[j], arr[i])

    (arr[i + 1], arr[high]) = (arr[high], arr[i + 1])
    return i + 1


def quickSort(arr: list, low: int, high: int):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)

def extract_pages(file_name):
    # Convert PDF to images
    pages = convert_from_path(file_name, 600)  # 300 DPI for better quality
    pdf_content = list()
    # Save each page as an image
    output_folder='./data/images_nom'
    os.makedirs(output_folder)
    # Save each page as an image
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")  # Save as PNG
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
        for i, text_line in enumerate(text_lines):
            # row = {}
            # row["page_number"] = i
            # row['position'] = stringToStringSorted(text_line['position'])
            # row['content'] = text_line['text']
            page_content.append({'bbox': text_line['position'], 'content': text_line['text'], 'transliteration':transliterate_text[i]})
        pdf_content.append({'page_number': i+1, 'content':page_content})
    shutil.rmtree(output_folder)
    return pdf_content
    