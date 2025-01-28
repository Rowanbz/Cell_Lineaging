#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:59:21 2025

@author: u2260235
"""

import numpy as np
import csv
import os

csv_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/6_mask_classes_csv"
file = "240408_240411_WT_150nM_pos33_mask_classes.csv"

csv_path = os.path.join(csv_dir, file)  # Add a filename to the directory path
probs=[]

with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        probs.append(row)  # Each row is appended as a list

# 0-frame, 1-mask_id, 2-class_id,
# 3-p_background, 4-p_interphase, 5-p_mitotic, 6-p_dead
#z=probs[0][0]

fr=0
median=1
#result=0
z=probs[1][0]

# select row where column 0 == fr and column 1 == median
for i in range(1,len(probs)):
    #print(row)
    #print(i)
    # check current frame and mask_id
    if int(probs[i][0]) == fr and int(probs[i][1]) == median:
        p_interphase = (probs[i][4])
        p_mitosis = (probs[i][5])
        p_death = (probs[i][6])  # Select the value in column 6
        print('x')
        
        #Processing file: 240408_240411_WT_DMSO_pos1