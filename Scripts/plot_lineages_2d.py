#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 13:31:52 2025

@author: u2260235
"""

def plot_lineages(input_dir, output_dir):
    import numpy as np
    import pandas as pd
    import os
    import math
    import matplotlib.pyplot as plt
    
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
    ### 1. Process all files
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            print(f'Processing file: {filename}')
            output_filename = os.path.splitext(filename)[0] + "_lineages.png"
            save_path = os.path.join(output_dir, output_filename)
            track_path = os.path.join(input_dir, filename)
        
            tracks = pd.read_csv(track_path)
            
            # initialise data
            tracks['division_code'] = tracks['division_code'].astype(str).str.replace('D_', '')
            family_ids = np.unique(tracks['family_id'])
            family_n = len(family_ids)
            frames = np.unique(tracks['fr'])
            
            ncols = min(22, family_n) # max 22 cols
            nrows = math.ceil(family_n/ncols)
            
            # create axis bar for number of frames
            
            fig, axes = plt.subplots(nrows,ncols, figsize=(ncols * 1, nrows * 1))
            axes = np.array(axes).reshape(-1)  # Flatten for 1D indexing
            
            for i in range(len(family_ids)):
                ax = axes[i]
                family_id=family_ids[i]
                family = tracks.loc[(tracks['family_id'] == family_id)]
                cell_ids = np.unique(family['division_code'])
                col = py_col[i%len(py_col)]
                
                for j in range(len(cell_ids)):
                    #print(cell_ids[i])
                    # plot cell function
                    plotcell(cell_ids[j], 0, ax, offset, family, col)
        
                # Set the y-axis range to match the frame range
                ax.set_ylim(min(frames), max(frames))
            
                # Keep y-axis for the first subplot in each column
                if i % ncols == 0:
                    # Set row y-axis
                    ax.set_yticks([min(frames),max(frames)])
                    # Define minor ticks at 10% intervals
                    minor_ticks = np.linspace(min(frames), max(frames), 11) # 10% intervals  
                    # Set minor ticks
                    ax.set_yticks(minor_ticks, minor=True)
                    # Hide other axes
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                else:
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.set_yticks([])  # Hide y-ticks for other subplots
                ax.set_xticks([])  # Hide x-ticks for all subplots
                ax.invert_yaxis()  # Flip y-axis
            # Hide unused subplots
            for j in range(len(family_ids), len(axes)):
                axes[j].axis('off')
            
            #seaborn.despine(left=False, bottom=True, right=True)
        
            plt.tight_layout()
            # Change inline graphics setting in python > preferences > IPython Console > Graphics
            plt.savefig(save_path)
            plt.show()
