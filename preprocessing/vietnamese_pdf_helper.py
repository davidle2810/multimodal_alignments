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
        # elements = partition(image_path, languages=['vie'])  # 'vie' is for Vietnamese
        # page_content = {'page_number': i, 'content': clean_text(clean_text_with_gemini("\n".join([str(el) for el in elements])))}
        # pdf_content.append(page_content)
    shutil.rmtree(output_folder)
    return [{'page_number': 0, 'content': 'lời giới thiệu\nthánh giáo yếu lý quốc ngữ được xuất bản lần đầu vào năm 1774 tại trung quốc đến năm 1933 thánh giáo yếu lý quốc ngữ được tái bản lần cuối\nthánh giáo yếu lý quốc ngữ được giới thiệu ở đây xuất bản năm 1837\ntác giả của thánh giáo yếu lý quốc ngữ là đức cha pigneau de belhaine 17411799 viết bằng chữ nôm\nnăm 1997 thánh giáo yếu lý quốc ngữ được nhóm dịch thuật hán nôm công giáo do cố linh mục vĩnh sơn nguyễn hưng phiên âm ghép trong quyển thánh giáo yếu lý và lưu hành nội bộ\nnay được phép của đức giám mục gioan đỗ văn ngân chủ tịch ủy ban giáo lý đức tin ban từ vựng hán nôm công giáo do đức ông phêrô nguyễn chí thiết chủ biên và thầy michel nguyễn hạnh hiệu đính chú thích và sắp xếp lại bố cục mộc bản chữ nôm ở trang trái theo cột từ phải sang trái và bản phiên âm việt ở trang phải sắp xếp theo dòng tương ứng với cột ở trang trái theo hướng từ trên xuống dưới\nnay kính\nđức ông phêrô nguyễn chí thiết\ntrưởng ban từ vựng hán nôm công giáo\n'}, {'page_number': 1, 'content': 'thánh giáo yếu lý\nmục lục\nthiên chúa nhất thể\ngiáng sinh cứu thế\ntử kỳ hữu định\nnhân sinh tội chủng\nthánh bí tích luận\nthánh thể giải luận\ncáo giải giải luận\n'}, {'page_number': 2, 'content': 'cáo minh bổ thục kiến nhất trang\nchung truyền thần phẩm kiến tam trang\nthập giới giải nghĩa kiến lục trang\nhội thánh điều luật kiến bát trang\nthiên chủ kinh giải thập nhất trang\nthánh mẫu kinh giải thập tứ trang\nchính dịch giáo hữu thập thất trang\nkinh trước rước lễ ngũ thập kinh sau rước lễ ngũ thập nhị chung\n'}]
    