from unstructured.partition.auto import partition
import google.generativeai as genai
import os
import shutil
from pdf2image import convert_from_path
import re

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
        page_content = {'page_number': i, 'content': clean_text("\n".join([str(el) for el in elements]))}
        pdf_content.append(page_content)
    shutil.rmtree(output_folder)
    return pdf_content
    
    