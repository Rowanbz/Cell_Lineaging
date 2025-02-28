#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 13:31:52 2025

@author: u2260235
"""

import numpy as np
import pandas as pd
import os
import math
import matplotlib.pyplot as plt
import seaborn

py_col = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
 '#7f7f7f', '#bcbd22', '#17becf')

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list
def getoffset(full_division_code, x, default_offset):
    # remove first character - will always be 0
    division_code = full_division_code[1:]
    length = len(division_code)
    dx = default_offset
    for i in range(length):
        if division_code[i] == '0':
            x = x-dx
        if division_code[i] == '1':
            x = x+dx
        dx = dx*0.5
    return x, dx
def plotcell(division_code, x, ax, default_offset, family_df, col):
    c_cell = family_df.loc[(family_df['division_code'] == division_code)]
    min_fr = min(c_cell['fr'])
    max_fr = max(c_cell['fr'])
    # draw a vertical line from min_fr to max_fr for each frame
    # line should be offset left or right
    # Offset halves with each generation
    x_dx=[0,0]
    if len(division_code) > 1: # cells with parents
        x_dx = getoffset(division_code, 0, offset)
        x=x_dx[0]
        dx=x_dx[1]
        #parent_code = division_code[:-1]
        # check for if the daughter is the left one
        if division_code[-1] == '0':
            # link with horizontal lines
            ax.plot([x, x+4*dx], [min_fr, min_fr], color=col, linewidth=2)
        ax.text(x,min_fr-0.55,min_fr, horizontalalignment='center')# label  min fr
    else:
        ax.text(x,min_fr-0.55,family_id, horizontalalignment='center', color='gray')# label f
    #  plot vertical line
    ax.plot([x, x], [min_fr, max_fr+1], color=col, linewidth=2)
    #ax.text(x,min_fr-0.5,division_code, horizontalalignment='center')# label with division code
    #ax.text(x,min_fr-0.55,min_fr, horizontalalignment='center')# label  min fr
    #ax.text(x,max_fr,max_fr, horizontalalignment='center')# label  max fr

#%%


offset = 1  # Initially offsets by this amount
track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/6_tracks_revised_2"
save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/10_2d_lineages"

# For testing
#track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/test_track_dir"
#save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/test_track_dir"

track_files=getfilelist(track_dir, 'csv')
basenames = [
    os.path.basename(file).replace("_tracks.csv", "")
    for file in track_files
]
#basenames = ['240408_240411_WT_150nM_pos34']

for file_id in range(len(basenames)): # goes through every file
    print(f'Processing file: {basenames[file_id]}')
    track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
    save_path = save_dir + '/' + basenames[file_id] + '.png'

    tracks = pd.read_csv(track_path)
    
    # initialise data
    tracks['division_code'] = tracks['division_code'].astype(str).str.replace('D_', '')
    family_ids = np.unique(tracks['family_id'])
    family_n = len(family_ids)
    frames = np.unique(tracks['fr'])
    
    nrows = min(4, family_n) # max 4 rows
    ncols = math.ceil(family_n/nrows)
    
    # create axis bar for number of frames
    
    fig, axes = plt.subplots(nrows,ncols, figsize=(ncols * 1, nrows * 1), sharey=True)
    axes = np.array(axes).reshape(-1)  # Flatten for 1D indexing
    
    for i in range(len(family_ids)):
        ax = axes[i]
        family_id=family_ids[i]
        family = tracks.loc[(tracks['family_id'] == family_id)]
        cell_ids = np.unique(family['division_code'])
        col = py_col[i%len(py_col)]
        
        for i in range(len(cell_ids)):
            #print(cell_ids[i])
            # plot cell function
            plotcell(cell_ids[i], 0, ax, offset, family, col)
        ax.set_xticks([])  # Hide axes
        ax.set_yticks([])
    # Hide unused subplots
    for j in range(len(family_ids), len(axes)):
        axes[j].axis('off')
        
    ax.invert_yaxis()  # Flip y-axis
    
    seaborn.despine(left=True, bottom=True, right=True)
    
    # Add scale bars
    for row in range(nrows):
        ax = axes[row * ncols]  # Get the leftmost subplot in this row
        # Define x-position for scale (slightly left of the plot)
        x_pos = -1  
        # Draw vertical scale bar
        ax.vlines(x=x_pos, ymin=min(frames), ymax=max(frames), colors='black', linewidth=1)
        # Add labels for min and max frames
        ax.text(x_pos - 0.2, min(frames), min(frames), ha='center', va='bottom', fontsize=8, color='black')
        ax.text(x_pos - 0.2, max(frames), max(frames), ha='center', va='top', fontsize=8, color='black')
        # Ensure the scale is visible
        ax.set_xlim(x_pos - 0.5, ax.get_xlim()[1])  # Extend x-limits slightly

    plt.tight_layout()
    # Change inline graphics setting in python > preferences > IPython Console > Graphics
    plt.savefig(save_path)
    plt.show()
