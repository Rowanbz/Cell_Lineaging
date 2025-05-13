#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:28:11 2025

@author: u2260235
"""
def add_properties(source_dir, mask_dir, track_dir, save_dir, skip_existing=False):
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
    

    # branch detection is now carried out after this script so need to plot in a later one
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
    
    
    os.makedirs(save_dir, exist_ok=True) # creates output folder
    # May have to change track path depending on best version
    source_files=getfilelist(source_dir, 'tiff')

    basenames = [
        os.path.basename(file).replace(".tiff", "")
        for file in source_files
    ]

    for file_id in range(len(basenames)): # goes through every file
        print(f"Processing file: {basenames[file_id]}")
        source_path = source_dir + '/' + basenames[file_id] + '.tiff'
        mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
        track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
        save_path = save_dir + '/' + basenames[file_id] + '_tracks.csv'
        # Skip processing if output already exists and skip_existing is True
        if skip_existing and os.path.exists(save_path):
            print(f"Skipping {file_id} (output already exists)")
            continue
    
        movie = tf.imread(source_path)
        masks = tf.imread(mask_path)
        tracks = pd.read_csv(track_path)    
        
        addarea(tracks, masks)
        addintensity(tracks, masks, movie)
        
        tracks['mass'] = tracks['area']*tracks['intensity']
        
        tracks.to_csv(save_path, index=False)
