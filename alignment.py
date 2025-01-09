import preprocessing.sinonom_pdf_helper as sn
import preprocessing.vietnamese_pdf_helper as vn
import preprocessing.translate_sn2vn
import ocr_correction.corrector as crt
import os
import random
import argparse
from random import seed as seed
from laserembeddings import Laser
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
"""parser = argparse.ArgumentParser('Sentence alignment using sentence embeddings and FastDTW',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--src', type=str, required=True,
                    help='path_to_source_document')

parser.add_argument('--tgt', type=str, required=True,
                    help='path_to_target_document')

parser.add_argument('-o', '--output', type=str, required=True,
                    help='path_to_output_folder')

args = parser.parse_args()"""
laser = Laser()

def get_content_from_bitext(sn_file, vn_file):
    sn_content = sn.extract_pages(sn_file)
    vn_content = vn.extract_pages(vn_file)
    return sn_content, vn_content

def paragraph_alignment(sn2vn_content,vn_content):
    source_embeddings = laser.embed_sentences([page['content'] for page in sn2vn_content], lang='vi')  # or "en" if your source is in English, etc.
    target_embeddings = laser.embed_sentences([page['content'] for page in vn_content], lang='vi')  # adapt the language code as needed
    source_embeddings = np.array(source_embeddings)
    target_embeddings = np.array(target_embeddings)
    alignment_results = list()
    similarities = cosine_similarity(source_embeddings, target_embeddings)
    best_i = np.argmax(similarities, axis=1)
    best_j = np.argmax(similarities, axis=0)
    for i, source_page in enumerate(sn2vn_content):
        if best_j[best_i[i]]==i:
            best_score = similarities[i][best_i[i]]
            target_page = vn_content[best_i[i]]
            
            alignment_results.append({
                'source_page_number': i,
                'source_text': source_page['content'],
                'target_page_number': best_i[i],
                'target_text': target_page['content'],
                'similarity_score': float(best_score)
            })
    return alignment_results


        
"""
def main():
    # make temp directory
    tmp_dir = '/tmp' + str(random.randint(0, 100))
    while os.path.isdir(tmp_dir):
        tmp_dir = '/tmp' + str(random.randint(0, 100))
    os.mkdir(tmp_dir)  
    # read the content of 2 pdf files: nom and viet
    sn_file = args.src_file
    vn_file = args.tgt_file
    sn_content, vn_content = get_content_from_bitext(sn_file,vn_file)
    # get the transliteration of sino-nom content
    sn2vn_content = list()
    for page in sn_content:
        sn2vn_content.append({'page_number': page['page_number'], 'content': '\n'.join([line['transliteration'] for line in page['content']])})
    # align paragraphs
    paragraph_alignments = paragraph_alignment(sn2vn_content,vn_content)
    # align sentences
    result = list()
    for idx, alignment in enumerate(paragraph_alignments):
        src_id = alignment['source_page_number']
        tgt_id = alignment['target_page_number']
        path_temp_file_sn2vn = os.path.join(tmp_dir, f"sn2vn_{idx}.txt")
        path_temp_file_vn = os.path.join(tmp_dir, f"vn_{idx}.txt")
        # output_file = os.path.join(tmp_dir, f"aligned_{idx}.txt")  
        with open(path_temp_file_sn2vn, "w", encoding="utf-8") as f:
            f.write(sn2vn_content[src_id]['content'])
        with open(path_temp_file_vn, "w", encoding="utf-8") as f:
            f.write(vn_content[tgt_id]['content'])
        script = os.environ['vecalign'] + '/sentence_alignments/align.sh' 
        print(f"Running: {script}")
        os.system(script)
        with open('data/output.txt','r',encoding='utf-8') as f:
            alignments=''.join(f.readlines()).split('\n')
        for i in range(len(alignments)):
            x = eval(alignments[i].split(':')[0])
            y = eval(alignments[i].split(':')[1])
            src_lines = [line['content'] for line in sn_content[src_id]['content']]
            tgt_lines = vn_content[tgt_id]['content'].split('\n')
            if len(x)>0 and len(y)>0:
                src_line = ''.join([src_lines[j] for j in x])
                tgt_line = ' '.join([tgt_lines[j] for j in y])
            result.append(crt.normalize_correction(crt.normalize(src_line,tgt_line.split(' '))))
    return result
    # read output file (in data/output.txt) and perform OCR correction
"""