#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 02:30:48 2025

@author: u2260235
"""
def prob_stacks_to_movie(prob_dir, save_dir, skip_existing=False):
    print(f"Starting probability stack concatenation from: {prob_dir}")
    import os
    import tifffile as tf
    import dask.array as da
    from dask import delayed
    import shutil
    
    def getfolderlist(path):
        return [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    
    def getfilelist(path, filetype):
        return sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.' + filetype)])
        
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    prob_dirs = getfolderlist(prob_dir)
    basenames = [os.path.basename(folder) for folder in prob_dirs]
    
    for basename in basenames:
        print(f"\n=== Processing file: {basename} ===")
    
        save_path = os.path.join(save_dir, f"{basename}_probs.tiff")
        prob_folder = os.path.join(prob_dir, basename)
    
        if skip_existing and os.path.exists(save_path):
            print(f"Skipping {basename} — output already exists.")
            continue
    
        prob_stacks = getfilelist(prob_folder, 'tiff')
        stack_number = len(prob_stacks)
    
        print(f"Found {stack_number} slices in {prob_folder}")
        print("Loading slices (Dask)")
    
        # Preview one frame to get shape and dtype
        sample = tf.imread(prob_stacks[0])
        shape = sample.shape
        dtype = sample.dtype
    
        # Prepare delayed loaders
        lazy_arrays = []
        for i, path in enumerate(prob_stacks):
            #print(f" - Scheduling frame {i+1}/{stack_number}: {os.path.basename(path)}")
            delayed_load = delayed(tf.imread)(path)
            lazy_array = da.from_delayed(delayed_load, shape=shape, dtype=dtype)
            lazy_arrays.append(lazy_array)
    
        # Stack all slices into one time-series array
        stack = da.stack(lazy_arrays, axis=0)  # shape: (T, C, Y, X) or similar
    
        print(f"Computing Dask array (this may take a moment)...")
        array = stack.compute()  # Now we trigger the actual loading
        print(f"Finished loading and stacking for {basename}")
    
        print(f"Saving TIFF to {save_path}")
        tf.imwrite(save_path, array, imagej=True, metadata={'axes': 'TCYX'})
        print(f"Saved: {save_path}")
        
        # Optionally delete the folder
        shutil.rmtree(prob_folder)
