#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:42:15 2025

@author: mlskat
"""

import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt
import pandas as pd
from scipy.special import logit
from scipy.stats import mode
import os


#### 1. Read the data
df = pd.read_csv("/Users/mlskat/Dropbox/QPhase/hmm/240408_240411_WT_150nM_pos33_tracks.csv")

probs =  df[["class_1_prob","class_2_prob","class_3_prob"]]


def sequential_fit_hmm(probs):
   
    probs1 = probs[["class_1_prob"]]
    logit_probs1 = logit(probs1) 
    #### 2. Fit Step 1: Find 'interphase' vs 'mitotic/dead'
    ## 2-1. Logit transform of the probability of class_1 (interphase)

    model1 = hmm.GaussianHMM(
        n_components=2, ## 2-hidden states
        covariance_type="diag", 
        n_iter=1000, ## max iteration
    )
    model1.fit(logit_probs1)
    
    ## 2-2. Reorder the states so that low mean: state 0, high mean: state 1
    # Get the means of the emissions for each state
    means1 = model1.means_.flatten()
    
    # Sort state indices by the mean emissions
    sorted_states = np.argsort(means1)  # Lowest mean will be at index 0
    
    # Reorder the parameters of the model (state 0: lower mean, state 1: higher mean)
    model1.startprob_ = model1.startprob_[sorted_states]
    model1.transmat_ = model1.transmat_[:, sorted_states][sorted_states]
    model1.means_ = model1.means_[sorted_states]
    model1.covars_ = model1.covars_[sorted_states].reshape(model1.n_components, model1.n_features)
    
    ## 2-3 Decode the hidden states (most probable states sequence)
    hidden_states1 = model1.predict(logit_probs1)



    #### 3. Fit Step 2: Focus on finding 'mitotic' vs 'dead'
    ## 3-1. Logit transform of the probabilities of class 2 and class 3 and get the difference
    probs2 = df[["class_2_prob", "class_3_prob"]]
    logit_probs2 = logit(probs2).to_numpy()
    #logit_probs2 = probs2.to_numpy()
    diff_logit_probs2 =logit_probs2[:,0]-logit_probs2[:,1]
    diff_logit_probs2=diff_logit_probs2.reshape(-1, 1) # long matrix with 1 column
    diff_logit_probs2[hidden_states1==1]=np.random.normal(loc=0.0, scale=0.3, size=(np.sum(hidden_states1==1),1)) # set 'interphase' rows to 0

    model2 = hmm.GaussianHMM(
        n_components=3, ## 2-hidden states
        covariance_type="diag", 
        n_iter=1000, ## max iteration
    #random_state=42, ## fixed seed for randamization
    #startprob_prior=np.array([100.0, 1.0, 1.0]) ## State 1 is more likely at the start (I am not sure why this works)
    )
    model2.fit(diff_logit_probs2)


    ## 3-2. Reorder the states so that low mean: state 0, high mean: state 1
    # Get the means of the emissions for each state
    means2 = model2.means_.flatten()

    # Sort state indices by the mean emissions
    sorted_states = np.argsort(means2)  # Lowest mean will be at index 0

    # Reorder the parameters of the model (state 0: lower mean, state 1: higher mean)
    model2.startprob_ = model2.startprob_[sorted_states]
    model2.transmat_ = model2.transmat_[:, sorted_states][sorted_states]
    model2.means_ = model2.means_[sorted_states]
    model2.covars_ = model2.covars_[sorted_states].reshape(model2.n_components, model2.n_features)

    ## 3-3 Decode the hidden states (most probable states sequence)

    hidden_states2 = model2.predict(diff_logit_probs2)
    return hidden_states1, hidden_states2


#### 4. Repeat the sequential fitting until the oscillations stop

def repeat_sequential_fit_hmm(probs):
    hidden_states1_oscillation = probs.shape[0]
    hidden_states2_oscillation = probs.shape[0]
    oscillation_threshold = 200
    while (hidden_states1_oscillation>oscillation_threshold) or     (hidden_states2_oscillation>oscillation_threshold):
        [hidden_states1, hidden_states2] = sequential_fit_hmm(probs)
        hidden_states1_oscillation = np.sum(np.diff(hidden_states1)**2)
        hidden_states2_oscillation = np.sum(np.diff(hidden_states2)**2)
    return hidden_states2

#### repeat for each file
track_dir = '/Users/u2260235/Documents/Y3 Project/cell_mass_250213/1_tracks'
track_dir = '/Users/u2260235/Documents/Y3 Project/cell_mass_250213/1_tracks'

#### 5. Repeat step 4 10 times and take the mode 
n_repeats = 10
# Initialize an empty results matrix
hidden_states2_matrix = np.zeros((np.shape(probs)[0], n_repeats), dtype=int)

for i in range(n_repeats):
    hs2 = repeat_sequential_fit_hmm(probs)
    hidden_states2_matrix[:, i] = hs2
    
# Find the most frequent result per row
hidden_states2 = mode(hidden_states2_matrix, axis=1).mode.flatten()

#### 6. Plot the fitting result
n_points_per_row = 1000
fig, ax = plt.subplots(3, 1, figsize=(15,12))
for i in range(3):
    ax[i].plot(probs["class_1_prob"])
    ax[i].plot(probs["class_2_prob"])
    ax[i].plot(probs["class_3_prob"])
    ax[i].plot(df["fr"]/100)
    ax[i].plot(hidden_states2/2)
    ax[i].set_xlim(n_points_per_row*i, n_points_per_row*(i+1))
    
plt.show()

#print(np.sum(np.diff(hidden_states1)**2))
#print(np.sum(np.diff(hidden_states2)**2))