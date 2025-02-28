#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 17:47:16 2024

@author: u2260235
"""

import numpy as np
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'

track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/3_tracks"

allow_edges = False

# select
track_files = [
    os.path.join(track_dir, f)
    for f in os.listdir(track_dir)
    if f.endswith('.csv')
]

for file_indx in range(len(track_files)): # goes through every file
    print(f"Processing file: {track_files[file_indx]}")
    tracks = pd.read_csv(track_files[file_indx])
    track_ids = tracks["track_id"].unique().tolist() # list of track ids
    
    # add new rows for lineage_id and cell name
    tracks['lineage_id'] = pd.Series(dtype='int')
    tracks['cell'] = pd.Series(dtype='str')
    
    tracks=tracks.sort_values(by=['track_id', 'fr'])
    track_at_edge = tracks.groupby("track_id")["edge"].any()
    
    track_ids = np.array(track_ids)
    
    if not allow_edges:
        # remove rows where True in track_at_edge
        # ~ is negative condition so keep all rows where False
        tracks = tracks[~tracks["track_id"].isin(track_at_edge[track_at_edge].index)]
        #track_at_edge = track_at_edge.to_list() # converts from series to list
        track_at_edge = np.array(track_at_edge)
        track_ids = track_ids[~track_at_edge] # negative logical indexing
    
    ### Initialise lineage IDs
    current_lineage = 0
    frame1_idx = tracks[tracks["fr"] == 1] # filter rows at frame 1
    for index, row in frame1_idx.iterrows():
        # index and row not reserved keywords so could use i (int )and j (series)
        track_id = row["track_id"]
        # Update lineage_id and cell in tracks for the current track_id
        tracks.loc[tracks["track_id"] == track_id, "lineage_id"] = current_lineage
        tracks.loc[tracks["track_id"] == track_id, "cell"] = "0"
        # Increment current_lineage
        current_lineage += 1
    
    ### Assign other lineage IDs
    for i in track_ids:
        t1 = tracks[tracks["track_id"] == i]
        if t1.iloc[0]["fr"] != 1 and t1.iloc[0]["cell_class"] == 'mitotic':
            x0 = t1.iloc[0]["X"]
            y0 = t1.iloc[0]["Y"]
            d1 = np.nan # reset table of nearby cells
            r = 15 # reset search radius (pixels)
            found = False
            # FINISH THIS WITH ANOTHER SAMPLE TO TEST
            
        if t1.iloc[0]["fr"] != 1 and t1.iloc[0]["cell_class"] != 'mitotic':
            # Update lineage_id and cell in tracks for the current track_id
            tracks.loc[tracks["track_id"] == i, "lineage_id"] = current_lineage
            tracks.loc[tracks["track_id"] == i, "cell"] = "0"
            # Increment current_lineage
            current_lineage += 1
    
    ### Plot lineages in 3D
    fig = px.line_3d(tracks, x="X", y="Y", z="fr", color="lineage_id")
    fig.show()
        