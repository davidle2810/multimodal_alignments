#!/bin/bash
export LASER='/mnt/d/LASER'
# Generate overlap files
python ./sentence_alignments/overlap.py -i data/test.tr -o data/overlaps.tr -n 8
python ./sentence_alignments/overlap.py -i data/test.vn -o data/overlaps.vn -n 8

# Remove existing embedding files (if any)
rm -f data/overlaps.tr.emb data/overlaps.vn.emb

# Generate embeddings for the overlap files
sh ../LASER/tasks/embed/embed.sh data/overlaps.tr data/overlaps.tr.emb
sh ../LASER/tasks/embed/embed.sh data/overlaps.vn data/overlaps.vn.emb

# Perform vector alignment
python ./sentence_alignments/vecalign.py \
    --alignment_max_size 8 \
    --src data/test.tr \
    --tgt data/test.vn \
    --src_embed data/overlaps.tr data/overlaps.tr.emb \
    --tgt_embed data/overlaps.vn data/overlaps.vn.emb
