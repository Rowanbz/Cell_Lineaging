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

# Directories
mask_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/2_masks"
prob_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/3_probs"
output_mask_probs = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/4_mask_probs"
output_mask_classes = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/5_mask_classes"
output_csv_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/6_mask_classes_csv"
output_mask_classes_separate = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/8_mask_classes_separate"

DOmaskprobs = True
DOmaskclasses = True
DOcsd = True
DOmaskclassesseparate = True

# Reorder files to match basenames
mask_files = [
    os.path.join(mask_dir, f)
    for f in os.listdir(mask_dir)
    if f.endswith('.tiff') and "_masks" in f
]
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]
prob_files = [
    os.path.join(prob_dir, f)
    for f in os.listdir(prob_dir)
    if f.endswith('.tiff') and "_prob" in f
]
prob_files_map = {
    os.path.basename(file).replace("_prob.tiff", ""): file
    for file in prob_files
}
prob_files = [prob_files_map[basename] for basename in basenames if basename in prob_files_map]

for file_indx in range(len(mask_files)):
    print(f"Processing file: {basenames[file_indx]}")

    # Load probability and mask files
    class_probs = tf.imread(prob_files[file_indx])  # Shape: (frame, channel, height, width)
    masks_3d = tf.imread(mask_files[file_indx])  # Shape: (time, height, width)

    # Prepare output arrays
    mask_classes = np.zeros_like(masks_3d, dtype=np.uint8)  # Shape: (frame, height, width)
    mask_probabilities = np.zeros_like(class_probs, dtype=np.float64)  # Shape: (frame, channel, height, width)
    channel_mask_classes = np.zeros_like(class_probs, dtype=np.float64)  # Shape: (frame, channel, height, width)
    csv_data = []

    for j in range(masks_3d.shape[0]):  # Frame
        frame_seg = masks_3d[j]  # Shape: (height, width)
        frame_probs = class_probs[j]  # Shape: (channel, height, width)

        # Get unique mask IDs (excluding background with value 0)
        mask_ids = np.unique(frame_seg[frame_seg != 0])

        # Preallocate probabilities for all masks and channels
        mask_mean_probs = np.zeros((len(mask_ids), class_probs.shape[1]))  # Shape: (num_masks, num_channels)

        # Calculate mean probabilities for each mask and channel
        for i, mask_id in enumerate(mask_ids):
            mask_pixels = frame_probs[:, frame_seg == mask_id]  # Pixels for each channel
            mask_mean_probs[i] = mask_pixels.mean(axis=1)  # Mean probability per channel

        # Assign class IDs based on the highest mean probability
        max_channels = np.argmax(mask_mean_probs, axis=1)  # Dominant class per mask

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


        print(f"Frame progress for {basenames[file_indx]}: {j + 1}/{masks_3d.shape[0]}")

    # Save mask_probs
    file_output_mask_probs = os.path.join(output_mask_probs, f"{basenames[file_indx]}_mask_probs.tiff")
    tf.imwrite(file_output_mask_probs, mask_probabilities, metadata={'axes': 'TCYX'})
    print(f"Saved: {file_output_mask_probs}")
    
    # Save mask_classes
    file_output_mask_classes = os.path.join(output_mask_classes, f"{basenames[file_indx]}_mask_classes.tiff")
    tf.imwrite(file_output_mask_classes, mask_classes, photometric='minisblack')
    print(f"Saved: {file_output_mask_classes}")
    
    # Save classes as separate channels
    file_output_mask_classes_separate = os.path.join(output_mask_classes_separate, f"{basenames[file_indx]}_mask_classes_separate.tiff")  
    tf.imwrite(file_output_mask_classes_separate, channel_mask_classes, metadata={'axes': 'TCYX'})
    print(f"Saved: {file_output_mask_classes_separate}")

    # Save CSV file
    csv_file = os.path.join(output_csv_dir, f"{basenames[file_indx]}_mask_classes.csv")
    column_names = ['frame', 'mask_id', 'class_id'] + [f'class_{i}_prob' for i in range(class_probs.shape[1])]
    csv_df = pd.DataFrame(csv_data, columns=column_names)
    csv_df.to_csv(csv_file, index=False)
    print(f"Saved CSV: {csv_file}")


"""
ChatGPT Optimisations:
Eliminate Redundant Loops:

Instead of looping over channels and frames separately, we compute the mean probabilities for all channels in a single operation using NumPy's slicing and mean().
Vectorized Probability Calculation:

Use frame_probs[:, frame_seg == mask_id] to slice pixels directly for all channels at once, avoiding the need to loop over channels.
Preallocation:

Preallocate the mask_mean_probs array to store mean probabilities for all masks and channels in one step.
Efficient Class Assignment:

Use np.argmax() on mask_mean_probs to determine the dominant class for all masks in a frame at once, avoiding iterative comparisons.
Minimized DataFrame Operations:

Group and export data only once, directly appending rows to csv_data for later DataFrame creation.
Reduced Memory Overhead:

Avoid redundant copies of arrays. For example, instead of mask_probabilities (not used later), focus on mask_classes and the CSV export.

"""