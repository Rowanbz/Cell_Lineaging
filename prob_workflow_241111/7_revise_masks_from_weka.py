#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 15:02:03 2024

@author: u2260235
"""

import numpy as np
import pandas as pd
import tifffile as tf
import os

mask_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/2_masks"
prob_csv_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/6_mask_classes_csv"
output_folder = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/7_revised_masks"

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
    os.path.join(prob_csv_dir, f)
    for f in os.listdir(prob_csv_dir)
    if f.endswith('.csv') and "_mask_classes" in f
]
prob_files_map = {
    os.path.basename(file).replace("_mask_classes.csv", ""): file
    for file in prob_files
}
prob_files = [prob_files_map[basename] for basename in basenames if basename in prob_files_map]

for file_indx in range(len(mask_files)):
    print(f"Processing file: {basenames[file_indx]}")
    masks = tf.imread(mask_files[file_indx])  # Shape: (time, height, width)
    classes = pd.read_csv(prob_files[file_indx])
    masks_revised = np.copy(masks)
    for i in range(masks.shape[0]):  # frame
        frame_masks = masks[i]
        frame_classes = classes[classes["frame"]==i]

        # Filter for mask IDs where the class is 0 (background)
        background_mask_ids = frame_classes.loc[frame_classes["class_id"] == 0, "mask_id"].to_numpy()

        # Set pixels in masks_revised to 0 for all background mask IDs
        for mask_id in background_mask_ids:
            masks_revised[i][frame_masks == mask_id] = 0

    # Create the output filename with "_masks" appended
    output_filename = str(basenames[file_indx]) + "_masks.tiff"
    output_path = os.path.join(output_folder, output_filename)

    # Save the processed masks as a multi-page TIFF
    tf.imwrite(output_path, masks_revised, photometric='minisblack')
    print(f"Saved {output_filename}")
    #%%
"""
        for _, row in frame_classes.iterrows():
            mask_id = row["mask_id"]
            mask_class = row["class_id"]
            if mask_class == 0:  # background class
                # overrides position in masks revised with value 0 if class is 0
                masks_revised[i][frame_masks == mask_id] = 0
"""