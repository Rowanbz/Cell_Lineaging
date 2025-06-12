def detect_branches(track_dir, family_dir, max_search_radius, mass_tolerance, detect_fusion=True):
    import numpy as np
    import pandas as pd
    import networkx as nx
    import os

    def getfilelist(path, filetype):
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith(f".{filetype}")
        ]

    def find_parent(first_row, cframe, mass_tolerance):
        daughter_id = first_row['spot_id']
        daughter_mass = first_row['mass']
        x0 = first_row['X']
        y0 = first_row['Y']
    
        # Frame before daughter appears
        cframe = tracks.loc[tracks['fr'] == first_row['fr'] - 1].copy()
        cframe['distance'] = ((cframe['X'] - x0)**2 + (cframe['Y'] - y0)**2)**0.5
    
        # Candidate parents within range
        parent_candidates = cframe[cframe['distance'] <= max_search_radius]
        parent_candidates = parent_candidates.sort_values('distance')
    
        for _, parent_row in parent_candidates.iterrows():
            parent_mass = parent_row['mass']
            parent_id = parent_row['spot_id']
            class_id = parent_row.get('class_id', None)
    
            #if class_id == 2 or significant_mass_drop(parent_mass, daughter_mass):
            if class_id == 2:
                if mass_check(daughter_mass, parent_mass, mass_tolerance):
                    return parent_id
        return None
    
    def mass_check(daughter_mass, parent_mass, mass_tolerance):
        """
        Ensures that parent mass is roughly double daughter mass, 
        within the allowed mass_tolerance.
        """
        lower_bound = 2 * daughter_mass * (1 - mass_tolerance)
        return parent_mass > lower_bound
    
    def significant_mass_drop(parent_mass, daughter_mass):
        """
        Returns True if parent mass dropped by at least 35%.
        """
        return daughter_mass < 0.65 * parent_mass

    def detect_fusions(tracks, max_search_radius, mass_tolerance):
        """
        Detects fusion events: when a track disappears and a nearby cell's mass increases.
        """
        print("Detecting fusions")
        
        # Get frame range
        all_frames = np.sort(tracks['fr'].unique())
    
        for frame in all_frames[:-1]:
            current_frame = tracks[tracks['fr'] == frame]
            next_frame = tracks[tracks['fr'] == frame + 1]
    
            # Cells that disappear after this frame (no targets)
            for _, row in current_frame.iterrows():
                spot_id = row['spot_id']
                
                if spot_id == 14682:
                    print('Hey!')
                
                if not isinstance(row['targets'], list) or len(row['targets']) == 0:
                    x0, y0, m0 = row['X'], row['Y'], row['mass']
                    
                    # All possible candidates in next frame
                    next_candidates = next_frame.copy()
                    next_candidates['distance'] = np.sqrt((next_candidates['X'] - x0)**2 + (next_candidates['Y'] - y0)**2)
                    
                    # Only those nearby
                    close_candidates = next_candidates[next_candidates['distance'] < max_search_radius]
                    close_candidates = close_candidates.sort_values('distance')
                    if spot_id == 14682:
                        print(close_candidates)
    
                    for _, cand in close_candidates.iterrows():
                        future_spot_id = cand['spot_id']
                        # Previous mass of candidate
                        future_track_id = cand['track_id']
                        past_mass = tracks.loc[(tracks['track_id'] == future_track_id) & (tracks['fr'] == frame), 'mass']
                        if spot_id == 14682:
                            print(f'Past mass: {past_mass}')

                        if not past_mass.empty:
                            past_mass = past_mass.values[0]
                        if spot_id == 14682:
                            print(f'Past mass: {past_mass}')
                            print(f"Present mass: {cand['mass']}")
                            delta_mass = cand['mass'] - past_mass
                            if spot_id == 14682:
                                print(f'Delta mass: {delta_mass}')
                                print(f'M0: {m0}')
    
                            # Check if delta mass ~ disappeared cell's mass
                            if abs(delta_mass - m0) / m0 < mass_tolerance:
                                # Fusion detected
                                future_index = tracks.index[(tracks['spot_id'] == future_spot_id) & (tracks['fr'] == frame + 1)][0]
                                tracks.at[future_index, 'targets'].append(int(spot_id))
                                print(f"Fusion detected! {spot_id} into {future_spot_id} at frame {frame + 1}")
                                break  # Only fuse to one target


    print('Detecting branches')
    os.makedirs(family_dir, exist_ok=True)

    track_files = getfilelist(track_dir, 'csv')
    basenames = [os.path.basename(f).replace("_tracks.csv", "") for f in track_files]
    basenames = ['240408_240411_WT_150nM_pos35']

    for basename in basenames:
        print(f'Processing file: {basename}')
        track_path = os.path.join(track_dir, f"{basename}_tracks.csv")
        save_path = os.path.join(family_dir, f"{basename}_tracks.csv")

        tracks = pd.read_csv(track_path)
        track_ids = np.unique(tracks['track_id'])

        # Initialize columns
        tracks['family_id'] = np.nan
        tracks['division_code'] = np.nan
        tracks['branch_id'] = np.nan
        tracks['targets'] = [[] for _ in range(len(tracks))]

        # Assign target_1 based on next frame
        for track_id in track_ids:
            ctrack = tracks.loc[tracks['track_id'] == track_id]
            tframes = np.unique(ctrack['fr'])

            for i in range(len(tframes) - 1):
                next_frame = tframes[i + 1]
                target_row = ctrack.loc[ctrack['fr'] == next_frame]
                if not target_row.empty:
                    target_id = int(target_row['spot_id'].iloc[0])
                    idx = tracks.index[(tracks['fr'] == tframes[i]) & (tracks['track_id'] == track_id)][0]
                    tracks.at[idx, 'targets'].append(target_id)

        # Detect branches
        for track_id in track_ids:
            current_track = tracks.loc[tracks['track_id'] == track_id]
            if current_track.empty:
                continue

            first_row = current_track.sort_values('fr').iloc[0]

            if first_row['fr'] != 1 and first_row['class_id'] == 2:
                cframe = tracks.loc[tracks['fr'] == first_row['fr'] - 1]
                parent_id = find_parent(first_row, cframe, mass_tolerance)
                if parent_id is not None:
                    daughter_id = first_row['spot_id']
                    parent_index = tracks.index[tracks['spot_id'] == parent_id][0]
                    tracks.at[parent_index, 'targets'].append(int(daughter_id))
                    
        # Detect Fusion
        if detect_fusion:
            detect_fusions(tracks, 100, 0.02)


        # Build graph
        G = nx.DiGraph()
        for spot in tracks['spot_id']:
            G.add_node(spot)

        for _, row in tracks.iterrows():
            spot_id = row['spot_id']
            if isinstance(row['targets'], list):
                for target in row['targets']:
                    G.add_edge(spot_id, int(target))

        # Assign family_id
        family_mapping = {}
        for family_id, component in enumerate(nx.weakly_connected_components(G), start=1):
            for node in component:
                family_mapping[node] = family_id
        tracks['family_id'] = tracks['spot_id'].map(family_mapping)

        # Assign division_code
        division_code = {}
        # Initialize roots
        for root in [n for n, d in G.in_degree() if d == 0]:
            division_code[root] = '0'
        
        # Traverse and assign codes
        for parent in nx.topological_sort(G):
            # If parent doesn't have a code, assign a placeholder
            if parent not in division_code:
                division_code[parent] = 'X'  # or fallback guess
        
            children = list(G.successors(parent))
        
            if len(children) == 1:
                # Continuation
                division_code[children[0]] = division_code[parent]
            if len(children) > 2:
                print('Multipolar division detected!')
            elif len(children) > 1:
                # Division (bipolar, tripolar, etc.)
                for i, child in enumerate(children):
                    division_code[child] = division_code[parent] + str(i)

        tracks['division_code'] = tracks['spot_id'].map(division_code)
        tracks['division_code'] = 'D_' + tracks['division_code']

        tracks['branch_id'] = tracks['family_id'].astype(int).astype(str) + tracks['division_code']

        # Convert targets to underscore-separated string for saving
        tracks['targets'] = tracks['targets'].apply(lambda x: '_'.join(map(str, x)) if isinstance(x, list) else '')

        # Save
        tracks.to_csv(save_path, index=False)
