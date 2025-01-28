import sys,os

from ij import IJ
from ij import WindowManager

from ij.plugin import FolderOpener
from ij.measure import Measurements
from ij.plugin import HyperStackConverter
from ij.plugin import Concatenator

from ij.gui import Overlay, Roi
from java.awt import Color

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

source_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/1_source"
mask_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/4_mask_track_id"
save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/5_mask_overlay"

source_files=getfilelist(source_dir, 'tiff')
mask_files=getfilelist(mask_dir, 'tiff')
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]
for file_id in range(len(source_files)): # goes through every file
	print("Processing file: " + source_files[file_id])
	imp1 = IJ.openImage(source_files[file_id])
	imp2 = IJ.openImage(mask_files[file_id])
	#imp3 = IJ.Concatenator.run(imp1, imp2)
	ij.plugin.Concatenator()
