#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 09:33:59 2025

@author: u2260235
"""

import numpy as np
import os
import pandas as pd

track_dir = '/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Data/cell_families_csv'
branch_properties_dir = '/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Data/branch_properties'


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
        family_id = current_branch['family_id'].iloc[0]
        division_code = current_branch['division_code'].iloc[0]
        start_frame = current_branch['fr'].iloc[0]
        end_frame = current_branch['fr'].iloc[-1]
        frames = end_frame-start_frame+1
        start_class = current_branch['class_id'].iloc[0]
        end_class = current_branch['class_id'].iloc[-1]
        edge = current_branch['edge'].iloc[0]
        
        branch_dict={'branch_id':[branch_id]
                     ,'family_id':[family_id]
                     ,'division_code':[division_code]
                     ,'start_frame':[start_frame]
                     ,'end_frame':[end_frame]
                     ,'frames':[frames]
                     ,'start_class':[start_class]
                     ,'end_class':[end_class]
                     ,'edge':[edge]
                     }
        current_branch=pd.DataFrame(branch_dict)
        branches_list.append(current_branch) # adds this to the list of branches
    #convert the list of dfs to a proper single df
    branches=pd.concat(branches_list, ignore_index=True)
    return branches

#%%
os.makedirs(branch_properties_dir, exist_ok=True) # creates output folder

track_files=getfilelist(track_dir, 'csv')
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
    track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
    branch_properties_path = branch_properties_dir + '/' + basenames[file_id] + '_branches.csv'
    branches = pd.DataFrame(columns=['branch_id', 'family_id', 'division_code', 'start_frame', 'end_frame', 'start_class', 'end_class'])

    
    tracks = pd.read_csv(track_path)
    branches = getbranches(tracks)
    
    