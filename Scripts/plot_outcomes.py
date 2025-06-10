#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 16:34:40 2025

@author: u2260235
"""

def plot_outcomes(branch_dir, group_string):
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    import os
    
    def getfilelist (path, filetype):
        file_list = [os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(str('.'+filetype))]
        return file_list
    
    def outcome_bars(df):
        df = pd.concat(df, ignore_index=True)

        # Remove unknown outcomes
        df = df[df['outcome'] != 'u']

        # Get unique outcomes and ensure consistent order
        outcome_order = ['normal', 'divided', 'arrested', 'died']  # Example: dead, survived, mitotic
        df['outcome'] = pd.Categorical(df['outcome'], categories=outcome_order, ordered=True)

        # Combine cell_type and condition into one label
        df['label'] = df['cell_type'] + '_' + df['condition'].astype(str)

        # Count outcome frequencies
        outcome_counts = df.groupby(['label', 'outcome']).size().unstack(fill_value=0)

        # Sort logically by cell type and condition
        sort_order = sorted(df['label'].unique(), key=lambda x: (x.split('_')[0], int(x.split('_')[1])))
        outcome_counts = outcome_counts.loc[sort_order]

        # Plot
        ax = outcome_counts.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set2')
        plt.title('Outcome Frequencies by Condition')
        plt.xlabel('Condition')
        plt.ylabel('Number of Cells')
        plt.xticks(rotation=45)
        plt.legend(title='Outcome')
        plt.tight_layout()
        plt.show()
        
        stats_tests(outcome_counts)
        
    def stats_tests(outcome_counts):
        from scipy.stats import fisher_exact, chi2_contingency
        
        if outcome_counts.shape[0] == 2:
            groups = outcome_counts.index.to_list()
            total_counts = outcome_counts.sum(axis=1)
        
            print("\nIndividual outcome statistical tests:")
        
            for outcome in outcome_counts.columns:
                count1 = outcome_counts.loc[groups[0], outcome]
                count2 = outcome_counts.loc[groups[1], outcome]
                absent1 = total_counts[groups[0]] - count1
                absent2 = total_counts[groups[1]] - count2
        
                contingency = [[count1, absent1],
                               [count2, absent2]]
        
                # Choose test depending on counts
                if min(contingency[0] + contingency[1]) < 5:
                    # Small counts - Fisher's exact test
                    oddsratio, p = fisher_exact(contingency)
                    test_name = "Fisher's exact"
                else:
                    # Chi-square test
                    chi2, p, dof, expected = chi2_contingency(contingency)
                    test_name = "Chi-squared"
        
                print(f"Outcome '{outcome}': {test_name} p-value = {p:.4f}")
        else:
            print("\nMore than two groups detected. Individual outcome tests not performed.")


    #%%

    branch_files=getfilelist(branch_dir, 'csv')
    basenames = [
        os.path.basename(file).replace("_outcomes.csv", "")
        for file in branch_files
    ]
    
    # For combined data
    df = []
    print(basenames)
    
    for basename in basenames:
        print(f'Processing file: {basename}')
        branch_path = branch_dir + '/' + basename + '_outcomes.csv'
        
        branches = pd.read_csv(branch_path)
        
        df.append(branches)
        
    outcome_bars(df)

