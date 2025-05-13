#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:59:59 2025

@author: u2260235
"""

def cell_mask_label(mask_dir, track_dir, save_dir, column_name):
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
    mask_files=getfilelist(mask_dir, 'tiff')
    basenames = [
        os.path.basename(file).replace("_masks.tiff", "")
        for file in mask_files
    ]
    
    #%%
    os.makedirs(save_dir, exist_ok=True) # creates output folder
    
    for file_id in range(len(basenames)): # goes through every file
        mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
        track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
        save_path = save_dir + '/' + basenames[file_id] + '_masks.tiff'
    
        print(f"Processing file: {mask_files[file_id]}")
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
                label_id = tracks.loc[(tracks['fr'] == fr + 1) & (tracks['mask_id'] == i), column_name]
                if len(label_id) == 0: # spots with no associated track
                    # [0,0,mask_id,fr,0,0,False,0,0,0,''] # whole row
                    # this is for masks that do not have an associated track
                    # so are not passed by the Jython script
                    # this can be removed if these rows are later included in script
                    label_id=-1
                else: # spots with track
                    label_id = label_id.iloc[0]
                
                blank_frame[current_frame == i] = label_id + 1
            masks[fr] = blank_frame # save mask to movie
            
        tf.imwrite(save_path, masks)
        print(f"Saved: {save_path}")