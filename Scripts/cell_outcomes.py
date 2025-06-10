#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 11:40:57 2025

@author: u2260235
"""

def get_cell_outcomes(track_dir, branch_dir, output_dir, exclude_edges=False):
    import numpy as np
    import pandas as pd
    import os
    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def get_outcome(current_branch, branch_tracks, branch_id, last_frame, outlier_threshold):
        # divided normally
        if current_branch['divided_end'] == True:
            outcome='divided'
        # died
        elif current_branch['end_class'] == 3:
            outcome='died'
        # arrested - length of at least mean + 3SD of time between divisions but did not divide    
        elif len(branch_tracks) > outlier_threshold and (current_branch['end_class'] == 1 or current_branch['end_class'] == 2):
            outcome='arrested'
        elif (current_branch['end_class'] == 1 or current_branch['end_class'] == 2) and current_branch['end_frame'] == last_frame:
            outcome='normal'
        else:
            outcome='unknown'
            
        return outcome
    
    def length_distribution(branch_dir, basenames):
        all_frames=[]
        for basename in basenames:
            branch_path = branch_dir + '/' + basename + '_branches.csv'
            branches = pd.read_csv(branch_path)
            current_frames = branches['frames'].to_numpy()
            all_frames.append(current_frames)
        # Combine into one long 1D array
        all_frames = np.concatenate(all_frames)
        mean = np.mean(all_frames)
        std = np.std(all_frames)
        return [mean, std]
    
    def add_condition(branches, basename):
        # This is specifically for files named in the format 240522_NM_25_pos21
        # Split the filename into parts
        parts = basename.split('_')
        # cell NM or C2
        branches['cell_type'] = parts[1]
        
        # condition 25
        branches['condition'] = parts[2]
        
        return branches
            
        
    #%%
    os.makedirs(output_dir, exist_ok=True) # creates output folder
    
    branch_files=getfilelist(branch_dir, 'csv')
    basenames = [
        os.path.basename(file).replace("_branches.csv", "")
        for file in branch_files
    ]
    
    # gets mean and sd of 
    length_mean = length_distribution(branch_dir, basenames)[0]
    print(f'Mean: {length_mean}')
    length_std = length_distribution(branch_dir, basenames)[1]
    print(f'STD: {length_std}')
    
    outlier_threshold = length_mean + 2*length_std
    print(f'Outleir thershold: {outlier_threshold}')    
    
    print('Determining cell outcomes')
    for file_id in range(len(basenames)): # goes through every file
        print(f'Processing file: {basenames[file_id]}')
        track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
        branch_path = branch_dir + '/' + basenames[file_id] + '_branches.csv'
        output_path = output_dir + '/' + basenames[file_id] + '_outcomes.csv'
        
        tracks = pd.read_csv(track_path)
        branches = pd.read_csv(branch_path)
        branches['outcome']='u'
        
        # find last frame
        last_frame = np.max(tracks['fr'])
        
        # add data based on file name
        branches = add_condition(branches, basenames[file_id])
        
        # choose only branches (cell lifetimes) where there has been a division at the start
        d_branches = branches[branches['divided_start'] == True]
        
        if exclude_edges:
            d_branches = d_branches[d_branches['edge'] == False]
            
        # check each branch/cell
        branch_ids = np.unique(d_branches['branch_id'])
        for branch_id in branch_ids:
            current_branch = d_branches.loc[d_branches['branch_id']==branch_id].iloc[0]
            branch_tracks = tracks.loc[(tracks['branch_id'] == branch_id)]
            
            outcome = get_outcome(current_branch, branch_tracks, branch_id, last_frame, outlier_threshold)
            # Add this outcome to the branches df
            branches.loc[branches['branch_id'] == branch_id, 'outcome'] = outcome
            
        # Saves updated branches file
        branches.to_csv(output_path, index=False)