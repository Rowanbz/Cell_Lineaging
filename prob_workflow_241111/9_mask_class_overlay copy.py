from ij import IJ
from  ij.plugin import Concatenator, HyperStackConverter
import time

original_path = '/Users/u2260235/Documents/Y3 Project/Segmentation/images/240408_240411_WT_150nM_pos33.tiff'
mask_path = '/Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/8_mask_classes_separate/240408_240411_WT_150nM_pos33_mask_classes_separate.tiff'

out_path = '/Users/u2260235/Documents/Y3 Project/Segmentation/class_overlays'

imp1 = IJ.openImage(original_path)
time.sleep(1)
print(type(imp1))
imp1.setDisplayRange(-1, 4)
#imp1.updateAndDraw();
imp1.show()
IJ.run(imp1, "8-bit", "")
imp2 = IJ.run("Bio-Formats Importer", "open=["+ mask_path +"] autoscale color_mode=Composite rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT")
imp2 = IJ.getImage()
IJ.run(imp2, "8-bit", "")

dims = imp2.getDimensions()
nch=dims[2]
print(str(nch)+" channels")

#imp2.setPosition(1,1,1)
imp2.setC(1) # background - change to source image
IJ.run(imp2, "Grays", "")

#imp2.setPosition(2,1,1)
imp2.setC(2) # interphase
IJ.run(imp2, "Yellow", "")
imp2.setDisplayRange(0, 1000)

#imp2.setPosition(3,1,1)
imp2.setC(3) # mitosis
time.sleep(0.1)
IJ.run(imp2, "Magenta", "")
imp2.setDisplayRange(0, 2000)

#imp2.setPosition(4,1,1)
imp2.setC(4) # dead
time.sleep(0.1)
IJ.run(imp2, "Green", "")
imp2.setDisplayRange(0, 2000)



nfr = dims[4]
print(str(nfr)+" frames")
for i in range(nfr):
	imp1.setSlice(i+1)
	imp1.copy()
	imp2.setPosition(1, 1, i+1)
	imp2.paste()

#IJ.run(imp2, "AVI... ", "compression=JPEG frame=25 save=/Users/u2260235/Documents/Y3 Project/Segmentation/class_overlays/240408_240411_WT_150nM_pos2_mask_overlay.avi");
#IJ.run(imp2, "AVI... ", "compression=JPEG frame=25 save="+out_path+"_class_overlay.avi")
#print("Saved")