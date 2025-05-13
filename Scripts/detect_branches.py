def detect_branches(track_dir, family_dir, max_search_radius):
    import numpy as np
    import pandas as pd
    import networkx as nx
    import os

    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def detect_possible_mitosis(tracks, frames_checked=4, dead_allowed=2):
        track_ids = np.unique(tracks['track_id'])
        for track_id in track_ids:
            current_track = tracks.loc[(tracks['track_id'] == track_id)]
            # mitotic=2, dead=3
            # list for higher efficiency
            frame_indices = current_track.index.to_list()
            class_ids = current_track['class_id'].to_list()
            frames = current_track['fr'].to_list()
            
            for i, frame in enumerate(frames):
                checked_frames = np.arange(frame, frame+frames_checked)
                # corresponding class_ids
                class_ids_checked = current_track[current_track['fr'].isin(checked_frames)]['class_id'].values
                
                total_checked = len(class_ids_checked)
                dead_count = np.sum(class_ids_checked == 3)
                total_count = np.sum(class_ids_checked == 2) + dead_count
                # check if all are mitotic/dead and no more than a certain amound dead
                if total_count==total_checked and dead_allowed >= dead_count:
                    tracks.at[frame_indices[i], 'm_detected'] = True
                
        return tracks
    
    #%%
    os.makedirs(family_dir, exist_ok=True) # creates output folder
    
    track_files=getfilelist(track_dir, 'csv')
    basenames = [
        os.path.basename(file).replace("_tracks.csv", "")
        for file in track_files
    ]
    
    files_branch_total = 0
    files_branch_parent_found_total = 0
    
    for file_id in range(len(basenames)): # goes through every file
        print(f'Processing file: {basenames[file_id]}')
        track_path = track_dir + '/' + basenames[file_id] + '_tracks.csv'
        save_path = family_dir + '/' + basenames[file_id] + '_tracks.csv'
        
        tracks = pd.read_csv(track_path)
        #print(f"Columns in {track_path}: {tracks.columns.tolist()}")
        
        
        branch_total = 0
        branch_parent_found_total = 0
        
        #%%
        # Assigns edges to existing tracks
        tracks['m_detected']=False      
        tracks['family_id']=np.nan
        tracks['division_code']=np.nan
        tracks['targets']=np.nan # id of child cells

        #frames0 = frames[frames != np.max(frames)] # logical indexing to remove last frame
        
        # identfies frames where the cell appears to have just divided
        detect_possible_mitosis(tracks)
        

        # Saves tracks file
        tracks.to_csv(save_path, index=False)
        '''
        # Check success rate
        print(f'=== Search radius: {max_search_radius} ===')
        print(f'Total branches detected: {branch_total}')
        print(f'Total branches resolved: {branch_parent_found_total}')
        print('\n')
        # increment total resolved and detected counts
        files_branch_total = files_branch_total + branch_total
        files_branch_parent_found_total = files_branch_parent_found_total + branch_parent_found_total
    resolved_percent = (files_branch_parent_found_total/files_branch_total)*100
    print(f'Resolved/Detected: {files_branch_parent_found_total}/{files_branch_total} ({resolved_percent}%)')
    '''
