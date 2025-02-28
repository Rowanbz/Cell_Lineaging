#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 00:22:52 2025

@author: u2260235
"""

import os
import numpy as np
import tifffile as tf

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

def process_mask(mask_path, prob_path, save_path):
    """
    Process a mask file and overlay it with probability data.
    Saves a new TIFF where each mask region is colored by the class with the highest median probability.
    """
    # Load probability and mask files
    class_probs = tf.imread(prob_path)  # Shape: (frame, channel, height, width)
    masks = tf.imread(mask_path)  # Shape: (frame, height, width)

    # Create output array
    mask_classes = np.zeros_like(masks, dtype=np.uint8)  # Shape: (frame, height, width)

    for fr in range(masks.shape[0]):  # Iterate through each frame
        frame_seg = masks[fr]  # Shape: (height, width)
        frame_probs = class_probs[fr]  # Shape: (channel, height, width)

        # Get array of all mask IDs (excluding background with value 0)
        mask_ids = np.unique(frame_seg[frame_seg != 0])
        
        # Create empty table for masks with all class probabilities
        mask_median_probs = np.zeros((len(mask_ids), class_probs.shape[1]))  # (num_masks, num_channels)

        # Calculate median probabilities for each mask and channel
        for i, mask_id in enumerate(mask_ids):
            mask_pixels = frame_probs[:, frame_seg == mask_id]  # Pixels for each channel
            mask_median_probs[i] = np.mean(mask_pixels, axis=1)  # Median probability per channel

        # Assign class IDs based on the highest median probability
        max_channels = np.argmax(mask_median_probs, axis=1)

        # Assign mask classes
        for i, mask_id in enumerate(mask_ids):
            mask_classes[fr][frame_seg == mask_id] = max_channels[i]  # Assign class to mask region

        print(f"Frame progress: {fr + 1}/{masks.shape[0]}")
    return mask_classes

### 1. Set directories
mask_dir = "/Users/u2260235/Documents/Y3 Project/mask_erosion_250218/1_masks_eroded"
prob_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/3_probs"
save_dir = "/Users/u2260235/Documents/Y3 Project/mask_erosion_250218/2_mask_classes"


mask_files=getfilelist(mask_dir, 'tiff')
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]
#basenames = ['240408_240411_WT_150nM_pos33']

### 2. Process each file
for basename in basenames:
    print(f"Processing file: {basename}")
    mask_path = os.path.join(mask_dir, f"{basename}_masks_10px.tiff")
    prob_path = os.path.join(prob_dir, f"{basename}_prob.tiff")
    save_path = os.path.join(save_dir, f"{basename}_mask_classes_10px.tiff")
    
    mask_classes = process_mask(mask_path, prob_path, save_path)
    # Save the mask classes file
    tf.imwrite(save_path, mask_classes, photometric='minisblack')
    print(f"Saved: {save_path}")
