#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 10:18:38 2025

@author: u2260235
"""

# models.CellposeModel(gpu=True)

# required python libraries: cellpose, imagej, matplotlib, numpy, pandas, tifffile, wakepy
import os
import scyjava as sj
import imagej
from timeit import default_timer as timer # allows recording of the time taken to run the script
from datetime import timedelta # allows time formatting
from wakepy import keep

# Make sure to go through these and make sure they all create their own folders
### 1. Functions
def cellpose_segmentation(exec_cellpose_segmentation):
    if exec_cellpose_segmentation:
        from Scripts import cellpose_segmentation
        input_dir = os.path.join(data_path, '1_source')
        output_dir = os.path.join(data_path, '2_masks')
        diam1 = 30
        diam2 = 60
        area = 3000
        overlap_threshold = 0.5
        #min_area = 300 # non-default argument
        #area_buffer = 200 # non-default argument
        #skip_existing = True
        cellpose_segmentation.cellpose_segmentation(input_dir, output_dir, diam1, diam2, area, overlap_threshold, save_stacks=True, skip_existing=False)
        
def mask_probs(exec_mask_probs):
    if exec_mask_probs:
        from Scripts import add_probs
        mask_dir = os.path.join(data_path, '2_masks')
        prob_dir = os.path.join(data_path, '3_probs')
        mask_classes_dir = os.path.join(data_path, '5_mask_classes')
        csv_dir = os.path.join(data_path, '6_mask_classes_csv')
        #save_mask_classes = True
        #save_classes_csv = True #non-default
        add_probs.mask_probs(mask_dir, prob_dir, csv_dir, mask_classes_dir, skip_existing=False)
        
def weka_classification(exec_weka_classification):  
    if exec_weka_classification:
        jy_weka_segmentation = os.path.join(scripts_path, 'weka_classification.py')
        input_path = os.path.join(data_path, '1_source')
        output_path = os.path.join(data_path, '3_probs')
        skip_existing = False
        # classifier currently needs this exact name
        model_path = os.path.join(data_path, 'weka_model/classifier.model')
        args = {
            'input_dir': input_path,
            'output_dir': output_path,
            'model_path': model_path,
            'skip_existing': skip_existing
            }
        # read whole script as string and run it
        ij.py.run_script("python", open(jy_weka_segmentation).read(), args)
        
def remove_class(exec_remove_class):
    if exec_remove_class:
        from Scripts import remove_class
        mask_dir = os.path.join(data_path, '2_masks')
        prob_csv_dir = os.path.join(data_path, '6_mask_classes_csv')
        output_dir = os.path.join(data_path, '7_revised_masks')
        class_to_remove = 0
        remove_class.remove_class(mask_dir, prob_csv_dir, output_dir, class_to_remove)

def trackmate_track_cells(exec_trackmate_track_cells):
    # need to add folder 8_tracks creation
    if exec_trackmate_track_cells:
        jy_track_cells = os.path.join(scripts_path, 'trackmate_track_cells.py')
        mask_dir = os.path.join(data_path, '7_revised_masks')
        output_dir = os.path.join(data_path, '8_tracks')
        linking_max_distance = 50
        args = {
            'mask_dir': mask_dir,
            'output_dir': output_dir,
            'linking_max_distance': linking_max_distance
            }
        ij.py.run_script("python", open(jy_track_cells).read(), args)

def cell_mask_continuity(exec_cell_mask_continuity):
    # need to add masks_track_id_label creation
    if exec_cell_mask_continuity:
        from Scripts import label_cell_masks
        mask_dir = os.path.join(data_path, '7_revised_masks')
        track_dir = os.path.join(data_path, '8_tracks')
        output_dir = os.path.join(data_path, 'masks_track_id_label')
        label_cell_masks.cell_mask_label(mask_dir, track_dir, output_dir, 'track_id')
        
def add_probs_to_tracks(exec_add_probs_to_tracks):
    if exec_add_probs_to_tracks:
        from Scripts import tracks_add_probs
        track_dir = os.path.join(data_path, '8_tracks')
        classes_dir = os.path.join(data_path, '6_mask_classes_csv')
        output_dir = os.path.join(data_path, 'tracks_with_probs')
        tracks_add_probs.add_probs_to_tracks(track_dir, classes_dir, output_dir)
        
def add_mass(exec_add_mass):
    if exec_add_mass:
        from Scripts import add_cell_propeties
        source_dir = os.path.join(data_path, '1_source')
        mask_dir = os.path.join(data_path, '7_revised_masks')
        track_dir = os.path.join(data_path, 'tracks_with_probs')
        save_dir = os.path.join(data_path, 'tracks_with_mass')
        skip_existing = False
        add_cell_propeties.add_properties(source_dir, mask_dir, track_dir, save_dir,skip_existing)

def detect_branches(exec_detect_branches):
    if exec_detect_branches:
        from Scripts import detect_branches
        track_dir = os.path.join(data_path, 'tracks_with_mass')
        family_dir = os.path.join(data_path, 'cell_families_csv')
        max_search_radius = 40
        detect_branches.detect_branches(track_dir, family_dir, max_search_radius)
        
def label_by_family_id(exec_label_family_id):
    if exec_label_family_id:
        from Scripts import label_cell_masks
        mask_dir = os.path.join(data_path, '7_revised_masks')
        track_dir = os.path.join(data_path, 'cell_families_csv')
        output_dir = os.path.join(data_path, 'family_id_labelled_cells')
        label_cell_masks.cell_mask_label(mask_dir, track_dir, output_dir, 'family_id')
        
def overlay_id(exec_overlay_id):
    if exec_overlay_id:
        overlay_family_masks = os.path.join(scripts_path, 'overlay_family_masks.py')
        input_dir = os.path.join(data_path, '1_source')
        family_masks_dir = os.path.join(data_path, 'family_id_labelled_cells')
        output_dir = os.path.join(data_path, 'family_overlay')
        args = {
            'source_dir': input_dir,
            'mask_dir': family_masks_dir,
            'save_dir': output_dir
            }
        ij.py.run_script("python", open(overlay_family_masks).read(), args)
        
def plot_2d_lineages(exec_plot_2d_lineages):
    if exec_plot_2d_lineages:
        from Scripts import plot_lineages_2d
        input_dir = os.path.join(data_path, 'cell_families_csv')
        output_dir= os.path.join(figures_path, '2d_lineages')
        plot_lineages_2d.plot_lineages(input_dir, output_dir)
        
def label_by_class_id(exec_label_class_id):
    if exec_label_class_id:
        from Scripts import label_cell_masks
        mask_dir = os.path.join(data_path, '7_revised_masks')
        track_dir = os.path.join(data_path, 'tracks_with_probs')
        output_dir = os.path.join(data_path, '5_mask_classes_adjusted')
        label_cell_masks.cell_mask_label(mask_dir, track_dir, output_dir, 'class_id')
def overlay_class_id(exec_overlay_id):
    if exec_overlay_id:
        overlay_family_masks = os.path.join(scripts_path, 'overlay_family_masks.py')
        input_dir = os.path.join(data_path, '1_source')
        masks_dir = os.path.join(data_path, '5_mask_classes_adjusted')
        output_dir = os.path.join(data_path, 'class_overlay')
        args = {
            'source_dir': input_dir,
            'mask_dir': masks_dir,
            'save_dir': output_dir
            }
        ij.py.run_script("python", open(overlay_family_masks).read(), args)
        
### 2. Configure ImageJ/FIJI
sj.config.add_options('-Xmx6g') # <--- Example: set 6G memory
# paste into command line to check memory: ij.getApp().getInfo(True)


#ij = imagej.init('2.3.0') #Works
#ij = imagej.init('sc.fiji.fiji:2.14.0')  #Doesn't work
ij = imagej.init('/Applications/Fiji.app') # Less reproducible but works where previous doesn't
print(f"ImageJ version: {ij.getVersion()}")

Runtime = sj.jimport('java.lang.Runtime')
print(Runtime.getRuntime().maxMemory() // (2**20), " MB available to Java")

### 1. Create folders
## To run the script, the user has to choose a file location. This file should also be stored there
project_folder = '/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project'
data_path = os.path.join(project_folder, 'Data')
scripts_path = os.path.join(project_folder, 'Scripts')
figures_path = os.path.join(project_folder, 'Figures')

## Inside the /Data/ they need to create a folder "1_source" which contains the source files
## Data/weka_model/classifier.model (a pretrained model) needs to be added
## All scripts need to be placed inside /Scripts/

# List of data folder names:
#directory_names = ['1_source', '2_masks', '3_probs', '4_mask_probs', '5_mask_classes', '6_mask_classes_csv']
# instead make it so each scripts creates its own output folder

###### Once working, put this in the function execute_scripts
### Scripts ###
start = timer() # start timer for time to run all scripts
# A possible cause of slowdown is saving and loading files between each script. However, this helps keep scripts stay modular so is currently still in use.
# It may be sensible to use WakePy so that computer doesn't enter sleept mode (if so then remove its implementation from cellpose_segmentation)


## Actually execute scripts:
with keep.running():  # Keeps code running during sleep mode
    # Segment source images using Cellpose
    cellpose_segmentation(False)
    
    # Classify pixels with pretrained Weka model
    weka_classification(False)
    
    # Save masks labelled with probabilities
    mask_probs(False)
        
    # Remove masks of a specific class based on Weka mean
    remove_class(False)
    
    # Track cells using the masks revised by Weka
    trackmate_track_cells(False)
    
    # Relabel masks for continuity across frames
    cell_mask_continuity(False)
    
    # Concatenates probability and track data
    add_probs_to_tracks(True)
    
    # Exports improved classification masks
    label_by_class_id(True)
    # Overlay on source
    overlay_class_id(True)
    
    # Add the area and intensity (density) from the source images
    add_mass(False)
    
    # Detect cell divisions from mitosis
    detect_branches(False)
    
    # Label by family
    label_by_family_id(False)
    # Overlay family label
    overlay_id(False)
    
    
    # Draw 2D lineages of families
    plot_2d_lineages(False)
    
    # Calculate time it took to process
    end = timer()
    elapsed_time = end - start
    formatted_time = str(timedelta(seconds=elapsed_time))
    print(f'Analysis Finished (time elapsed: {formatted_time})')