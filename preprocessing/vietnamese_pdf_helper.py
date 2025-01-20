from unstructured.partition.auto import partition
import google.generativeai as genai
import os
import shutil
from pdf2image import convert_from_path
#pytesseract.pytesseract.tesseract_cmd = r"mnt/c/users/Quoc Anh/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
genai.configure(api_key='AIzaSyDX5tM_HRPoFl7pCQxZ97WwICMCFwtsGqc')
model = genai.GenerativeModel('gemini-1.5-pro')
import re
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

def clean_text(input_text):
    clean_text_list =  re.sub(r'\n\n+', '\n', re.sub(r'[^\w\s]', '', input_text.lower())).split('\n')
    for i in range(len(clean_text_list)):
        clean_text_list[i]=re.sub(r'\s+', ' ',clean_text_list[i].strip())
    return '\n'.join(clean_text_list)

def convert_to_bw(image, threshold=128):
    gray_image = image.convert('L')    
    # Apply thresholding to create a binary (black and white) image
    bw_image = gray_image.point(lambda p: p > threshold and 255)
    return bw_image


def extract_pages(file_name: str) -> list:
    """
    Extracts the QN text from each page of the provided file.
    :param file_name: The path to the NS file.
    :return: A list of dictionaries, where each dictionary represents a page in the file and contains:
        - 'page_number': An integer representing the page index (starting from 0).
        - 'content': A cleaned text
    """
    # Convert PDF to images
    pages = convert_from_path(file_name, 600)  # 300 DPI for better quality
    pdf_content = list()
    output_folder='./data/images_viet'
    if os.path.exists(output_folder) and os.path.isdir(output_folder):
        os.system(f'rm -r {output_folder}')
    os.makedirs(output_folder)

    # Save each page as an image
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i}.png")  # Save as PNG
        convert_to_bw(page).save(image_path, 'PNG')
        elements = partition(image_path, languages=['vie'])  # 'vie' is for Vietnamese
        page_content = {'page_number': i, 'content': clean_text(clean_text_with_gemini("\n".join([str(el) for el in elements])))}
        pdf_content.append(page_content)
    shutil.rmtree(output_folder)
    return pdf_content
    