#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:35:52 2025

@author: u2260235
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as sim
import tifffile as tf
import os

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

min_size = 20  # Pixels
shrink_parameter = 10

#%%

mask_dir = '/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/7_revised_masks'
save_dir = '/Users/u2260235/Documents/Y3 Project/mask_erosion_250218/1_masks_eroded'

mask_files=getfilelist(mask_dir, 'tiff')
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]

### errode masks of input mask file
def erode_masks(mask_path):
    masks = tf.imread(mask_path)
    masks_eroded = np.zeros(masks.shape)
    for fr in range(masks.shape[0]): # goes through every frame
        current_frame = masks[fr]  
        
        # Structuring element for erosion
        element = np.array([[0,1,0], [1,1,1], [0,1,0]], dtype=bool)
        
        # Create an empty array for the eroded mask
        eroded_frame = np.zeros_like(current_frame)
        
        for mask_id in np.unique(current_frame):
            if mask_id == 0:
                continue  # skip background
            # Create a binary mask for the current label
            binary_mask = (current_frame == mask_id)
        
            # Measure the size of the mask
            if np.sum(binary_mask) < min_size:
                eroded_frame[binary_mask] = mask_id  # Keep the small mask unchanged
                continue  
        
            # Erode the binary mask
            eroded_binary_mask = sim.binary_erosion(binary_mask, element, iterations=shrink_parameter)
        
            # Ensure the mask is not entirely lost
            if np.sum(eroded_binary_mask) == 0:
                eroded_frame[binary_mask] = mask_id
            else:
                eroded_frame[eroded_binary_mask] = mask_id
        masks_eroded[fr] = eroded_frame
    return masks_eroded

### repeat erosion function and save for every file
basenames = ['240408_240411_WT_150nM_pos33']
for file_id in range(len(basenames)): # goes through every file
    print(f"Processing file: {basenames[file_id]}")
    mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
    save_path = save_dir + '/' + basenames[file_id] + '_masks_10px.tiff'
    #save_path = save_dir + '/' + basenames[file_id] + '_masks.tiff'

    masks_eroded = erode_masks(mask_path)
    tf.imwrite(save_path, masks_eroded)
    print(f'Saved: {basenames[file_id]}')

# Plot the result
#fig, myaxes = plt.subplots(1,2)
#myaxes[0].imshow(current_frame, cmap='gray')  # Display as grayscale
#myaxes[1].imshow(eroded_frame, cmap='gray')  # Display as grayscale
#plt.show()