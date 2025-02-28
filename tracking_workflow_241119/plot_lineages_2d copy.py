#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 13:31:52 2025

@author: u2260235
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

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
def plotcell(division_code, x, default_offset, family_df):
    c_cell = family_df.loc[(family_df['division_code'] == division_code)]
    parent_code = division_code[1:]
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
            ax.plot([x, x+4*dx], [min_fr, min_fr], color='red')
    #  plot vertical line
    ax.plot([x, x], [min_fr, max_fr+1], color='red')
    #ax.text(x,min_fr-0.5,division_code, horizontalalignment='center')# label with division code
    ax.text(x,min_fr-0.55,min_fr, horizontalalignment='center')# label  min fr
    #ax.text(x,max_fr,max_fr, horizontalalignment='center')# label  max fr
    

track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/6_tracks_revised_2"
basename = '240408_240411_WT_150nM_pos34'
track_path = track_dir + '/' + basename + '_tracks.csv'
track_path = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/test_track.csv"
tracks = pd.read_csv(track_path)

tracks['division_code'] = tracks['division_code'].astype(str).str.replace('D_', '')
family_ids = np.unique(tracks['family_id'])
total_frames = np.unique(tracks['fr'])

# create axis bar for number of frames

fig, ax = plt.subplots(1,1)
offset = 5  # Initially offsets by this amount

family_id = 1
family = tracks.loc[(tracks['family_id'] == family_id)]
frames = np.unique(family['fr'])
cell_ids = np.unique(family['division_code'])
for i in range(len(cell_ids)):
    print(cell_ids[i])
    # plot cell function
    plotcell(cell_ids[i], 0, offset, family)
    


ax.invert_yaxis()
ax.set_ylabel('Frame')
#ax.set_title(f'Cell Lineages for Family {family_id}')
#ax.legend()
plt.show()