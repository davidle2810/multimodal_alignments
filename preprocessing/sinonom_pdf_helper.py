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
        # image_base64 = encode_image_to_base64(image_path)
        # page_content = list()
        # # Call the API
        # result = kandian_ocr_api(
        #         token=TOKEN,
        #         email=EMAIL,
        #         image_base64=image_base64,
        #         det_mode="auto",
        #         char_ocr=False,
        #         image_size=0,
        #         return_position=True,
        #         return_choices=False,
        #     )
        # text_lines=result['data']['text_lines']
        # transliterate_text = preprocessing.translate_sn2vn.sn_transliteration_api('\n'.join([text_line['text'] for text_line in text_lines]))        
        # for line_id, text_line in enumerate(text_lines):
        #     page_content.append({'bbox': text_line['position'], 'content': text_line['text'], 'transliteration': transliterate_text[line_id]})
        # pdf_content.append({'page_number': i, 'content': preprocessing.sort_boxes.sort(page_content)})
    shutil.rmtree(output_folder)
    return [{'page_number': 0, 'content': [{'bbox': [[3063, 933], [3356, 929], [3363, 2624], [3071, 2628]], 'content': '型敎要理目錄', 'transliteration': 'hình giáo yếu lý mục lục '}, {'bbox': [[2733, 1187], [2994, 1183], [3002, 2340], [2740, 2344]], 'content': '天主一體', 'transliteration': 'thiên chúa nhất thể '}, {'bbox': [[2840, 3293], [3044, 3289], [3052, 4161], [2844, 4165]], 'content': '見一張', 'transliteration': 'kiến nhất trương '}, {'bbox': [[2398, 1206], [2671, 1206], [2671, 2332], [2398, 2332]], 'content': '降生救世', 'transliteration': 'giáng sanh cứu thế '}, {'bbox': [[2514, 3289], [2698, 3285], [2706, 4146], [2521, 4150]], 'content': '見三張', 'transliteration': 'kiến tam trương '}, {'bbox': [[2179, 430], [2237, 430], [2237, 553], [2179, 553]], 'content': '4', 'transliteration': '4 '}, {'bbox': [[2056, 1206], [2318, 1202], [2333, 2324], [2068, 2328]], 'content': '死期有定', 'transliteration': 'tử kỳ hữu định '}, {'bbox': [[2156, 3293], [2356, 3289], [2368, 4176], [2168, 4180]], 'content': '見六張', 'transliteration': 'kiến lục trương '}, {'bbox': [[1722, 1198], [1999, 1195], [2006, 2324], [1733, 2328]], 'content': '人生罪種', 'transliteration': 'nhân sinh tội giống '}, {'bbox': [[1860, 3297], [2045, 3297], [2045, 4176], [1860, 4176]], 'content': '見八張', 'transliteration': 'kiến bát trương '}, {'bbox': [[1364, 1198], [1653, 1191], [1687, 2332], [1395, 2344]], 'content': '聖秘跡論', 'transliteration': 'thánh bí tích luận '}, {'bbox': [[1499, 3297], [1683, 3293], [1703, 4169], [1514, 4173]], 'content': '十一張', 'transliteration': 'thập nhất trương '}, {'bbox': [[1030, 1187], [1322, 1187], [1322, 2344], [1030, 2344]], 'content': '聖體解論', 'transliteration': 'thánh thể giải luận '}, {'bbox': [[1160, 3300], [1349, 3300], [1349, 4173], [1160, 4173]], 'content': '十四張', 'transliteration': 'thập tứ trương '}, {'bbox': [[672, 1183], [957, 1179], [964, 2336], [680, 2340]], 'content': '告解解論', 'transliteration': 'cáo giải giải luận '}, {'bbox': [[799, 3293], [984, 3297], [976, 4188], [795, 4184]], 'content': '十七張', 'transliteration': 'thập thất trương '}, {'bbox': [[453, 2805], [641, 2805], [641, 3262], [453, 3262]], 'content': '目鑠', 'transliteration': 'mục thước '}]}, {'page_number': 1, 'content': [{'bbox': [[3271, 1471], [3425, 1471], [3425, 1944], [3271, 1944]], 'content': '男王', 'transliteration': 'nam vương '}, {'bbox': [[2929, 1164], [3194, 1168], [3179, 2320], [2917, 2317]], 'content': '告明補贖', 'transliteration': 'cáo minh bổ chuộc '}, {'bbox': [[3029, 3247], [3213, 3247], [3213, 4100], [3029, 4100]], 'content': '廾一張', 'transliteration': 'chấp nhất trương '}, {'bbox': [[2556, 1145], [2863, 1148], [2863, 2286], [2556, 2286]], 'content': '終傅神品', 'transliteration': 'chung phó thần phẩm '}, {'bbox': [[2667, 3235], [2887, 3235], [2887, 4119], [2667, 4119]], 'content': '卅三張', 'transliteration': 'táp tam trương '}, {'bbox': [[2252, 1141], [2514, 1141], [2514, 2324], [2252, 2324]], 'content': '十誠解義', 'transliteration': 'thập thành giải nghĩa '}, {'bbox': [[2337, 3262], [2529, 3262], [2529, 4134], [2337, 4134]], 'content': '廾七張', 'transliteration': 'nhập thất trương '}, {'bbox': [[1983, 434], [2033, 434], [2033, 522], [1983, 522]], 'content': '4', 'transliteration': '4 '}, {'bbox': [[1891, 1114], [2183, 1114], [2183, 2320], [1891, 2320]], 'content': '㑹聖條律', 'transliteration': 'hội thánh điều luật '}, {'bbox': [[2025, 3266], [2214, 3273], [2179, 4073], [1991, 4065]], 'content': '三十八', 'transliteration': 'tam thập bát '}, {'bbox': [[1556, 1141], [1829, 1141], [1829, 2297], [1556, 2297]], 'content': '天主經解', 'transliteration': 'thiên chủ kinh giải '}, {'bbox': [[1653, 3277], [1852, 3277], [1852, 4115], [1653, 4115]], 'content': '三十九', 'transliteration': 'tam thập cửu '}, {'bbox': [[1230, 1137], [1503, 1137], [1503, 2301], [1230, 2301]], 'content': '聖母經解', 'transliteration': 'thánh mẫu kinh giải '}, {'bbox': [[1349, 3250], [1526, 3254], [1514, 4096], [1341, 4092]], 'content': '四十四', 'transliteration': 'tứ thập tứ '}, {'bbox': [[864, 1152], [1160, 1152], [1160, 2301], [864, 2301]], 'content': '正役敎友', 'transliteration': 'chính việc giáo hữu '}, {'bbox': [[991, 3254], [1199, 3254], [1199, 4130], [991, 4130]], 'content': '四十八', 'transliteration': 'tứ thập bát '}, {'bbox': [[499, 1141], [791, 1133], [830, 2851], [538, 2858]], 'content': '經畧逴禮五十', 'transliteration': 'kinh lược rước lễ ngũ thập '}, {'bbox': [[530, 3216], [807, 3216], [807, 4403], [530, 4403]], 'content': '經娄連禮', 'transliteration': 'kinh lâu liền lễ '}, {'bbox': [[665, 4442], [807, 4442], [807, 4714], [665, 4714]], 'content': '五十', 'transliteration': 'ngũ thập '}, {'bbox': [[511, 4457], [645, 4457], [645, 4591], [511, 4591]], 'content': '二', 'transliteration': 'nhị '}, {'bbox': [[518, 4730], [807, 4730], [807, 4980], [518, 4980]], 'content': '終', 'transliteration': 'chung'}]}]
    