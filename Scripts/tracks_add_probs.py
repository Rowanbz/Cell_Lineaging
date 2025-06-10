#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 10:58:22 2025

@author: u2260235
"""
def add_probs_to_tracks(track_dir, classes_dir, save_dir):
    import pandas as pd
    import numpy as np
    import os
    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
            
            # after each row, look at the next 3 in the track (make this a variable so can be changed). If they are all the same AND different to class_id for the last row, change to this new class_id. Otherwise, keep previous class_id (remeber to account for rows at end of track)
            
            # after this, go through every track again. If a row is class 3 (dead), but class_id == 1 (interphase) later in the same track, instead change these rows to class_id = 2 (mitotic). This serves as a way of validating dead detection as it should never progress from that state. If it does then it has been misidentified.

    
    def refine_classes(df, search_size=3):
        df.rename(columns={'class_id': 'class_id_raw'}, inplace=True)
        df['interphase'] = False
        df['class_id'] = np.nan
        #df['search_classes'] = np.nan #for testing
        track_ids = np.unique(df['track_id'])
    
        # First pass: Assign starting class and apply transition logic
        for track_id in track_ids:
            current_tr = df[df['track_id'] == track_id].copy()
            starting_class_id = current_tr.iloc[0]['class_id_raw'] # may need to look at multiple frames
            starting_spot_id = current_tr.iloc[0]['spot_id']
            
            # differentiate interphase from everything else
            if starting_class_id == 1: #interphase
                df.loc[df['spot_id'] == starting_spot_id, 'interphase'] = True
            else:
                df.loc[df['spot_id'] == starting_spot_id, 'interphase'] = False

    
            # Iterate through each row in the track
            for idx in range(len(current_tr)):
                current_row = current_tr.iloc[idx]
                current_spot_id = current_row['spot_id']
                currently_interphase = df.loc[df['spot_id'] == current_spot_id, 'interphase'].values[0] if not df.loc[df['spot_id'] == current_spot_id, 'interphase'].empty else np.nan

    
                # Assign the current class to avoid NaN propagation
                #df.loc[df['spot_id'] == current_spot_id, 'class_id'] = current_class_id
    
                # Check 'search_size' rows
                if idx + 1 >= len(current_tr):
                    continue  # Avoid accessing out-of-range indices
    
                # Define search window
                search_window = current_tr.iloc[idx + 1 : idx + 1 + search_size]
    
                if len(search_window) == 0:
                    continue  # No rows left to check
    
                # Extract classes in search window
                search_classes = search_window['class_id_raw'].values
                unique_classes = np.unique(search_classes)
    
                # Identify next spot_id for updating
                next_spot_id = search_window.iloc[0]['spot_id']
                
                # test
                #df.loc[df['spot_id'] == next_spot_id, 'search_classes'] = str(search_classes)
    
                # Apply class update logic
                # if no unanimous change in class
                if len(unique_classes) > 1:
                    df.loc[df['spot_id'] == next_spot_id, 'interphase'] = currently_interphase
                
                # elif unique_classes[0] == 1 (interphase)
                elif unique_classes[0] == 1:
                    df.loc[df['spot_id'] == next_spot_id, 'interphase'] = True
                
                # elif unique_classes[0] != 1 (not interphase)
                elif unique_classes[0] != 1:
                    df.loc[df['spot_id'] == next_spot_id, 'interphase'] = False
                    
                # else error
                else:
                    print('Error - interphase not assigned')
                    # Assign mitotic/dead classes in non-interphase regions
        df = assign_non_interphase(df, search_size=search_size) # process mitotic and dead
        df = cleanup_dead(df) # check if cells are falsely labelled as dead
        
        df = df[df['mask_id'] != 0] # drops bg if it is somehow in a track (pos7)
        df['class_id'] = df['class_id'].fillna(1) # bg row. If it has been detected as a mask we assume it is dim interphase???

        return df
    
    def assign_non_interphase(df, search_size=3):
        non_interphase = df[df['interphase'] == False].copy()
    
        for track_id in np.unique(non_interphase['track_id']):
            current_tr = non_interphase[non_interphase['track_id'] == track_id]
            previous_class = np.nan  # Initialize for each track
    
            for idx in range(len(current_tr)):
                current_row = current_tr.iloc[idx]
                current_spot_id = current_row['spot_id']
                current_class = current_row['class_id_raw']
    
                # Restrict to valid classes
                current_class = current_class if current_class in [2, 3] else np.nan
    
                # Set `previous_class` for the first row
                if idx == 0:
                    previous_class = current_class
    
                # Define search window
                search_window = current_tr.iloc[idx + 1 : idx + 1 + search_size]
    
                # Extract valid classes in the window
                search_classes = search_window['class_id_raw'].values
                valid_classes = search_classes[(search_classes == 2) | (search_classes == 3)]
    
                # Check for unanimous class
                unique_classes = np.unique(valid_classes)
    
                if len(unique_classes) == 1:
                    unanimous_class = unique_classes[0]
                    df.loc[df['spot_id'] == current_spot_id, 'class_id'] = unanimous_class
                    previous_class = unanimous_class
                else:
                    # Assign previous_class if not unanimous
                    df.loc[df['spot_id'] == current_spot_id, 'class_id'] = previous_class
    
        # Assign interphase class as 1
        df.loc[df['interphase'] == True, 'class_id'] = 1
    
        return df

    def cleanup_dead(df):
        # if dead but the same cell is mitotic or interphase later in the same track, change to next most probable class
        track_ids = np.unique(df['track_id'])
        for track_id in track_ids:
            current_tr = df[df['track_id'] == track_id]
    
            # Identify dead rows in the track
            dead_rows = current_tr[current_tr['class_id'] == 3]
    
            for idx in dead_rows.index:
                # Check if there is a later interphase (1) in the track
                later_rows = current_tr.loc[idx + 1:]
                # Ensure we're only checking non-NaN entries
                if any(later_rows['class_id'].fillna(-1) != 3):
                    # Correct dead (3) to mitotic (2)
                    df.loc[idx, 'class_id'] = 2
        return df

        
    #%%
    
    os.makedirs(track_dir, exist_ok=True) # creates output folder
    os.makedirs(classes_dir, exist_ok=True)
    os.makedirs(save_dir, exist_ok=True)
    
    track_files=getfilelist(track_dir, 'csv')
    basenames = [
        os.path.basename(file).replace("_tracks.csv", "")
        for file in track_files
    ]
    
    #basenames = ['240408_240411_WT_150nM_pos33']
    print('Concatenating track and probability files')
    
    for file_id in range(len(basenames)): # goes through every file
        print(f'Processing: {basenames[file_id]}')
        track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
        classes_path = classes_dir + '/' + basenames[file_id] + '_mask_classes.csv'
        save_path = save_dir + '/' + basenames[file_id] + '_tracks.csv'
        
        tracks = pd.read_csv(track_path)
        tracks= tracks.sort_values(['fr', 'mask_id'])
        probs = pd.read_csv(classes_path)
        probs['frame'] = probs['frame'] + 1 # add 1 so frames in sync
        probs = probs.sort_values(['frame', 'mask_id'])
    
        # Carry our a left join
        df = pd.merge(tracks, probs, left_on=['fr', 'mask_id'],
            right_on=['frame', 'mask_id'], how='left'  # keeps all columns
        )
        df = df.drop(columns=['frame'])
        df = df.sort_values(['track_id', 'fr'])
        #df.fillna(0, inplace=True)
        
        # Carry out a process of using cell division logic to improve classification
        df = refine_classes(df, 3)
        
        df.to_csv(save_path, index=False)
        print(f'Saved: {basenames[file_id]}')
    