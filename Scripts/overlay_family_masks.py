from ij.plugin import Concatenator, HyperStackConverter
from ij import WindowManager, IJ
import os

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

#source_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/1_source"
#mask_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/7_mask_family_id"
#save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/8_family_overlay"

# input_dir, output_dir and model_path should all be passed by ij.py.run_script
#@ String source_dir
#@ String mask_dir
#@ String save_dir

print('Overlaying masks (Fiji)')

source_files=getfilelist(source_dir, 'tiff')
basenames = [
    os.path.basename(file).replace(".tiff", "")
    for file in source_files
]
#basenames = ['240408_240411_WT_150nM_pos34']

for i, basename in enumerate(basenames): # goes through every file
    source_path = source_dir + '/' + basename + '.tiff'
    mask_path = mask_dir + '/' + basename + '_masks.tiff'
    save_path = save_dir + '/' + basename + '.avi'
    print('Overlaying with file' + str(i) +'/' + str(len(basenames)))
    	
    imp1 = IJ.openImage(source_path)
    dims = imp1.getDimensions()
    n = imp1.getNSlices()
    imp2 = IJ.openImage(mask_path)
    IJ.run(imp2, "32-bit", "")
    ip2 = imp2.getProcessor()
    ip2 = ip2.convertToFloatProcessor()
    imp2.setProcessor(ip2)
    print('Concatenating source and masks')
    imp3 = Concatenator.run(imp1, imp2)
    HyperStackConverter.toStack(imp3)
    	
    #imp3.show()
    print(dims)
    print(n)
    imp3=HyperStackConverter.toHyperStack(imp3, 2, 1, n, "xytcz", "Composite")
        	
    print('Applying LUTs')
    imp3.setC(1)
    IJ.run(imp3, "Grays", "")
    imp3.setC(2)
    IJ.run(imp3, "glasbey on dark reduced brightness", "")
    #imp3.setDisplayRange(0, 255)  # or whatever min/max values are appropriate
    #IJ.run("Brightness/Contrast...")
    IJ.resetMinAndMax(imp3)
    #imp3.show()
    # flipping channels after showing makes resetminmax apply properly:
    imp3.setC(1)
    #IJ.run(imp3, "AVI... ", "compression=JPEG frame=25 save="+save_path)
    #IJ.run(imp3, "RGB Color", "")
    print('Saving overlayed movie')
    IJ.saveAs(imp3, "Tiff", save_path)
    IJ.run("Close All")
    print('Saved '+ save_path)
    
'''
from ij.plugin import Concatenator, HyperStackConverter
from ij import WindowManager, IJ
import os

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

source_dir = "/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Data/1_source"
mask_dir = "/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Data/family_id_labelled_cells"
save_dir = "/Users/u2260235/Library/CloudStorage/OneDrive-UniversityofWarwick/Y3_Project/Data/family_overlay"

source_files=getfilelist(source_dir, 'tiff')
basenames = [
    os.path.basename(file).replace(".tiff", "")
    for file in source_files
]
#basenames = ['240408_240411_WT_150nM_pos34']

for file_id in range(len(basenames)): # goes through every file
	source_path = source_dir + '/' + basenames[file_id] + '.tiff'
	mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
	save_path = save_dir + '/' + basenames[file_id] + '.avi'
	print(save_path)
	
	imp1 = IJ.openImage(source_path)
	dims = imp1.getDimensions()
	n = imp1.getNSlices()
	imp2 = IJ.openImage(mask_path)
	IJ.run(imp2, "32-bit", "")
	ip2 = imp2.getProcessor()
	ip2 = ip2.convertToFloatProcessor()
	imp2.setProcessor(ip2)
	#imp3 = Concatenator().concatenate(imp1, imp2, True)
	imp3 = Concatenator.run(imp1, imp2)
	HyperStackConverter.toStack(imp3)
	
	imp3.show()
	print(dims)
	print(n)
	imp3=HyperStackConverter.toHyperStack(imp3, 2, 1, n, "xytcz", "Composite")
	
	imp3.setC(1)
	IJ.run(imp3, "Grays", "")
	imp3.setC(2)
	IJ.run(imp3, "glasbey on dark reduced brightness", "")
	IJ.run("Brightness/Contrast...")
	IJ.resetMinAndMax(imp3)
	imp3.show()
	# flipping channels after showing makes resetminmax apply properly:
	imp3.setC(1)
	imp3.setC(2)
	#IJ.run(imp3, "AVI... ", "compression=JPEG frame=25 save="+save_path)
	#IJ.run(imp3, "RGB Color", "")
	IJ.saveAs(imp3, "Tiff", save_path)
	IJ.run("Close All")
'''