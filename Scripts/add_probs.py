#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 19:01:09 2024

@author: u2260235
"""

def mask_probs(mask_dir, prob_dir, csv_dir, mask_classes_dir, save_mask_classes=False, save_classes_csv=True, debris_size = 200, skip_existing=False):
    import numpy as np
    import pandas as pd
    import tifffile as tf
    import os
    #print(os.listdir(prob_dir))
    
    os.makedirs(prob_dir, exist_ok=True) # creates output folder
    os.makedirs(mask_classes_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    for filename in os.listdir(prob_dir): # goes through every file
        if filename.endswith(".tiff"):
            print(f"Processing file: {filename}")
            prob_path = os.path.join(prob_dir, filename)
            # get basename (without "_prob" attached)
            basename = filename.replace('_probs.tiff', '')
            # create other paths
            mask_path = os.path.join(mask_dir, basename + '_masks.tiff')
            mask_classes_path = os.path.join(mask_classes_dir, basename + '_masks_classes.tiff')
            csv_path = os.path.join(csv_dir, basename + '_mask_classes.csv')
            
            # check if these exist and if they need to be processed if not
            must_process_mask_classes = True
            must_process_csv = True
            
            # if it needs to be processed and the file does not exist
            if save_mask_classes==False or (os.path.exists(mask_classes_path)):
                must_process_mask_classes = False
            if save_classes_csv==False or (os.path.exists(csv_path)):
                must_process_csv = False
            # not checking 4_mask_probs as not in use
            # Skip if both these files exist (or are not needed):
            if skip_existing and must_process_mask_classes==False and must_process_csv==False:
                print(f"Skipping {filename} (output already exists)")
                continue
                
        
            # load probability and mask files
            class_probs = tf.imread(prob_path)  # Shape: (frame, channel, height, width)
            masks_3d = tf.imread(mask_path)  # Shape: (time, height, width)
        
            # create output arrays
            mask_classes = np.zeros_like(masks_3d, dtype=np.uint16)  # Shape: (frame, height, width)
            mask_probabilities = np.zeros_like(class_probs, dtype=np.float64)  # Shape: (frame, channel, height, width)
            channel_mask_classes = np.zeros_like(class_probs, dtype=np.float64)  # Shape: (frame, channel, height, width)
            csv_data = []
        
            for j in range(masks_3d.shape[0]):  # goes through every frame
                frame_seg = masks_3d[j]  # Shape: (height, width)
                frame_probs = class_probs[j]  # Shape: (channel, height, width)
        
                # get array of all mask IDs (excluding background with value 0)
                mask_ids = np.unique(frame_seg[frame_seg != 0])
        
                # create empty table for masks with all 4 class probs
                mask_mean_probs = np.zeros((len(mask_ids), class_probs.shape[1]))  # Shape: (num_masks, num_channels)
        
                # Calculate mean probabilities for each mask and channel
                for i, mask_id in enumerate(mask_ids):
                    mask_pixels = frame_probs[:, frame_seg == mask_id]  # Pixels for each channel
                    #mask_mean_probs[i] = mask_pixels.mean(axis=1)  # Mean probability per channel
                    # Using median instead as there are outliers
                    mask_mean_probs[i] = np.median(mask_pixels, axis=1)
  # Mean probability per channel
        
                # Assign class IDs based on the highest mean probability
                max_channels = np.argmax(mask_mean_probs, axis=1)
        
                # Assign mask classes and collect data for CSV
                for i, mask_id in enumerate(mask_ids):
                    mask_channel = max_channels[i]
                    mask_classes[j][frame_seg == mask_id] = mask_channel  # Assign to mask_classes (frame-level)
        
                    # Set mean probabilities in mask_probabilities
                    for channel in range(class_probs.shape[1]):
                        if channel == mask_channel:
                            mask_probabilities[j, channel][frame_seg == mask_id] = mask_mean_probs[i, channel]
        
                    # Assign to the appropriate channel in channel_mask_classes
                    channel_mask_classes[j, mask_channel][frame_seg == mask_id] = 1
        
                    # Collect CSV data for this mask
                    csv_data.append([j, mask_id, mask_channel] + mask_mean_probs[i].tolist())
        
        
                print(f"Frame progress for {basename}: {j + 1}/{masks_3d.shape[0]}")
        
            # save mask_classes
            if save_mask_classes == True:
                add_probs_save_mask_classes(mask_classes, mask_classes_path)
                
            # save classes as separate channels
            ### These are only used for class overlay which with a standardised funciton is probably now unnecessary
            
            # save as csv
            if save_classes_csv == True:
                add_probs_save_csv(csv_data, csv_path, class_probs)
        
def add_probs_save_mask_classes(mask_classes, mask_classes_path):
    import tifffile as tf
    tf.imwrite(mask_classes_path, mask_classes, photometric='minisblack')
    print(f"Saved class labelled masks: {mask_classes_path}")

def add_probs_save_csv(csv_data, csv_path, class_probs):
    import pandas as pd
    column_names = ['frame', 'mask_id', 'class_id'] + [f'class_{i}_prob' for i in range(class_probs.shape[1])]
    csv_df = pd.DataFrame(csv_data, columns=column_names)
    csv_df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")
