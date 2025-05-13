#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 10:18:38 2025

@author: u2260235
"""

def cellpose_segmentation(input_folder, output_folder, diam1, diam2, area, min_area, overlap_threshold):
    import os
    import tifffile
    from cellpose import models
    import numpy as np
    from wakepy import keep
    
    #diam1 = 30
    #diam2 = 60
    #area = 3000
    #min_area = 300
    
    # currently saving as uint16. 255 seems slightly to low for the number of masks
    
    
    # Load the Cellpose model (configure for your GPU/CPU setup)
    model = models.Cellpose(model_type='cyto3')
    
    # Define channels for Cellpose processing
    chan = [[0, 0]]
    
    ### carry out Cellpose segmentation with stack_path and diameter=diam1/2
    def segment_movie(stack_path, diam):
        stack = tifffile.imread(stack_path)
        # To collect processed images for the current stack
        processed_masks = []
        # Loop through each image in the stack and process with Cellpose
        for i in range(len(stack)):
            img = stack[i]
            masks, flows, styles, diams = model.eval(img, diameter=diam, channels=chan)
            print(f"Progress: {i+1}/{len(stack)}")
            # Convert mask to 8-bit
            masks_8bit = masks.astype(np.uint8)
            # Append the mask to the list for multi-page TIFF
            processed_masks.append(masks_8bit)
        # Convert list of 8-bit arrays to a single 8-bit array stack
        processed_masks_stack = np.stack(processed_masks).astype(np.uint8)
        # FOR TESTING save this mask:
        tifffile.imwrite
        return processed_masks_stack
       
    # not used
    def remove_particles(masks, min_area):
        output_masks = np.zeros_like(masks, dtype=np.uint16)
        for fr in range(masks.shape[0]):  # goes through every frame
            current_frame = masks[fr]
            mask_ids = np.unique(current_frame[current_frame != 0])
            for i, mask_id in enumerate(mask_ids):
                mask_pixels = current_frame == mask_id
                if len(mask_pixels) > min_area:
                    output_masks[fr][mask_pixels] = mask_id        
        return output_masks
         
        
    def merge_stacks(small_stack, large_stack, area, min_area, overlap_threshold):
        # add all masks with area < area from small_masks and all with area > area from large_masks
        # also exclude masks smaller than a certain size
        merged_masks = [] #creates output array
        
        for fr in range(small_stack.shape[0]):  # goes through every frame
            s_current_frame = small_stack[fr]
            s_mask_ids = np.unique(s_current_frame[s_current_frame != 0])
            l_current_frame = large_stack[fr]
            l_mask_ids = np.unique(l_current_frame[l_current_frame != 0])
            next_id = max(s_mask_ids) + 1
            
            # Create set of small masks
            small_segmentation = np.zeros_like(s_current_frame, dtype=np.uint16)
            for mask_id in s_mask_ids:
                mask_pixels = s_current_frame == mask_id  # boolean mask
                mask_area = np.sum(mask_pixels)
                if mask_area > min_area and mask_area < area:
                    # add this to the set of masks from the small diameter
                    small_segmentation[mask_pixels] = mask_id
            
            # Create set of large masks
            large_segmentation = np.zeros_like(l_current_frame, dtype=np.uint16)
            for mask_id in l_mask_ids:
                mask_pixels = l_current_frame == mask_id  # boolean mask
                mask_area = np.sum(mask_pixels)
                if mask_area > area:
                    # add this to the set of masks from the large diameter
                    large_segmentation[mask_pixels] = mask_id
                    
            tifffile.imwrite('small_seg.tiff', small_segmentation, photometric='minisblack')
            tifffile.imwrite('large_seg.tiff', large_segmentation, photometric='minisblack')
            # Combine small and large masks sets for this frame
            merged_masks.append(concat_frame(small_segmentation, large_segmentation, overlap_threshold))
        return merged_masks
    
    def concat_frame(small_segmentation, large_segmentation, overlap_threshold):
        # contains all large masks. Small masks then added
        merged_masks = np.copy(large_segmentation)
        s_current_frame = small_segmentation
        s_mask_ids = np.unique(s_current_frame[s_current_frame != 0])
        l_current_frame = large_segmentation
        l_mask_ids = np.unique(l_current_frame[l_current_frame != 0])
        next_id = max(l_mask_ids) + 1
        
        # Add small to large
        for mask_id in s_mask_ids:
            mask_pixels = small_segmentation == mask_id  # boolean mask
            mask_area = np.sum(mask_pixels)
            # Create a binary mask of large regions for overlap detection
            large_binary = l_current_frame > 0  
            # check if this is overlapping with a large mask
            # this can be a problem for cells near the threshold area
            overlap_pixels = np.logical_and(mask_pixels, large_binary)
            overlap_ratio = np.sum(overlap_pixels) / mask_area  # Fraction overlap
            if overlap_ratio < overlap_threshold:
                # check if this id is already in use
                if mask_id in l_mask_ids:
                    # if this mask_id is already used
                    assigned_id = next_id
                    # books out this id and moves onto the next
                    next_id += 1
                else:
                    assigned_id = mask_id
                # add the assigned_id to the result image
                merged_masks[mask_pixels] = assigned_id
        return merged_masks
                
            
    #%%
    ### 1. Process all files
    with keep.running():  # Keeps code running for a long time without interruption
        # Loop through each file in the folder
        for filename in os.listdir(input_folder):
            if filename.endswith(".tif") or filename.endswith(".tiff"):
                # Load the image stack (multi-page TIFF)
                stack_path = os.path.join(input_folder, filename)
                print(f"Processing: {filename}")
                print(f"Processing with diameter {diam1}")
                small_masks = segment_movie(stack_path, diam1)
                # save for testing
                #tifffile.imwrite(f"//Users/u2260235/Documents/Y3 Project/segmentation_test_030325/masks/d{diam1}_{filename}", small_masks, photometric='minisblack')
                
                print(f"Processing with diameter {diam2}")
                large_masks = segment_movie(stack_path, diam2)
                # save for testing
                #tifffile.imwrite(f"//Users/u2260235/Documents/Y3 Project/segmentation_test_030325/masks/d{diam2}_{filename}", large_masks, photometric='minisblack')
          
                # merge 2 segmentation results
                merged_masks = merge_stacks(small_masks, large_masks, area, min_area, overlap_threshold)
    
                # Create the output filename with "_masks" appended
                output_filename = os.path.splitext(filename)[0] + "_masks.tiff"
                output_path = os.path.join(output_folder, output_filename)
        
                # Save the processed masks as a multi-page TIFF
                merged_masks = np.array(merged_masks, dtype=np.uint16)
                tifffile.imwrite(output_path, merged_masks, photometric='minisblack')
                print(f"Saved {output_filename}")
