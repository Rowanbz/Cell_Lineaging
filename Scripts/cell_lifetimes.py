#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 23:44:00 2025

@author: u2260235
"""

def calculate_cell_lifetimes(input_dir, output_dir, group_string):
    import os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy.stats import mannwhitneyu
    import statsmodels.stats.multitest as smm

    def get_matching_files(path, ext='csv'):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.' + ext)]

    def compare_mutants(df):
        print('\nStatistical comparisons between Wild type and TDP2 mutant at same concentrations:')
        df['concentration'] = df['Condition'].str.extract(r'_(\d+)').astype(int)
        df['mutant'] = df['Condition'].str.extract(r'^(NM|C2)')

        results = []
        for conc in sorted(df['concentration'].unique()):
            group = df[df['concentration'] == conc]
            nm = group[group['mutant'] == 'NM']['frames']
            c2 = group[group['mutant'] == 'C2']['frames']
            if len(nm) >= 2 and len(c2) >= 2:
                stat, p = mannwhitneyu(nm, c2, alternative='two-sided')
                results.append({'concentration': conc, 'p': p, 'n_NM': len(nm), 'n_C2': len(c2)})
            else:
                results.append({'concentration': conc, 'p': np.nan, 'n_NM': len(nm), 'n_C2': len(c2)})

        # FDR correction
        valid_p = [r['p'] for r in results if not np.isnan(r['p'])]
        _, corrected_p, _, _ = smm.multipletests(valid_p, method='fdr_bh')

        i = 0
        for r in results:
            if not np.isnan(r['p']):
                r['p_corrected'] = corrected_p[i]
                i += 1
            else:
                r['p_corrected'] = np.nan

        for r in results:
            print(f"Concentration {r['concentration']} | NM: {r['n_NM']}, C2: {r['n_C2']} | p = {r['p']:.4f}, corrected p = {r['p_corrected']:.4f}")

    def plot_violinplot(df, group_order):
        plt.figure(figsize=(6, 5))
        sns.set_style("whitegrid")
    
        # Extract metadata
        df['mutant'] = df['Condition'].str.extract(r'^(NM|C2)')
        df['concentration'] = df['Condition'].str.extract(r'_(\d+)')[0].astype(int)
        df['mutant_full'] = df['mutant'].map({'NM': 'Wild type', 'C2': 'TDP2 mutant'})
        df['x_label'] = df['mutant'] + '_' + df['concentration'].astype(str)
    
        # Generate group order
        group_order_labels = [g.strip() for g in group_order]
    
        # Dynamically build palette for each x_label
        unique_labels = df['x_label'].unique()
        palette = {
            label: '#1f77b4' if 'NM' in label else '#ff7f0e'
            for label in unique_labels
        }
    
        sns.violinplot(
            x='x_label',
            y='Time (hours)',
            data=df,
            scale='width',
            inner='quartile',
            palette=palette,
            order=group_order_labels
        )
    
        plt.xlabel("Condition")
        plt.ylabel("Lifetime (hours)")
        plt.tight_layout()
        plt.legend([], [], frameon=False)  # remove legend


    os.makedirs(output_dir, exist_ok=True)
    #group_string = str(group_string)
    group_strings = [g.strip() for g in group_string.split(',')]

    files = get_matching_files(input_dir, 'csv')

    all_data = []

    for file_path in files:
        basename = os.path.basename(file_path).replace('_branches.csv', '')
        basename_split = basename.split('_')
        #print(basename_split)
        condition=str(basename_split[1]+'_'+basename_split[2])
        #condition=str(basename_split[1])

        print(f'Processing: {basename}')
        branches = pd.read_csv(file_path)

        # Filter criteria
        max_frame = branches['end_frame'].max()
        branches = branches[
            (branches['start_frame'] != 1) &
            (branches['end_frame'] != max_frame) &
            (branches['divided_start']) &
            (branches['divided_end']) &
            (~branches['edge']) &
            (branches['frames'] >= 20)
        ]
        
        branches['Time (hours)'] = branches['frames'] / 3
        branches['Condition'] = condition
        all_data.append(branches)

    if not all_data:
        print("No matching data found.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    for cond in combined_df['Condition'].unique():
        d = combined_df[combined_df['Condition'] == cond]
        print(f"{cond} | Mean: {d['frames'].mean():.2f}, SD: {d['frames'].std():.2f}, N: {len(d)}")

    plot_violinplot(combined_df, group_order=group_strings)

    output_path = os.path.join(output_dir, 'lifetimes_violinplot.png')
    plt.savefig(output_path)
    plt.close()

    compare_mutants(combined_df)

