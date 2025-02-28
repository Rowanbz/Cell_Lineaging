#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:58:28 2025

@author: u2260235
"""

import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt

# Simulated data example: Observations generated from two overlapping distributions
# Let's assume 200 samples: 100 around 0 (state 0) and 100 around 1 (state 1)
np.random.seed(42)
state_0 = np.random.normal(loc=0.0, scale=0.4, size=100)  # State 0 distribution
state_1 = np.random.normal(loc=1.0, scale=0.4, size=20)  # State 1 distribution
observations = np.concatenate([state_0, state_1])

# Reshape observations for HMM (needs 2D array: n_samples x n_features)
observations = observations.reshape(-1, 1)

# Initialize and configure HMM with 2 hidden states (Gaussian emissions)
model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=100, random_state=42, verbose=True, tol=1e-12)

# Fit the model to the observations
model.fit(observations)

# Decode the hidden states (most probable states sequence)
hidden_states = model.predict(observations)

# Print the transition matrix and emission means (state parameters)
print("Transition Matrix:")
print(model.transmat_)

print("\nState Means:")
print(model.means_)

print("\nState Covariances:")
print(model.covars_)

# Output hidden states
print("\nInferred Hidden States:")
print(hidden_states)

plt.hist(observations, bins=30, alpha=0.7, color="blue", label='observations')
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.title("Histogram of Observations")
plt.legend()
plt.show()