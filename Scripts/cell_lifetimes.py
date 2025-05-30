#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 23:44:00 2025

@author: u2260235
"""

def calculate_cell_lifetimes(input_dir, output_dir, group_strings):
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import os
    
    def getfilelist(path, filetype):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.' + filetype)]
    
    def plot_df_beeswarm(df, title):
        plt.figure(figsize=(12, 8))
        sns.set_style("whitegrid")
        sns.swarmplot(x='condition', y='frames', data=df, alpha=0.7)
        sns.boxplot(x='condition', y='frames', data=df,
        showcaps=False,boxprops={'facecolor':'None'},
        showfliers=False,whiskerprops={'linewidth':0})
        
        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    
    branch_files = getfilelist(input_dir, 'csv')
    basenames = [os.path.basename(file).replace("_branches.csv", "") for file in branch_files]
    
    df = []

    for file_id, basename in enumerate(basenames):
        # determine the condition based on the group strings
        condition = next((group for group in group_strings if group in basename), None)
        
        # Only process files that match one of the group strings
        if not condition:
            continue

        print(f'Processing file: {basename}')
        branch_path = os.path.join(input_dir, f'{basename}_branches.csv')
        output_path = os.path.join(output_dir, f'{basename}_lifetimes_hist.png')

        # Load the data
        branches = pd.read_csv(branch_path)
        branches['filename'] = basename
        
        max_end_frame = branches['end_frame'].max()
        branches = branches[
            (branches['start_frame'] != 1) & (branches['end_frame'] != max_end_frame)
        ]
        #branches = branches[(branches['start_class'] == 2) & (branches['end_class'] == 2)]
        
        # only those between divisions
        branches = branches[(branches['divided_start'] == True) & (branches['divided_end'] == True)]
        
        branches = branches[
            branches['edge'] == False
        ]
        
        # Assign the identified condition
        branches['condition'] = condition
        print(f'Condition: {condition}, Rows: {len(branches)} \n')

        # Append to the combined data list for swarm plot
        df.append(branches)
    
    # Combine all data for the swarm plot
    if df:
        # Combine the list of DataFrames into one
        combined_df = pd.concat(df, ignore_index=True)
        combined_df.to_csv('/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Debugging/df.csv', index=False)
        
        # Calculate mean and SD for each group
        for current_condition in combined_df['condition'].unique():
            condition_df = combined_df[combined_df['condition'] == current_condition]
            condition_mean = condition_df['frames'].mean()
            condition_sd = condition_df['frames'].std()
            print(f'Condition: {current_condition}, Mean: {condition_mean:.2f}, SD: {condition_sd:.2f}')
        
        # Plot swarm plot
        plot_df_beeswarm(combined_df, title='Swarm Plot of Lifetimes by Condition')
        output_path = os.path.join(output_dir, f'lifetimes_swarm_3.png')
        plt.savefig(output_path)
        plt.close()
    