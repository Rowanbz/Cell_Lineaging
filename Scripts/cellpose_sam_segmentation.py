#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 10:18:38 2025

@author: u2260235
"""

def cellpose_segmentation(input_folder, output_folder, min_area=0, area_buffer=700,  skip_existing=False):
    import os
    import tifffile
    from cellpose import models
    import numpy as np
    
    # currently saving as uint16. 255 seems slightly to low for the number of masks
    
    
    # Load the Cellpose model (configure for your GPU/CPU setup)
    model = models.CellposeModel(gpu=True)
    
    # Define channels for Cellpose processing
    #chan = [[0, 0]]
    
    ### carry out Cellpose segmentation with stack_path and diameter=diam1/2

    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def segment_movie(stack_path):
        stack = tifffile.imread(stack_path)
        # To collect processed images for the current stack
        processed_masks = []
        # Loop through each image in the stack and process with Cellpose
        for i in range(len(stack)):
            img = stack[i]
            masks, flows, styles = model.eval(img, diameter=None, batch_size=8)
            print(f"Progress: {i+1}/{len(stack)}")
            # Keep masks as 16-bit to preserve all IDs
            processed_masks.append(masks.astype(np.uint16))
        # Convert list of 8-bit arrays to a single 8-bit array stack
        processed_masks_stack = np.stack(processed_masks).astype(np.uint16)
        return processed_masks_stack

            
    #%%     
    ### 1. Process all files
    
    os.makedirs(output_folder, exist_ok=True) # creates output folder

    input_files=getfilelist(input_folder, 'tiff')
    basenames = [
        os.path.basename(file).replace(".tiff", "")
        for file in input_files
    ]
    #print(basenames)
    for basename in basenames:
        # Define output filename and path early
        output_path = os.path.join(output_folder, basename + '_masks.tiff')

        # Skip processing if output already exists and skip_existing is True
        if skip_existing and os.path.exists(output_path):
            print(f"Skipping {basename} (output already exists)")
            continue

        # Load the image stack
        stack_path = os.path.join(input_folder, basename + '.tiff')
        print(f"Processing {basename}")
        masks = segment_movie(stack_path)

        # Save the processed masks as a tiff
        masks = np.array(masks, dtype=np.uint16)
        tifffile.imwrite(output_path, masks, photometric='minisblack')
        print(f"Saved {basename}")

                
