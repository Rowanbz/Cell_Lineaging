#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 11:04:07 2025

@author: u2260235
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default='browser'

def plot_tracks(tracks):
    fig = px.line_3d(tracks, x='X', y='Y', z='fr', color='family_id', line_group='track_id')

    # annotate points for mitotic state
    m_rows = tracks[tracks['class_id'] == 2]
    d_rows = tracks[tracks['class_id'] == 3]

    # adds dot for mitosis
    for family, group in m_rows.groupby('family_id'):
        fig.add_trace(
            go.Scatter3d(
                x=group['X'],
                y=group['Y'],
                z=group['fr'],
                mode='markers',
                marker=dict(size=3, color='gray', opacity=0.8),
                name=f'M, \n f_id={family}'
            )
        )
    # adds crosses for dead
    for family, group in d_rows.groupby('family_id'):
        fig.add_trace(
            go.Scatter3d(
                x=group['X'],
                y=group['Y'],
                z=group['fr'],
                mode='markers',
                marker=dict(size=2, color='black', symbol='circle', opacity=0.5),
                name=f'D, \n f_id={family}'
            )
        )

    fig.show()

def plot_tracks2(tracks, family_id=None, radius=None):
    if family_id is not None and radius is not None:
        # Get all tracks in the selected family
        selected_tracks = tracks[tracks['family_id'] == family_id]
        
        # Find unique frames where this family appears
        frames = selected_tracks['fr'].unique()

        # Find tracks that come within the radius
        nearby_tracks = set()
        for fr in frames:
            selected_positions = selected_tracks[selected_tracks['fr'] == fr][['X', 'Y']]
            other_tracks = tracks[tracks['fr'] == fr]

            for _, pos in selected_positions.iterrows():
                close_tracks = other_tracks[
                    np.sqrt((other_tracks['X'] - pos['X'])**2 + (other_tracks['Y'] - pos['Y'])**2) <= radius
                ]['family_id'].unique()
                nearby_tracks.update(close_tracks)

        # Filter dataset to include only selected family + nearby families
        filtered_tracks = tracks[tracks['family_id'].isin(nearby_tracks)]
    else:
        filtered_tracks = tracks  # Default: plot all tracks

    # Create 3D line plot
    fig = px.line_3d(filtered_tracks, x='X', y='Y', z='fr', color='family_id', line_group='track_id')

    # Annotate mitotic (class_id == 2) and dead (class_id == 3) states
    m_rows = filtered_tracks[filtered_tracks['class_id'] == 2]
    d_rows = filtered_tracks[filtered_tracks['class_id'] == 3]

    # Add dots for mitosis
    for family, group in m_rows.groupby('family_id'):
        fig.add_trace(
            go.Scatter3d(
                x=group['X'],
                y=group['Y'],
                z=group['fr'],
                mode='markers',
                marker=dict(size=3, color='gray', opacity=0.8),
                name=f'M, \n f_id={family}'
            )
        )

    # Add crosses for dead cells
    for family, group in d_rows.groupby('family_id'):
        fig.add_trace(
            go.Scatter3d(
                x=group['X'],
                y=group['Y'],
                z=group['fr'],
                mode='markers',
                marker=dict(size=2, color='black', symbol='circle', opacity=0.5),
                name=f'D, \n f_id={family}'
            )
        )

    fig.show()
#%%

track_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/6_tracks_revised_2"

basename = '240408_240411_WT_150nM_pos33'

track_path = track_dir + '/' + basename + '_tracks.csv'

tracks = pd.read_csv(track_path)

#plot_tracks(tracks)
plot_tracks2(tracks, 28, 100)


