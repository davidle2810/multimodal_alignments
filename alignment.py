import preprocessing.sinonom_pdf_helper as sn
import preprocessing.vietnamese_pdf_helper as vn
import preprocessing.translate_sn2vn
import os
import random
import argparse
from random import seed as seed
from laserembeddings import Laser
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
parser = argparse.ArgumentParser('Sentence alignment using sentence embeddings and FastDTW',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--src', type=str, required=True,
                    help='path_to_source_document')

parser.add_argument('--tgt', type=str, required=True,
                    help='path_to_target_document')

parser.add_argument('-o', '--output', type=str, required=True,
                    help='path_to_output_folder')

args = parser.parse_args()
laser = Laser()

def get_content_from_bitext(sn_file, vn_file):
    sn_content = sn.extract_pages(sn_file)
    vn_content = vn.extract_pages(vn_file)
    return sn_content, vn_content

def paragraph_alignment(sn2vn_content,vn_content):
    source_embeddings = laser.embed_sentences('\n'.join([' '.join(page['content'].split('\n')) for page in sn2vn_content]), lang='vi')  # or "en" if your source is in English, etc.
    target_embeddings = laser.embed_sentences('\n'.join([' '.join(page['content'].split('\n')) for page in vn_content]), lang='vi')  # adapt the language code as needed
    source_embeddings = np.array(source_embeddings)
    target_embeddings = np.array(target_embeddings)
    alignment_results = list()
    similarities = cosine_similarity(source_embeddings, target_embeddings)
    for i, source_page in enumerate(sn2vn_content):
        best_j = np.argmax(similarities[i])
        best_score = similarities[i, best_j]
        target_page = vn_content[best_j]
        
        alignment_results.append({
            'source_page_number': source_page['page_number'],
            'source_text': source_page['content'],
            'target_page_number': target_page['page_number'],
            'target_text': target_page['content'],
            'similarity_score': float(best_score)
        })
    return alignment_results


        
def main():
    tmp_dir = '/tmp' + str(random.randint(0, 100))
    while os.path.isdir(tmp_dir):
        tmp_dir = '/tmp' + str(random.randint(0, 100))
    os.mkdir(tmp_dir)  
    sn_file = args.src_file
    vn_file = args.tgt_file
    sn_content, vn_content = get_content_from_bitext(sn_file,vn_file)
    sn2vn_content = list()
    for page in sn_content:
        sn2vn_content.append({'page_number': page['page_number'], 'content': '\n'.join([line['transliteration'] for line in page['content']])})
    paragraph_alignments = paragraph_alignment(sn2vn_content,vn_content)
    for idx, alignment in enumerate(paragraph_alignments):
        src_id = alignment['source_page_number']
        tgt_id = alignment['target_page_number']
        path_temp_file_sn2vn = os.path.join(tmp_dir, f"sn2vn_{idx}.txt")
        path_temp_file_vn = os.path.join(tmp_dir, f"vn_{idx}.txt")
        output_file = os.path.join(tmp_dir, f"aligned_{idx}.txt")  
        with open(path_temp_file_sn2vn, "w", encoding="utf-8") as f:
            f.write(sn2vn_content[src_id]['content'])
        with open(path_temp_file_vn, "w", encoding="utf-8") as f:
            f.write(vn_content[tgt_id]['content'])
        script = os.environ['vecalign'] + '/sentence_alignments/align.sh' 
        print(f"Running: {script}")
        os.system(script)