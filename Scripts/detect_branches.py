def detect_branches(track_dir, family_dir, max_search_radius, mass_tolerance):
    import numpy as np
    import pandas as pd
    import networkx as nx
    import os

    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def find_parent(first_row, cframe, mass_tolerance):
        daughter_id = first_row['spot_id']
        daughter_mass = first_row['mass']
        x0 = first_row['X']
        y0 = first_row['Y']
        r = 0
        found = False
        
        cframe = tracks.loc[tracks['fr'] == first_row['fr'] - 1].copy()
        # Calculate distances and filter by max search radius
        cframe['distance'] = ((cframe['X'] - x0)**2 + (cframe['Y'] - y0)**2)**0.5
        parent_candidates = cframe[(cframe['distance'] <= max_search_radius) & (cframe['class_id'] == 2)]
        # Sort by distance
        parent_candidates = parent_candidates.sort_values('distance')

        # Iterate through potential parents
        for _, parent_row in parent_candidates.iterrows():
            parent_mass = parent_row['mass']
            parent_id = parent_row['spot_id']
            # Compares masses
            if mass_check(daughter_mass, parent_mass, mass_tolerance):
                return parent_id
        return None
            
            
    def mass_check(daughter_mass, parent_mass, mass_tolerance):
        conserved = False
        lower_bound = 2*daughter_mass * (1 - mass_tolerance)
        upper_bound = 2*daughter_mass * (1 + mass_tolerance)
        
        if parent_mass > lower_bound and parent_mass < upper_bound:
            conserved = True
        return conserved
            
    
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
        
        track_ids = np.unique(tracks['track_id'])
        
        branch_total = 0
        branch_parent_found_total = 0
        
        #%%
        # Assigns edges to existing tracks
        tracks['family_id']=np.nan
        tracks['division_code']=np.nan
        tracks['branch_id']=np.nan
        tracks['target_1']=np.nan
        tracks['target_2']=np.nan
        
        #frames0 = frames[frames != np.max(frames)] # logical indexing to remove last frame
        
        # assigns target for each spot in track
        for track_id in track_ids:
            ctrack = tracks.loc[(tracks['track_id'] == track_id)]
            tframes = np.unique(ctrack['fr'])
            #tframes = tframes[tframes != np.max(tframes)] # logical indexing to remove last frame
            
            for i in range(len(tframes) - 1):
                # for each frame, set target_1 to spot_id of the next frame
                next_frame = tframes[i + 1]  
                
                # get spot_id of next frame
                target_1 = ctrack.loc[(ctrack['fr'] == next_frame), 'spot_id'].iloc[0]
                
                tracks.loc[(tracks['fr'] == tframes[i]) & (tracks['track_id'] == track_id), 'target_1'] = target_1
                #print(f'track: {track_id}, frame: {tframes[i]}')
                
        
        
        #%%
        # Detects branches
        for track_id in track_ids:
            #print(track_id)
            current_track = tracks.loc[(tracks['track_id'] == track_id)]
            
            # Detect tracks that do not have 1st fr == 0, they must also be mitotic
            first_row = current_track.sort_values('fr').iloc[0]

            # Mitotic cell appears part way through
            if first_row['fr'] != 1 and first_row['class_id'] == 2:
                #branch_total += 1
                #print('Branch start detected:')
                #print('frame: ' + str(first_row['fr']))
                #print('track: ' + str(first_row['track_id']))
                # Select previous frame
                cframe = tracks.loc[(tracks['fr'] == first_row['fr']-1)]
                
                parent_id=find_parent(first_row, cframe, mass_tolerance)
                if parent_id is not None:
                    daughter_id = first_row['spot_id']
                    # write target id
                    tracks.loc[tracks['spot_id'] == parent_id, 'target_2'] = daughter_id
                
        #%%
        # Create NetworkX graph from the pandas dataframe.
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes (each spot_id is a node)
        for spot in tracks['spot_id']:
            G.add_node(spot)
        
        # Add edges (connect spot_id to target_1 and target_2 if they exist)
        for _, row in tracks.iterrows():
            spot_id = row['spot_id']
            
            for target_col in ['target_1', 'target_2']:
                target = row[target_col]
                if pd.notna(target):  # Only add edge if target is not NaN
                    G.add_edge(spot_id, int(target))
        
        # Find weakly connected nodes to get division code
        family_mapping = {}
        for family_id, component in enumerate(nx.weakly_connected_components(G), start=1):
            for node in component:
                family_mapping[node] = family_id  # Assign the same family_id to all nodes in this component
        tracks['family_id'] = tracks['spot_id'].map(family_mapping)
        
        division_code={}
        # Assign root node a default division code of '0'
        for root in [n for n, d in G.in_degree() if d == 0]:  # Nodes with no parent
            division_code[root] = '0'
        # Traverse the graph to assign division codes
        for parent in nx.topological_sort(G):  # Ensures correct order
            children = list(G.successors(parent))
            if len(children) == 2:  # Branching event detected
                division_code[children[0]] = division_code[parent] + '0'
                division_code[children[1]] = division_code[parent] + '1'
            elif len(children) == 1:  # Single successor, inherit division code
                division_code[children[0]] = division_code[parent]
        tracks['division_code'] = tracks['spot_id'].map(division_code)
        
        # not intepreting as string so trying to force this
        tracks['division_code'] = 'D_' + tracks['division_code']
        # doing this seems to create very strange formatting
        #convert_dict = {'division_code': str}
    
        # appends ids to make branch_id (single cell lifetime)
        tracks['branch_id'] = tracks['family_id'].astype(int).astype(str) + tracks['division_code']

        
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
