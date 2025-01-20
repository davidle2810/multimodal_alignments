#!/bin/bash
export LASER='/mnt/d/LASER'
# Generate overlap files
python ./overlap.py -i  ../data/test.no -o ../data/overlaps.no -n 8
python ./overlap.py -i  ../data/test.vi -o ../data/overlaps.vi -n 8

# Remove existing embedding files (if any)
rm -f ../data/overlaps.no.emb ../data/overlaps.vi.emb

# Generate embeddings for the overlap files
sh ../../LASER/tasks/embed/embed.sh ../data/overlaps.no ../data/overlaps.no.emb
sh ../../LASER/tasks/embed/embed.sh ../data/overlaps.vi ../data/overlaps.vi.emb

# Perform vector alignment
python ./vecalign.py \
    --alignment_max_size 8 \
    --src ../data/test.no \
    --tgt ../data/test.vi \
    --src_embed ../data/overlaps.no ../data/overlaps.no.emb \
    --tgt_embed ../data/overlaps.vi ../data/overlaps.vi.emb
