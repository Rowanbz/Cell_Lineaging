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
        blank_frame=np.zeros(current_frame.shape)

        # get array of all mask IDs (excluding background with value 0)
        mask_ids = np.unique(current_frame[current_frame != 0])
        for i in mask_ids:
            #print(f'frame: {fr+1}, mask: {i}')
            # Should have specific frame and mask
            track_id = tracks.loc[(tracks['fr'] == fr + 1) & (tracks['mask_id'] == i), 'family_id']
            if len(track_id) == 0: # spots with no associated track
                # [0,0,mask_id,fr,0,0,False,0,0,0,''] # whole row
                # this is for masks that do not have an associated track
                # so are not passed by the Jython script
                # this can be removed if these rows are later included in script
                track_id=-1
            else: # spots with track
                track_id = track_id.iloc[0]
            
            blank_frame[current_frame == i] = track_id + 1
        masks[fr] = blank_frame # save mask to movie
        
    tf.imwrite(save_path, masks)
    print(f"Saved: {save_path}")