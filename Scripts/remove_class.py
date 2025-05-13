#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 15:02:03 2024

@author: u2260235
"""

def remove_class(mask_dir, prob_csv_dir, output_dir, class_to_remove):
    import numpy as np
    import pandas as pd
    import tifffile as tf
    import os
    
    os.makedirs(output_dir, exist_ok=True) # creates output folder
    for filename in os.listdir(mask_dir): # goes through every file
        if filename.endswith(".tiff"):
            print(f"Processing file: {filename}")
            mask_path = os.path.join(mask_dir, filename)
            # get basename (without "_m" attached)
            basename = filename.replace('_masks.tiff', '')
            # create other paths
            prob_csv_path = os.path.join(prob_csv_dir, basename + '_mask_classes.csv')
            
            output_path = os.path.join(output_dir, basename + '_masks.tiff')
            
            masks = tf.imread(mask_path)  # Shape: (time, height, width)
            classes = pd.read_csv(prob_csv_path)
            masks_revised = np.copy(masks)
            for i in range(masks.shape[0]):  # frame
                frame_masks = masks[i]
                frame_classes = classes[classes["frame"]==i]
        
                # Filter for mask IDs where the class is 0 (background)
                background_mask_ids = frame_classes.loc[frame_classes["class_id"] == 0, "mask_id"].to_numpy()
        
                # Set pixels in masks_revised to 0 for all background mask IDs
                for mask_id in background_mask_ids:
                    masks_revised[i][frame_masks == mask_id] = 0
        
            # Save the processed masks as a multi-page TIFF
            tf.imwrite(output_path, masks_revised, photometric='minisblack')
            print(f"Saved {output_path}")
