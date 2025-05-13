# Cell_Lineaging
To run workflow:
1. Create Conda environment in Anaconda Navigator by importing .yml file
2. Populate Data/1_source with the source images to analyse
3. Open cell_lineage_analysis.py in Python and configure whether to run each function (True or False). Additional parameters can be set such as changing segmentation size or skipping already processed files.
4. Run cell_lineage_analysis.py If having issues with memory, just run a few steps at a time or run again after error with skip_existing=True.