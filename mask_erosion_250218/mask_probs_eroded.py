#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 19:01:09 2024

@author: u2260235
"""
# NOTE TO SELF - ISSUE WITH PROBS CSV FILE: IF MASK_ID GOES ABOVE 127 IN 1 FRAME IT WRAPS AROUND TO -128

import numpy as np
import pandas as pd
import tifffile as tf
import os

def getfilelist (path, filetype):
    file_list = [os.path.froin(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list
#%%

# Directories
mask_dir = "/Users/u2260235/Documents/Y3 Project/mask_erosion_250218/1_masks_eroded"
prob_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/3_probs"
save_dir = "/Users/u2260235/Documents/Y3 Project/mask_erosion_250218/2_mask_classes"

mask_files=getfilelist(mask_dir, 'tiff')
'''
basenames = [
    os.path.basename(file).replace(".tiff", "")
    for file in mask_files
]
'''
basenames = ['240408_240411_WT_150nM_pos33']

for file_id in range(len(mask_files)): # goes through every file
    print(f"Processing file: {basenames[file_id]}")
    mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
    prob_path = prob_dir + '/' + basenames[file_id] + '_probs.tiff'
    save_path = save_dir + '/' + basenames[file_id] + '_mask_classes.tiff'

    # load probability and mask files
    class_probs = tf.imread(prob_path)  # Shape: (frame, channel, height, width)
    masks = tf.imread(mask_path)  # Shape: (time, height, width)

    # create output array
    mask_classes = np.zeros_like(masks, dtype=np.uint8)  # Shape: (frame, height, width)

    for fr in range(masks.shape[0]):  # goes through every frame
        frame_seg = masks[fr]  # Shape: (height, width)
        frame_probs = class_probs[fr]  # Shape: (channel, height, width)

        # get array of all mask IDs (excluding background with value 0)
        mask_ids = np.unique(frame_seg[frame_seg != 0])

        # create empty table for masks with all 4 class probs
        mask_mean_probs = np.zeros((len(mask_ids), class_probs.shape[1]))  # Shape: (num_masks, num_channels)

        # Calculate mean probabilities for each mask and channel
        for i, mask_id in enumerate(mask_ids):
            mask_pixels = frame_probs[:, frame_seg == mask_id]  # Pixels for each channel
            mask_mean_probs[i] = mask_pixels.mean(axis=1)  # Mean probability per channel

        # Assign class IDs based on the highest mean probability
        max_channels = np.argmax(mask_mean_probs, axis=1)

        # Assign mask classes and collect data for CSV
        for i, mask_id in enumerate(mask_ids):
            mask_channel = max_channels[i]
            mask_classes[fr][frame_seg == mask_id] = mask_channel  # Assign to mask_classes

            # Set mean probabilities in mask_probabilities
            for channel in range(class_probs.shape[1]):
                if channel == mask_channel:
                    mask_probabilities[fr, channel][frame_seg == mask_id] = mask_mean_probs[i, channel]

        print(f"Frame progress for {basenames[file_id]}: {fr + 1}/{masks.shape[0]}")

    # save mask_classes
    tf.imwrite(save_path, mask_classes, photometric='minisblack')
    print(f"Saved: {file_output_mask_classes}")
