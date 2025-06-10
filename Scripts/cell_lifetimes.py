#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 23:44:00 2025

@author: u2260235
"""

def calculate_cell_lifetimes(input_dir, output_dir, group_string):
    
    print('Plotting cell lifetimes')
    
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import os
    from scipy.stats import mannwhitneyu
    import statsmodels.stats.multitest as smm

    def compare_mutants_same_concentration(df):
        print('\nStatistical comparisons between NM and C2 at same concentrations:')
        # Extract concentration from condition string
        df['concentration'] = df['Condition'].str.extract(r'_(\d+)').astype(int)
        df['mutant'] = df['Condition'].str.extract(r'^(C2|NM)')
    
        results = []
        concentrations = sorted(df['concentration'].unique())
        
        for conc in concentrations:
            group = df[df['concentration'] == conc]
            group_nm = group[group['mutant'] == 'NM']['frames']
            group_c2 = group[group['mutant'] == 'C2']['frames']
    
            if len(group_nm) >= 2 and len(group_c2) >= 2:  # Require sufficient samples
                stat, p = mannwhitneyu(group_nm, group_c2, alternative='two-sided')
                results.append({'concentration': conc, 'p_value': p, 'n_NM': len(group_nm), 'n_C2': len(group_c2)})
            else:
                results.append({'concentration': conc, 'p_value': np.nan, 'n_NM': len(group_nm), 'n_C2': len(group_c2)})
    
        # Multiple testing correction
        p_values = [r['p_value'] for r in results if not np.isnan(r['p_value'])]
        _, corrected_p, _, _ = smm.multipletests(p_values, method='fdr_bh')
    
        # Insert corrected p-values
        i = 0
        for r in results:
            if not np.isnan(r['p_value']):
                r['p_corrected'] = corrected_p[i]
                i += 1
            else:
                r['p_corrected'] = np.nan
    
        # Print results
        for r in results:
            print(f"Concentration {r['concentration']} | NM: {r['n_NM']}, C2: {r['n_C2']} | p = {r['p_value']:.4f}, corrected p = {r['p_corrected']:.4f}")
    
        return results

    
    def getfilelist(path, filetype):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.' + filetype)]
    
    def plot_df_beeswarm(df, title, group_order):
        import matplotlib.pyplot as plt
        import seaborn as sns
    
        plt.figure(figsize=(7, 5.5))
        sns.set_style("whitegrid")
    
        # Mapping from short codes to full names
        mutant_mapping = {'NM': 'WT', 'C2': 'C2'}
        legend_mapping = {'WT': 'Wild type', 'C2': 'TDP2 mutant'}
        palette = {'Wild type': '#1f77b4', 'TDP2 mutant': '#ff7f0e', 'WT':'#1f77b4', 'C2':'#ff7f0e'}
    
        # Extract info from condition
        df['mutant'] = df['Condition'].str.extract(r'^(NM|C2)')
        df['concentration'] = df['Condition'].str.extract(r'_(\d+)$')[0].astype(int)
        df['group_type'] = df['mutant'].map(mutant_mapping)
    
        # Build a compound label for x-axis
        df['x_label'] = df['group_type'] +'+'+ df['concentration'].astype(str) + 'nM' 
    
        # Generate order preserving `group_order`
        group_order_tuples = [
            (cond.split('_')[0], int(cond.split('_')[1])) for cond in group_order
        ]
        ordered_labels = [
            f"{mutant_mapping[mutant]}+{concentration}nM"
            for mutant, concentration in group_order_tuples
        ]
    
        # Plot
        sns.swarmplot(x='x_label', y='Time (hours)', data=df,
                      alpha=0.7, hue='group_type', palette=palette, dodge=False,
                      order=ordered_labels)
        
        sns.boxplot(x='x_label', y='Time (hours)', data=df,
                    showcaps=False, boxprops={'facecolor': 'None'},
                    showfliers=False, whiskerprops={'linewidth': 0},
                    order=ordered_labels)
    
        #plt.title(title)
        #plt.xticks(rotation=45)
        plt.xlabel("AZD concentration (Nm)")
        plt.legend(title='Cell type', loc='upper right')
        plt.tight_layout()
    
    group_strings = [g.strip() for g in group_string.split(',')]
    print(group_strings)
    os.makedirs(output_dir, exist_ok=True)
    
    branch_files = getfilelist(input_dir, 'csv')
    basenames = [os.path.basename(file).replace("_branches.csv", "") for file in branch_files]
    print(basenames)
    
    df = []

    for file_id, basename in enumerate(basenames):
        # determine the condition based on the group strings
        condition = next((group for group in group_strings if group in basename), None)
        print(condition)
        
        # Only process files that match one of the group strings
        if not condition:
            continue

        print(f'Processing file: {basename}')
        branch_path = os.path.join(input_dir, f'{basename}_branches.csv')
        output_path = os.path.join(output_dir, f'{basename}_lifetimes_hist.png')

        # Load the data
        branches = pd.read_csv(branch_path)
        branches['filename'] = basename
        
        max_end_frame = branches['end_frame'].max()
        branches = branches[
            (branches['start_frame'] != 1) & (branches['end_frame'] != max_end_frame)
        ]
        #branches = branches[(branches['start_class'] == 2) & (branches['end_class'] == 2)]
        
        # only those between divisions
        branches = branches[(branches['divided_start'] == True) & (branches['divided_end'] == True)]
        
        branches = branches[
            branches['edge'] == False
        ]
        branches = branches[branches['frames'] >= 20] # exclude short
        branches['Time (hours)'] = branches['frames']/3
        
        # Assign the identified condition
        branches['Condition'] = condition
        print(f'Condition: {condition}, Rows: {len(branches)} \n')

        # Append to the combined data list for swarm plot
        df.append(branches)
    
    # Combine all data for the swarm plot
    if df:
        # Combine the list of DataFrames into one
        combined_df = pd.concat(df, ignore_index=True)
        combined_df.to_csv('/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Debugging/df.csv', index=False)
        
        # Calculate mean and SD for each group
        for current_condition in combined_df['Condition'].unique():
            condition_df = combined_df[combined_df['Condition'] == current_condition]
            condition_mean = condition_df['frames'].mean()
            condition_sd = condition_df['frames'].std()
            print(f'Condition: {current_condition}, Mean: {condition_mean:.2f}, SD: {condition_sd:.2f}')
        
        # Plot swarm plot
        plot_df_beeswarm(combined_df, title='Swarm Plot of Lifetimes by Condition', group_order=group_strings)
        output_path = os.path.join(output_dir, f'lifetimes_swarm_3.png')
        plt.savefig(output_path)
        plt.close()
    
        # Run statistical comparisons between mutants at same concentration
        compare_mutants_same_concentration(combined_df)
