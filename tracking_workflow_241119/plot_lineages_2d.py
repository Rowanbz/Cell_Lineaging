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

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

def normalisearray (movie, maxval):
    # converts array to have values from 0-maxval
    if np.min(movie) < 0:
        movie_pos = movie + np.min(movie)
    else: movie_pos = movie
    movie_norm = (movie_pos-np.min(movie_pos))/(np.max(movie_pos)-np.min(movie_pos))
    #movie_norm = np.round(movie_norm * maxval) # runs very slow
    movie_norm = (movie_norm * maxval).astype(np.uint8) # runs very slow
    return movie_norm
    
#%%

source_files=getfilelist(source_dir, 'tiff')
track_files=getfilelist(track_dir, 'csv')

for file_indx in range(len(track_files)): # goes through every file
    print("Processing file: {track_files[file_indx]}")
    # Initialise tracks
    tracks = pd.read_csv(track_files[file_indx])
    movie_32bit = tf.imread(source_files[file_indx])
    
    # normalise data to be in 0-255 range
    
    movie_255 = normalisearray(movie_32bit, 255)
        
    movie_rgb = np.stack([movie_255] * 3, axis=1)  # frames, CHANNELS, height, width
    
    track_ids = tracks["track_id"].unique().tolist() # list of track ids
    for track_id in range(len(track_ids)):
        current_tr = tracks.loc[tracks['track_id'] == track_id]
        current_tr = current_tr.sort_values('fr')
        frames = current_tr['fr'].unique() # get list of all frames - skips spaces
        for i in range(len(frames) - 1):
            frame_id = frames[i]
            next_frame_id = frames[i+1]
            #print(f"track: {track_id}, frame: {frame_id}")
            x1 = int(current_tr.loc[current_tr['fr'] == frame_id, 'X'].iloc[0])
            y1 = int(current_tr.loc[current_tr['fr'] == frame_id, 'Y'].iloc[0])
            x2 = int(current_tr.loc[current_tr['fr'] == next_frame_id, 'X'].iloc[0])
            y2 = int(current_tr.loc[current_tr['fr'] == next_frame_id, 'Y'].iloc[0])
            # draw line on current frame of movie
            movie_frame_num = len(movie_rgb[:,0,0])
            for j in range(movie_frame_num):
                cv2.line(movie_rgb[j], (x1, y1), (x2, y2), color=(0,0,255), thickness=2)
                # cv2 uses BGR colour
    tf.imwrite('movie.tiff', movie_rgb, imagej=True, metadata={'axes': 'ZCYX'})