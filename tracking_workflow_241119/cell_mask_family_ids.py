#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:59:59 2025

@author: u2260235
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import tifffile as tf
import pandas as pd

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

#%%

#mask_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/1_mask_source"
#track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/1_mask_source"

mask_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/7_revised_masks"
track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/6_tracks_revised_2"
save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/7_mask_family_id"

mask_files=getfilelist(mask_dir, 'tiff')
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]

#%%

for file_id in range(len(basenames)): # goes through every file
    mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
    track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
    save_path = save_dir + '/' + basenames[file_id] + '_family.tiff'

    print(f"Processing file: {basenames[file_id]}")
    masks = tf.imread(mask_path)
    
    tracks = pd.read_csv(track_path)
    tracks = tracks.sort_values(['fr', 'mask_id'])
    
    for fr in range(masks.shape[0]): # goes through every frame
        current_frame = masks[fr]  # Shape: (height, width)
        new_current_frame=np.zeros(current_frame.shape)

        # get array of all mask IDs (excluding background with value 0)
        mask_ids = np.unique(current_frame[current_frame != 0])
        for mask_id in mask_ids:
            #print(f'frame: {fr+1}, mask: {i}')
            # Should have specific frame and mask
            family_id = tracks.loc[(tracks['fr'] == fr + 1) & (tracks['mask_id'] == mask_id), 'family_id']
            
            if len(family_id) != 0:
                family_id = family_id.iloc[0]
                new_current_frame[current_frame == mask_id] = family_id
        
        masks[fr] = new_current_frame # save mask to movie
        
    tf.imwrite(save_path, masks)
    print(f"Saved: {save_path}")