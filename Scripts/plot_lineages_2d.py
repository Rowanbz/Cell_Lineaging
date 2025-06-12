#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 13:31:52 2025

@author: u2260235
"""

def plot_lineages(input_dir, output_dir):
    import numpy as np
    import pandas as pd
    import os
    import math
    import matplotlib.pyplot as plt
    from collections import defaultdict

    py_col = ('#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
              '#7f7f7f', '#bcbd22', '#17becf')

    def getoffset(full_division_code, x, default_offset):
        division_code = full_division_code[1:]  # remove first char
        dx = default_offset
        for i in range(len(division_code)):
            if division_code[i] == '0':
                x = x - dx
            if division_code[i] == '1':
                x = x + dx
            dx = dx * 0.5
        return x, dx

    def plotcell(division_code, x, ax, default_offset, family_df, col, family_id):
        c_cell = family_df.loc[(family_df['division_code'] == division_code)]
        min_fr = min(c_cell['fr'])
        max_fr = max(c_cell['fr'])

        x_dx = [0, 0]
        if len(division_code) > 1:
            x_dx = getoffset(division_code, 0, offset)
            x = x_dx[0]
            dx = x_dx[1]
            if division_code[-1] == '0':
                ax.plot([x, x + 4 * dx], [min_fr, min_fr], color=col, linewidth=2)
            ax.text(x, min_fr - 0.55, min_fr, horizontalalignment='center')
        else:
            ax.text(x, min_fr - 0.55, family_id, horizontalalignment='center', color='gray')

        # Plot vertical line
        ax.plot([x, x], [min_fr, max_fr + 1], color=col, linewidth=2)

        for _, row in c_cell.iterrows():
            fr = row['fr']
            class_id = row.get('class_id', None)
            if class_id == 2:
                ax.plot(x, fr, 'o', color='grey', alpha=0.5, markersize=3, zorder=5)
            elif class_id == 3:
                ax.plot(x, fr, 'x', color='black', alpha=0.5, markersize=4, zorder=5)

    offset = 1
    print('Plotting 2D Lineages')

    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            print(f'Processing file: {filename}')
            output_filename = os.path.splitext(filename)[0] + "_lineages.png"
            save_path = os.path.join(output_dir, output_filename)
            track_path = os.path.join(input_dir, filename)

            tracks = pd.read_csv(track_path)
            tracks['division_code'] = tracks['division_code'].astype(str).str.replace('D_', '')
            family_ids = np.unique(tracks['family_id'])
            frames = np.unique(tracks['fr'])

            # STEP 1: Build fusion map
            target_map = defaultdict(list)
            for _, row in tracks.iterrows():
                targets = row.get('targets', '')
                if isinstance(targets, str) and targets:
                    for t in targets.split('_'):
                        try:
                            target_map[int(t)].append(int(row['spot_id']))
                        except ValueError:
                            continue
            fusion_targets = {t: s for t, s in target_map.items() if len(s) > 1}

            ncols = min(22, len(family_ids))
            nrows = math.ceil(len(family_ids) / ncols)

            fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 1, nrows * 1))
            axes = np.array(axes).reshape(-1)

            for i, family_id in enumerate(family_ids):
                ax = axes[i]
                family = tracks.loc[(tracks['family_id'] == family_id)]
                cell_ids = np.unique(family['division_code'])
                col = py_col[i % len(py_col)]

                for division_code in cell_ids:
                    plotcell(division_code, 0, ax, offset, family, col, family_id)

                # STEP 2: Draw fusion links in this family
                for target_id, source_ids in fusion_targets.items():
                    if target_id not in family['spot_id'].values:
                        continue
                    target_row = family.loc[family['spot_id'] == target_id].iloc[0]
                    target_code = target_row['division_code']
                    target_fr = target_row['fr']
                    target_x, _ = getoffset(target_code, 0, offset)

                    for source_id in source_ids:
                        if source_id not in family['spot_id'].values:
                            continue
                        source_row = family.loc[family['spot_id'] == source_id].iloc[0]
                        source_code = source_row['division_code']
                        source_fr = source_row['fr']
                        source_x, _ = getoffset(source_code, 0, offset)

                        # Draw dashed line and star
                        ax.plot([source_x, source_x], [source_fr, target_fr],
                                linestyle='--', color='black', linewidth=0.8, alpha=0.6)
                    ax.plot(target_x, target_fr+8, marker='*', color='red', markersize=6, zorder=10)

                # Format subplot
                ax.set_ylim(min(frames), max(frames))
                if i % ncols == 0:
                    ax.set_yticks([min(frames), max(frames)])
                    ax.set_yticks(np.linspace(min(frames), max(frames), 11), minor=True)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                else:
                    for spine in ['top', 'right', 'bottom', 'left']:
                        ax.spines[spine].set_visible(False)
                    ax.set_yticks([])

                ax.set_xticks([])
                ax.invert_yaxis()

            for j in range(len(family_ids), len(axes)):
                axes[j].axis('off')

            plt.tight_layout()
            plt.savefig(save_path)
            plt.show()






