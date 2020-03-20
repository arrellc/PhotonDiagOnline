#!/usr/bin/env bash
export PATH=/sf/photo/miniconda/bin:$PATH

source activate /sf/photo/miniconda
# python /sf/photo/src/PALM/AlvraDriftPALMOnly.py
python /sf/photo/src/PALM/AlvraPALM_BS.py
