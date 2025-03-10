#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 13:24:00 2024

@author: u2260235
"""
import os
import tifffile
from cellpose import models
import numpy as np
from wakepy import keep  # Assuming 'keep' is a utility for handling long-running code

with keep.running():  # Keeps code running for a long time without interruption
    
    # Load the Cellpose model (configure for your GPU/CPU setup)
    model = models.Cellpose(model_type='cyto3')
    
    # Specify the folder containing the TIFF files
    input_folder = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/1_source"
    output_folder = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/2_masks"
    
    # Define channels for Cellpose processing
    chan = [[0, 0]]
    
    # Loop through each file in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".tif") or filename.endswith(".tiff"):
            # Load the image stack (multi-page TIFF)
            stack_path = os.path.join(input_folder, filename)
            stack = tifffile.imread(stack_path)
    
            # To collect processed images for the current stack
            processed_masks = []
            
            # Loop through each image in the stack and process with Cellpose
            for i in range(len(stack)):
                img = stack[i]
                masks, flows, styles, diams = model.eval(img, diameter=50, channels=chan)
                print(f"Progress for {filename}: {i+1}/{len(stack)}")
    
                # Convert mask to 8-bit
                masks_8bit = masks.astype(np.uint8)
                
                # Append the mask to the list for multi-page TIFF
                processed_masks.append(masks_8bit)

            # Convert list of 8-bit arrays to a single 8-bit array stack
            processed_masks_stack = np.stack(processed_masks).astype(np.uint8)

            # Create the output filename with "_masks" appended
            output_filename = os.path.splitext(filename)[0] + "_masks.tiff"
            output_path = os.path.join(output_folder, output_filename)
    
            # Save the processed masks as a multi-page TIFF
            tifffile.imwrite(output_path, processed_masks_stack, photometric='minisblack')
            print(f"Saved {output_filename}")
