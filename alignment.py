import preprocessing.sinonom_pdf_helper as sn
import preprocessing.vietnamese_pdf_helper as vn
import ocr_correction.corrector as crt
import os
import argparse
from random import seed as seed
from laserembeddings import Laser
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import ocr_correction.corrector as crt
from xlsxwriter.workbook import Workbook

laser = Laser()

def get_content_from_bitext(sn_file, vn_file):
    sn_content = sn.extract_pages(sn_file)
    vn_content = vn.extract_pages(vn_file)
    return sn_content, vn_content

def align_paragraphs(sn2vn_content,vn_content):
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
                'source_page_number': source_page['page_number'],
                'source_text': source_page['content'],
                'target_page_number': target_page['page_number'],
                'target_text': target_page['content'],
                'similarity_score': float(best_score)
            })
    return alignment_results

def align_sentences(paragraph_alignment):
    src_paragraph_id = paragraph_alignment['source_page_number']
    tgt_paragraph_id = paragraph_alignment['target_page_number']
    path_temp_file_sn2vn = os.path.join('data', "test.no")
    path_temp_file_vn = os.path.join('data', "test.vi")
    with open(path_temp_file_sn2vn, "w", encoding="utf-8") as f:
        f.write(sn2vn_content[src_paragraph_id]['content'])
    with open(path_temp_file_vn, "w", encoding="utf-8") as f:
        f.write(vn_content[tgt_paragraph_id]['content'])
    os.chdir('./sentence_alignments')
    script = './align.sh' 
    os.system(script)
    os.chdir('../')
    with open('data/output.txt','r',encoding='utf-8') as f:
        return ''.join(f.readlines()).split('\n')
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Sentence alignment using sentence embeddings and FastDTW',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--src', type=str, required=True,
                        help='path_to_source_document')

    parser.add_argument('--tgt', type=str, required=True,
                        help='path_to_target_document')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='path_to_output_folder')

    args = parser.parse_args()
    # read the content of 2 pdf files: nom and viet
    sn_file = args.src
    vn_file = args.tgt
    output_file = args.output
    sn_content, vn_content = get_content_from_bitext(sn_file,vn_file)
    # get the transliteration of sino-nom content
    sn2vn_content = list()
    for page in sn_content:
        sn2vn_content.append({'page_number': page['page_number'], 'content': '\n'.join([line['transliteration'] for line in page['content']])})
    # align paragraphs
    paragraph_alignments = align_paragraphs(sn2vn_content,vn_content)
    # align sentences
    with Workbook(f"sample_output.xlsx") as workbook:
        worksheet   = workbook.add_worksheet(f"Result")
        font_format = workbook.add_format({'font_name': 'Nom Na Tong'})
        red         = workbook.add_format({'color': 'red', 'font_name': 'Nom Na Tong'})
        yellow      = workbook.add_format({'color': 'yellow', 'font_name': 'Nom Na Tong'})
        blue        = workbook.add_format({'color': 'blue', 'font_name': 'Nom Na Tong'})
        green       = workbook.add_format({'color': 'green', 'font_name': 'Nom Na Tong'})
        black       = workbook.add_format({'color': 'black', 'font_name': 'Nom Na Tong'})
        worksheet.write(0, 0, 'page_id', font_format)
        worksheet.write(0, 1, 'bbox', font_format)
        worksheet.write(0, 2, 'ocr', font_format)
        worksheet.write(0, 3, 'correction', font_format)
        worksheet.write(0, 4, 'nom', font_format)
        row_id = 1
        for paragraph_alignment_idx, paragraph_alignment in enumerate(paragraph_alignments):
            sentence_alignments = align_sentences(paragraph_alignment)
            src_lines = [(line['bbox'],line['content']) for line in sn_content[paragraph_alignment['source_page_number']]['content']]
            tgt_lines = vn_content[paragraph_alignment['target_page_number']]['content'].split('\n')
            for i in range(len(sentence_alignments)-1):
                src_line_id = eval(sentence_alignments[i].split(':')[0])
                tgt_line_id = eval(sentence_alignments[i].split(':')[1])
                if len(src_line_id)>0 and len(tgt_line_id)>0:
                    src_line = [(src_lines[j][0],src_lines[j][1]) for j in src_line_id]
                    tgt_line = ' '.join([tgt_lines[j] for j in tgt_line_id]).split(' ')
                    nom_line = ''.join([line[1] for line in src_line])
                    corrected_list=crt.correct(nom_line,tgt_line)
                    vie_list = tgt_line.copy()
                    for chunk in src_line:
                        page_id = paragraph_alignment['source_page_number']
                        bbox = chunk[0]
                        nom_list = list(chunk[1])
                        ocrs = []
                        corrs = []
                        qns = []
                        while len(nom_list)>0:
                            if corrected_list[0].startswith('correct:'):
                                ocrs.extend((black, nom_list[0]))
                                corrs.extend((black, corrected_list[0].split(':')[1]))
                                qns.extend((black, vie_list[0] + ' '))
                                nom_list.pop(0)
                                vie_list.pop(0)
                            elif corrected_list[0].startswith('replace:'):
                                if corrected_list[0].split(':')[1][-1]!="X":
                                    ocrs.extend((blue, nom_list[0]))
                                    corrs.extend((blue, corrected_list[0].split(':')[1][-1]))
                                    qns.extend((blue, vie_list[0] + ' '))
                                else:
                                    ocrs.extend((red, nom_list[0]))
                                    corrs.extend((red, corrected_list[0].split(':')[1][-1]))
                                    qns.extend((red, vie_list[0] + ' '))
                                nom_list.pop(0)
                                vie_list.pop(0)
                            elif corrected_list[0].startswith('delete:'):
                                ocrs.extend((red, nom_list[0]))
                                nom_list.pop(0)
                            elif corrected_list[0].startswith('insert:'):
                                corrs.extend((red, corrected_list[0].split(':')[1]))
                                qns.extend((red, vie_list[0] + ' '))
                                vie_list.pop(0)
                            corrected_list.pop(0)
                        worksheet.write(row_id, 0, page_id, font_format)
                        worksheet.write(row_id, 1, str(bbox), font_format)
                        worksheet.write_rich_string(row_id, 2, *ocrs)
                        if len(corrs)>0:
                            worksheet.write_rich_string(row_id, 3, *corrs)
                        if len(qns)>0:
                            worksheet.write_rich_string(row_id, 4, *qns)
                        row_id =  row_id + 1