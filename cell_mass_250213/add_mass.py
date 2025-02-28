#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:28:11 2025

@author: u2260235
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import tifffile as tf

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

def addarea (df, masks):
    # loop through each frame
    # get all mask ids for that frame THAT ARE ALSO IN DF
    for fr in range(masks.shape[0]):  # goes through every frame
        current_masks = masks[fr]
        # makes sure to only use mask_ids with a row
        #df_mask_ids = df.loc[(df['fr'] == fr + 1), 'mask_id']
        #mask_ids = df_mask_ids.to_numpy()
        mask_ids = np.unique(current_masks[current_masks != 0])
        for i, mask_id in enumerate(mask_ids):
            mask_pixels = current_masks[current_masks == mask_id]  # Pixels for each channel
            area = len(mask_pixels)
            df.loc[(df['fr'] == fr+1) & (df['mask_id'] == mask_id), 'area'] = area
    return df

def addintensity (df, masks, movie):
    for fr in range(masks.shape[0]):  # goes through every frame
        current_masks = masks[fr]
        current_frame = movie[fr]
        mask_ids = np.unique(current_masks[current_masks != 0])
        # gets bg intensity for this frame
        bg = np.median(current_frame[current_masks == 0])
        for i, mask_id in enumerate(mask_ids):
            pixel_vals = current_frame[current_masks == mask_id]  # Intensities for each mask
            intensity = np.mean(pixel_vals) - bg # Mean pixel intensity (minus bg)
            df.loc[(df['fr'] == fr+1) & (df['mask_id'] == mask_id), 'intensity'] = intensity
    return df

def plotcell(df, cell_id, y_val="mass"):
    # y_val should accept any value, try 'mass', 'area', or 'intensity'
    current_cell = df.loc[df['cell_id'] == cell_id]
    plt.plot(current_cell['fr'], current_cell[y_val])
    plt.xlabel("Frame")
    plt.ylabel(y_val.capitalize())  # Labeling the y-axis with a capitalized column name
    plt.title(f"Cell: {cell_id}, {y_val}")
    plt.show()
    
#%%

# to get size, just get the number of pixels in each mask

# overlay masks on source image
# take median of background mask as background value and subtract when working out mean intensity of each cell
# multiply by area to get mass

# should record for each row
# area
# mean_intensity
# mass

source_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/1_source"
mask_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/7_revised_masks"
# May have to change track path depending on best version
track_dir = "/Users/u2260235/Documents/Y3 Project/hmm_workflow_250213/1_hmm_tracks_logit"
save_dir = "/Users/u2260235/Documents/Y3 Project/cell_mass_250213/1_tracks"

source_files=getfilelist(source_dir, 'tiff')
basenames = [
    os.path.basename(file).replace(".tiff", "")
    for file in source_files
]
#basenames = ['240408_240411_WT_150nM_pos33']
for file_id in range(len(basenames)): # goes through every file
    print(f"Processing file: {basenames[file_id]}")
    source_path = source_dir + '/' + basenames[file_id] + '.tiff'
    mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
    track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
    save_path = save_dir + '/' + basenames[file_id] + '_tracks.csv'

    movie = tf.imread(source_path)
    masks = tf.imread(mask_path)
    tracks = pd.read_csv(track_path)    
    
    addarea(tracks, masks)
    addintensity(tracks, masks, movie)
    
    tracks['mass'] = tracks['area']*tracks['intensity']
    
    tracks.to_csv(save_path, index=False)
    
#%%
#cell_id = '16_D_01'
cell_id = '16_D_00'
plotcell(tracks, cell_id)

plotcell(tracks, cell_id, 'area')

plotcell(tracks, cell_id, 'intensity')