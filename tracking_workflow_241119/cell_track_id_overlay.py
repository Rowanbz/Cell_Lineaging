from ij import IJ
from  ij.plugin import Concatenator, HyperStackConverter
import time

source_path = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/4_mask_track_id/240408_240411_WT_150nM_pos33.tiff"
mask_path = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/1_source/240408_240411_WT_150nM_pos33.tiff"

imp1 = IJ.openImage(mask_path)
imp2 = IJ.openImage(source_path)

IJ.run(imp1, "glasbey on dark", "")
time.sleep(1)
IJ.run(imp1, "RGB Color", "")
time.sleep(1)
imp1.setDisplayRange(0, 2000)

IJ.run(imp2, "RGB Color", "")

dims = imp1.getDimensions()
nfr = dims[4]

for i in range(nfr):
	imp1.setT(nfr+1)
	IJ.run(imp1, "Select All", "")
	imp1.copy();
	
	imp2.setT(nfr+1)
	IJ.run(imp2, "Select All", "")
	imp1.paste()
	
imp2.show()