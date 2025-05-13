#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 10:18:38 2025

@author: u2260235
"""

def cellpose_segmentation(input_folder, output_folder, diam1, diam2, area, overlap_threshold, min_area=0, area_buffer=700, save_stacks=False, skip_existing=False):
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

    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def segment_movie(stack_path, diam):
        stack = tifffile.imread(stack_path)
        # To collect processed images for the current stack
        processed_masks = []
        # Loop through each image in the stack and process with Cellpose
        for i in range(len(stack)):
            img = stack[i]
            masks, flows, styles, diams = model.eval(img, diameter=diam, channels=chan, batch_size=8)
            print(f"Progress: {i+1}/{len(stack)}")
            # Keep masks as 16-bit to preserve all IDs
            processed_masks.append(masks.astype(np.uint16))
        # Convert list of 8-bit arrays to a single 8-bit array stack
        processed_masks_stack = np.stack(processed_masks).astype(np.uint16)
        # FOR TESTING save this mask:
        tifffile.imwrite
        return processed_masks_stack
        
    def merge_stacks(small_stack, large_stack, area, overlap_threshold, area_buffer, min_area):
        # add all masks with area < area from small_masks and all with area > area from large_masks
        # also has option to exclude masks smaller than a certain size
        merged_masks = [] #creates output array
        debug_masks = [] #creates output to show source of each mask
        
        for fr in range(small_stack.shape[0]):  # goes through every frame
            s_current_frame = small_stack[fr]
            l_current_frame = large_stack[fr]
            
            # Create set of small masks (larger than min_area, smaller than area + buffer)
            small_segmentation = filter_and_assign_masks(s_current_frame, min_area=min_area, max_area=area)            
            small_segmentation_buffer = filter_and_assign_masks(s_current_frame, min_area=area, max_area=area + area_buffer)
            
            # Create set of large masks (larger than area - buffer, no max threshold)
            large_segmentation = filter_and_assign_masks(l_current_frame, min_area=area, max_area=float('inf'))
            large_segmentation_buffer = filter_and_assign_masks(l_current_frame, min_area=area-area_buffer, max_area=area)
            
            # Combine small and large masks sets for this frame
            # output is an array of 2 (merged and debug)
            merged_frame, debug_frame = concat_frame(large_segmentation, large_segmentation_buffer, small_segmentation, small_segmentation_buffer, overlap_threshold)
            
            merged_masks.append(merged_frame)
            # save debug
            debug_masks.append(debug_frame)
        return merged_masks

    def filter_and_assign_masks(source_frame, min_area, max_area, dtype=np.uint16):
        #Create a filtered segmentation mask based on area thresholds.
        mask_ids = np.unique(source_frame[source_frame != 0])
        segmentation = np.zeros_like(source_frame, dtype=dtype)
        for mask_id in mask_ids:
            mask_pixels = source_frame == mask_id
            mask_area = np.sum(mask_pixels)
            if min_area < mask_area < max_area:
                segmentation[mask_pixels] = mask_id
        return segmentation
    
    def concat_frame(large_segmentation, large_segmentation_buffer, small_segmentation, small_segmentation_buffer, overlap_threshold):
        # Add in the following order:
        # 1. large_segmentation
        # 2. small_segmentation
        # 3. large_segmentation_buffer
        # 4. small_segmentation_buffer
    
        merged_masks = np.copy(large_segmentation)
        debug_mask_sources = (merged_masks > 0).astype(np.uint8)  # 1 for large_segmentation
        existing_ids = set(np.unique(merged_masks[merged_masks != 0]))
        next_id = max(existing_ids, default=0) + 1
    
        source_maps = [small_segmentation, large_segmentation_buffer, small_segmentation_buffer]
        source_ids = [2, 3, 4]  # Corresponding source colors
    
        for seg, source_id in zip(source_maps, source_ids):
            merged_masks, debug_mask_sources, existing_ids, next_id = add_masks_nonoverlapping(
                merged_masks, seg, debug_mask_sources, source_id, existing_ids, next_id, overlap_threshold
            )
    
        return merged_masks, debug_mask_sources

    
    def add_masks_nonoverlapping(target, new_segmentation, debug_mask_sources, source_id, existing_ids, next_id, overlap_threshold):
        # Adds masks from new_segmentation to target if they don't significantly overlap.
        # updates debug_mask_sources to track the origin (1-4).

        mask_ids = np.unique(new_segmentation[new_segmentation != 0])
        target_binary = target > 0
    
        for mask_id in mask_ids:
            mask_pixels = new_segmentation == mask_id
            mask_area = np.sum(mask_pixels)
            if mask_area == 0:
                continue
    
            overlap_pixels = np.logical_and(mask_pixels, target_binary)
            overlap_ratio = np.sum(overlap_pixels) / mask_area
    
            if overlap_ratio < overlap_threshold:
                assigned_id = mask_id if mask_id not in existing_ids else next_id
                if assigned_id == next_id:
                    next_id += 1
                target[mask_pixels] = assigned_id
                debug_mask_sources[mask_pixels] = source_id  # color by source
                existing_ids.add(assigned_id)
    
        return target, debug_mask_sources, existing_ids, next_id

            
    #%%     
    ### 1. Process all files
    
    os.makedirs(output_folder, exist_ok=True) # creates output folder

    if save_stacks: #outpyt folders for testing
        folder_split_stacks = output_folder+'_split'
        os.makedirs(folder_split_stacks, exist_ok=True)

    input_files=getfilelist(input_folder, 'tiff')
    basenames = [
        os.path.basename(file).replace(".tiff", "")
        for file in input_files
    ]
    print(basenames)
    for basename in basenames:
        # Define output filename and path early
        output_path = os.path.join(output_folder, basename + '_masks.tiff')

        # Skip processing if output already exists and skip_existing is True
        if skip_existing and os.path.exists(output_path):
            print(f"Skipping {basename} (output already exists)")
            continue

        # Load the image stack
        stack_path = os.path.join(input_folder, basename + '.tiff')
        print(f"Processing: {basename}")
        print(f"Processing with diameter {diam1} and buffer {area_buffer}")
        small_masks = segment_movie(stack_path, diam1)

        print(f"Processing with diameter {diam2} and buffer {area_buffer}")
        large_masks = segment_movie(stack_path, diam2)
        
        # Save for testing
        if save_stacks:
            path_small = os.path.join(folder_split_stacks, basename + f'_d{diam1}.tiff')
            path_large = os.path.join(folder_split_stacks, basename + f'_d{diam2}.tiff')
            tifffile.imwrite(path_small, small_masks, photometric='minisblack')
            tifffile.imwrite(path_large, large_masks, photometric='minisblack')

        # Merge the segmentation results
        merged_masks = merge_stacks(small_masks, large_masks, area, overlap_threshold, area_buffer, min_area)

        # Save the processed masks as a tiff
        merged_masks = np.array(merged_masks, dtype=np.uint16)
        tifffile.imwrite(output_path, merged_masks, photometric='minisblack')
        print(f"Saved {basename}")

                
