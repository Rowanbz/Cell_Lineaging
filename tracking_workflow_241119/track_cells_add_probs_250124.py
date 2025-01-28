#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 10:58:22 2025

@author: u2260235
"""

import numpy as np
import pandas as pd
import os

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list
#%%

track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/3_tracks"
prob_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/6_mask_classes_csv"
save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/5_tracks_revised"

track_files=getfilelist(track_dir, 'csv')
basenames = [
    os.path.basename(file).replace("_tracks.csv", "")
    for file in track_files
]

#basenames = ['240408_240411_WT_150nM_pos33']

for file_id in range(len(basenames)): # goes through every file
    print(f'Processing: {basenames[file_id]}')
    track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
    prob_path = prob_dir + '/' + basenames[file_id] + '_mask_classes.csv'
    save_path = save_dir + '/' + basenames[file_id] + '_tracks.csv'
    
    tracks = pd.read_csv(track_path)
    tracks= tracks.sort_values(['fr', 'mask_id'])
    probs = pd.read_csv(prob_path)
    probs['frame'] = probs['frame'] + 1 # add 1 so frames in sync
    probs = probs.sort_values(['frame', 'mask_id'])

# Carry our a left join
    df = pd.merge(tracks, probs, left_on=['fr', 'mask_id'],
        right_on=['frame', 'mask_id'], how='left'  # keeps all columns
    )
    df = df.drop(columns=['frame'])
    df = df.sort_values(['track_id', 'fr'])
    #df.fillna(0, inplace=True)
    
    df.to_csv(save_path, index=False)
    print(f'Saved: {basenames[file_id]}')
    