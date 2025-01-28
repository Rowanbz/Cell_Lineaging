#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 13:48:12 2024

@author: u2260235
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px
import plotly.io as pio
from scipy.spatial.distance import cdist
pio.renderers.default='browser'

def process_csv(df):
    #df = df.drop([0, 1, 2])
    #df.drop(labels=["LABEL"], axis=1, inplace=True)
    # Reset the index
    df = df.reset_index(drop=True)
    df = df.apply(pd.to_numeric)
    df = df.sort_values(by=['track_id', 'fr'])
    #df = df.sort_values(by=['TRACK_ID', 'FRAME'])
    return df
    

track_df = pd.read_csv("/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/out.csv")
#track_df = pd.read_csv("/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/231229_pos9_48hr_crop1_spots_DATA.csv")
track_df = process_csv(track_df)

#%%
# Choose Track
track_ID=0

s_track_df = track_df.loc[track_df['track_id'] == track_ID]
s_track_df['mass'] = s_track_df['mean'] * s_track_df['area']

# Area vs Frame
plt.plot(s_track_df['fr'], s_track_df['mass'])
plt.xlabel("Frame")
plt.ylabel("Dry mass")

#%%
# 3D plot Plotly
#track_df = px.data.gapminder().query("TRACK_ID==0")


fig = px.line_3d(track_df, x="X", y="Y", z="fr", color="track_id")
fig.show()

#%%
# Randomly select 10% of unique track_ids
sampled_track_ids = np.random.choice(track_df['track_id'].unique(), 
                                     size=int(len(track_df['track_id'].unique()) * 0.1), 
                                     replace=False)

filtered_df = track_df[track_df['track_id'].isin(sampled_track_ids)]

fig = px.line_3d(filtered_df, x="X", y="Y", z="fr", color="track_id")
fig.show()


"""
track_cells_240314.5 - use to get csv
"""