#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 13:31:52 2025

@author: u2260235
"""

import numpy as np
import pandas as pd
import os
import tifffile as tf
import cv2

source_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/1_source"
track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/3_tracks"

#%%



# select files
track_files = [
    os.path.join(track_dir, f)
    for f in os.listdir(track_dir)
    if f.endswith('.csv')
]
source_files = [
    os.path.join(source_dir, f)
    for f in os.listdir(source_dir)
    if f.endswith('.tiff')
]
# reorder files
basenames = [
    os.path.basename(file).replace("_tracks.csv", "")
    for file in track_files
]
track_files_map = {
    os.path.basename(file).replace("_tracks.csv", ""): file
    for file in track_files
}
track_files = [track_files_map[basename] for basename in basenames if basename in track_files_map]
#%%

for file_indx in range(len(track_files)): # goes through every file
    print("Processing file: {track_files[file_indx]}")
    # Initialise tracks
    tracks = pd.read_csv(track_files[file_indx])
    movie = tf.imread(source_files[file_indx])
    track_ids = tracks["track_id"].unique().tolist() # list of track ids
    current_track=0
    for track_id in range(len(track_ids)):
        current_tr = tracks.loc[tracks['track_id'] == track_id]
        fr_min = int(current_tr['fr'].min())
        fr_max = int(current_tr['fr'].max())
        frames = np.arange(fr_min, fr_max+1)
#        current_frame = tracks.loc[tracks['track_id'] == track_id and tracks['fr'] == frame]