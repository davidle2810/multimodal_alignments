from unstructured.partition.auto import partition
import pytesseract
import google.generativeai as genai
import os
import shutil
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = r"mnt/c/users/Quoc Anh/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
genai.configure(api_key='AIzaSyDX5tM_HRPoFl7pCQxZ97WwICMCFwtsGqc')
model = genai.GenerativeModel('gemini-1.5-pro')
import cv2
import numpy as np

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

def clean_text_with_gemini(input_text):
    """
    Function to clean text using Google's Gemini model.
    Removes specific artifacts and symbols.
    """
    prompt = [
        {'role': 'user',
         'parts': [
        f"Clean the following text by removing artifacts like '-86-', '(88a)', 'NMCÀY A4ÔXC TÁM' and ",
        "random symbols like '®?)', 'Ø⁄', 'CðuÁnft', etc. and unwords, while keeping the structure intact. ",
        "Example: Input: 46 + Em ° Diệt + E4 4T 20 D5] 31s BE” Hỏi. Đức Chúa Trời là Đấng nào? Thưa. Đức Chúa Trời là Đấng dựng nên trời đất muôn vật cùng hãng gìn. Output:Hỏi. Đức Chúa Trời là Đấng nào? Thưa. Đức Chúa Trời là Đấng dựng nên trời đất muôn vật cùng hãng gìn.\n\n",
        f"{input_text}\n\n"]}
    ]


    # Make the request to Gemini model for text completion
    response =  model.generate_content(prompt,safety_settings={'HARASSMENT':'BLOCK_ONLY_HIGH'},generation_config=genai.types.GenerationConfig(
                                                                                                                                        candidate_count=1))

    # Return the cleaned text
    return response.candidates[0].content.parts[0].text

def extract_pages(file_name):
    # Convert PDF to images
    pages = convert_from_path(file_name, 600)  # 300 DPI for better quality
    pdf_content = list()
    os.system('rm -r ./data/images_viet')
    # Save each page as an image
    output_folder='./data/images_viet'
    os.makedirs(output_folder)

    # Save each page as an image
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")  # Save as PNG
        page.save(image_path, 'PNG')
        # open_cv_image = np.array(page)
        # open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)  # Convert to BGR format
        # enhanced_page = enhance_image(open_cv_image)
        # cv2.imwrite(image_path, enhanced_page)
        elements = partition(image_path, languages=['vie'])  # 'vie' is for Vietnamese
        page_content = {'page_number': i+1, 'content': clean_text_with_gemini("\n".join([str(el) for el in elements]))}
        pdf_content.append(page_content)
    shutil.rmtree(output_folder)
    return pdf_content
    