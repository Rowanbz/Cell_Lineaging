#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 19:01:09 2024

@author: u2260235
"""
import numpy as np
import pandas as pd
import tifffile as tf
import os

mask_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/2_masks"
prob_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/3_probs"
output_mask_probs = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/4_mask_probs"
output_mask_classes = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/5_mask_classes"

mask_files = [
    os.path.join(mask_dir, f)
    for f in os.listdir(mask_dir)
    if f.endswith('.tiff') and "_masks" in f
]
prob_files = [
    os.path.join(prob_dir, f)
    for f in os.listdir(prob_dir)
    if f.endswith('.tiff') and "_prob" in f
]
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]


# classes are 0:background, 1:interphase, 2:mitotic, 3:dead

# process all files in directory
for file_indx in range(len(mask_files)):
    class_probs = tf.imread(prob_files[file_indx])  # Shape: (frame, channel, height, width) -> (3, 4, 1200, 1200)
    masks_3d = tf.imread(mask_files[file_indx])  # Shape: (time, height, width) -> (4, 1200, 1200)
    
    # Increase dimensions of masks to fit number of classes
    masks = np.repeat(np.expand_dims(masks_3d, axis=1), class_probs.shape[1], axis=1)


    # dataFrame containing the mean probabilities (based on previous steps)
    columns = ['frame', 'mask_id', 'mean_prob', 'median_prob', 'std_prob']
    results = []
    for j in range(masks.shape[0]): #frame
        for i in range(masks.shape[1]): #channel
            frame_seg = masks[j,i]
            frame_probs = class_probs[j,i]
            
            # Get unique mask IDs (excluding background with value 0)
            mask_ids = np.unique(frame_seg)
            mask_ids = mask_ids[mask_ids != 0]  # exclude background
            
            # Calculate statistics for each mask
            for mask_id in mask_ids:
                mask_pixels = frame_probs[frame_seg == mask_id]
                mean_prob = np.mean(mask_pixels)
                results.append([j, i, mask_id, mean_prob])
        print("Frame progress for"+basenames[file_indx]+": {j+1}/{masks.shape[0]}")
        
    
    # Convert results to a DataFrame
    df_means = pd.DataFrame(results, columns=['frame', 'channel', 'mask_id', 'mean_prob'])
    
    # Create a new array to store the updated mask stack with mean probabilities
    mask_probabilities = np.zeros_like(masks, dtype=np.float64)
    
    # Replace mask values with the corresponding mean probability
    for j in range(masks.shape[0]):
        for i in range(masks.shape[1]):
            frame_seg = masks[j,i]
            
            # Filter the DataFrame to get the current frame and channel data
            frame_df = df_means[(df_means['frame'] == j) & (df_means['channel'] == i)]
            
            # Iterate through each mask in the current channel
            for _, row in frame_df.iterrows():
                mask_id = row['mask_id']
                mean_prob = row['mean_prob']
                
                # Set the new mask values for this mask_id to the mean probability
                mask_probabilities[j,i][frame_seg == mask_id] = mean_prob
    
    # export the result to a TIFF file
    # need to work out baze name so it can be saved as a variant
    tf.imwrite(str(output_mask_probs)+str(basenames[file_indx]+'mask_probs.tiff'), mask_probabilities, metadata={'axes': 'TCYX'})
    # The file 'mask_probabilities.tiff' now contains the updated mask stack with mean probabilities for each cell.

#%%
# Colour cells by class
     
# GROUP BY mask_id
# For each mask_id, store a list with the mean_prob for each class
# (frame, channel, mask_id, mask_probs(array))
# Assign class based on position in mask_probs


mask_probs=[]
mask_classes = np.zeros_like(masks_3d, dtype=np.float64)

for j in range(masks.shape[0]):  # Frame
    frame_df = df_means[df_means['frame'] == j]
    mask_grouped_frame = frame_df.groupby("mask_id")
    
    for mask_id, group in mask_grouped_frame:
        # find channel with highest mean_prob
        highest_channel = group.loc[group['mean_prob'].idxmax()]
        max_channel = highest_channel['channel']
        mask_probs.append((j, mask_id, max_channel))

# convert list to dataframe
mask_classes_df = pd.DataFrame(mask_probs, columns=['frame', 'mask_id', 'channel'])

# replace mask values in mask_classes with the corresponding class_id for each frame
for i in range(masks_3d.shape[0]):  # Frame
    frame_seg = masks_3d[i]
    frame_mask_classes = mask_classes_df[mask_classes_df['frame'] == i]
    
    # iterate through each mask_id in the current frame
    for _, row in frame_mask_classes.iterrows():
        mask_id = row['mask_id']
        class_id = row['channel']
        
        # set mask value to correct class_id
        mask_classes[i][frame_seg == mask_id] = class_id

# Export the result to a TIFF file
tf.imwrite('mask_cell_classification.tiff', mask_classes, metadata={'axes': 'TYX'})
