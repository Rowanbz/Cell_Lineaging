#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 09:33:59 2025

@author: u2260235
"""

def create_branches_csv(input_dir, output_dir):
    import numpy as np
    import os
    import pandas as pd
    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def getbranches(tracks):
        tracks['branch_id'] = tracks['family_id'].astype(str) + tracks['division_code'].astype(str)
        branch_ids = np.unique(tracks['branch_id'])
        branches_list=[] # empty array to collect all individual branch dataframes
        for branch_id in branch_ids:
            current_branch = tracks.loc[tracks['branch_id']==branch_id]
            
            #('branch_id','family_id','division_code','start_frame','end_frame','start_class','end_class')
            # collects all data before adding it to a dictionary
            branch_id = current_branch['branch_id'].iloc[0]
            track_id = current_branch['track_id'].iloc[0]
            family_id = current_branch['family_id'].iloc[0]
            division_code = current_branch['division_code'].iloc[0]
            start_x = current_branch['X'].iloc[0]
            start_y = current_branch['Y'].iloc[0]
            start_frame = current_branch['fr'].iloc[0]
            end_frame = current_branch['fr'].iloc[-1]
            frames = end_frame-start_frame+1
            start_class = current_branch['class_id'].iloc[0]
            end_class = current_branch['class_id'].iloc[-1]
            edge = current_branch['edge'].iloc[0]
            divided_start = divides_at_start(current_branch, tracks)
            divided_end = divides_at_end(current_branch)
            
            branch_dict={'branch_id':[branch_id]
                         ,'track_id':[track_id]
                         ,'family_id':[family_id]
                         ,'division_code':[division_code]
                         ,'start_x': [start_x]
                         ,'start_y': [start_y]
                         ,'start_frame':[start_frame]
                         ,'end_frame':[end_frame]
                         ,'frames':[frames]
                         ,'start_class':[start_class]
                         ,'end_class':[end_class]
                         ,'edge':[edge]
                         ,'divided_start':[divided_start]
                         ,'divided_end':[divided_end]
                         }
            current_branch=pd.DataFrame(branch_dict)
            branches_list.append(current_branch) # adds this to the list of branches
        #convert the list of dfs to a proper single df
        branches=pd.concat(branches_list, ignore_index=True)
        return branches
    
    def divides_at_end(current_branch):
        # Return 2 if last spot has multiple children
        targets_str = current_branch['targets'].iloc[-1]
        targets_str=str(targets_str)
        if not targets_str:
            return False
        return len(targets_str.split('_')) > 1

    def divides_at_start(current_branch, tracks):
        """Return True if this cell is a daughter of any cell in the previous frame."""
        spot_id = str(current_branch['spot_id'].iloc[0])
        start_frame = current_branch['fr'].iloc[0]
        prev_frame = start_frame - 1
    
        prev_frame_rows = tracks[tracks['fr'] == prev_frame]
    
        for targets_str in prev_frame_rows['targets']:
            targets_str=str(targets_str)
            if not isinstance(targets_str, str) or not targets_str:
                continue
            if spot_id in targets_str.split('_'):
                return True
        return False

    
    #%%
    os.makedirs(output_dir, exist_ok=True) # creates output folder
    
    track_files=getfilelist(input_dir, 'csv')
    basenames = [
        os.path.basename(file).replace("_tracks.csv", "")
        for file in track_files
    ]
    
    # needs to divide create just 1 row for every branch contianing the following info
    # id
    # parent id
    # child id
    # length
    # class at start
    # class at end
    # track has divided? - may need to only account for these sometimes
    # at edge
    
    for file_id in range(len(basenames)): # goes through every file
        print(f'Processing file: {basenames[file_id]}')
        track_path = input_dir + '/' + basenames[file_id] + '_tracks.csv'
        out_path = output_dir + '/' + basenames[file_id] + '_branches.csv'
        branches = pd.DataFrame(columns=['branch_id', 'family_id', 'division_code', 'start_frame', 'end_frame', 'start_class', 'end_class'])
    
        
        tracks = pd.read_csv(track_path)
        branches = getbranches(tracks)
        
        # Saves tracks file
        branches.to_csv(out_path, index=False)