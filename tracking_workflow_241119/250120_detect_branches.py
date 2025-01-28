#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:44:08 2025

@author: u2260235
"""

import numpy as np
import pandas as pd
import os

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list



#%%

track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/5_tracks_revised"

track_file = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/5_tracks_revised/240408_240411_WT_150nM_pos33_tracks.csv"



tracks = pd.read_csv(track_file)

frames = np.unique(tracks['fr'])
track_ids = np.unique(tracks['track_id'])
#for fr in frames:
#    current_frame = tracks.loc[(tracks['fr'] == fr)]

for track_id in track_ids:
    #print(track_id)
    current_track = tracks.loc[(tracks['track_id'] == track_id)]
    
    # Select 1st frame of track
    first_row = current_track.sort_values('fr').iloc[0]
    if first_row['fr'] != 1 and first_row['class_id'] == 2:
        print('Branch start detected:')
        print('frame: ' + str(first_row['fr']))
        print('track: ' + str(first_row['track_id']))
        
        # Select previous frame
        current_frame = tracks.loc[(tracks['fr'] == first_row['fr']-1)]
        # need to locate the spot it likely originated from in previous frame (write function)
        # need some kind of generation id e.g. 0001
        # this needs to change along the length of a track too

# Detect tracks that do not have 1st fr == 0, they must also be mitotic
# Then limit these by comparing to all spots in the previous frame - only keep if one is mitotic within a certain distance

# Consider changing track_cells_250115 so that area and mean are recorded

# Check Data:
track_check = tracks[['track_id' , 'mask_id', 'fr', 'class_id', 'X', 'Y']]
track_check = track_check.sort_values(['fr', 'track_id'])