from ij import IJ, ImagePlus
from ij.process import ImageProcessor, Blitter
from trainableSegmentation import WekaSegmentation
import os

# File (label="Select the directory with input TIFF files", style="directory") input_dir
# File (label="Select the Weka model", style="file") model_path
# File (label="Directory to save the output", style="directory") out_dir

input_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/1_source"
model_path = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/classifier.model"
out_dir = "//Users/u2260235/Documents/Y3 Project/Segmentation/prob_workflow_241111/3_probs"

input_dir = str(input_dir)
model_path = str(model_path)

# Get list of all TIFF files in the input directory
tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tiff')]
print(tiff_files)

for tiff_file in tiff_files:
    input_path = os.path.join(input_dir, tiff_file)
    
    # Load the input image
    imp_input = IJ.openImage(input_path)
    [w, h, nch, nsl, nfr] = imp_input.getDimensions()
    n = nch * nsl * nfr
    ncl = 4  # Assuming 4 classes, adjust as needed

    title_input = imp_input.getTitle()
    out_name = title_input.replace(".tif", "_prob.tif")
    out_path = os.path.join(out_dir, out_name)

    # Create the output image
    imp_out = IJ.createImage(out_name, "32-bit black", w, h, ncl, 1, n)
    imp_out.show()

    stack_out = imp_out.getStack()

    for i in range(n):
        imp_input.setSlice(i + 1)
        ip = imp_input.getProcessor()
        imp_target = ImagePlus('target', ip)
        wekaSegmentation = WekaSegmentation(False)
        wekaSegmentation.setTrainingImage(imp_target)
        wekaSegmentation.loadClassifier(model_path)
        wekaSegmentation.applyClassifier(True)
        imp_prob = wekaSegmentation.getClassifiedImage()

        stack_prob = imp_prob.getStack()
        for j in range(ncl):
            ip_prob = stack_prob.getProcessor(j + 1)

            index_out = imp_out.getStackIndex(j + 1, 1, i + 1)
            ip_out = stack_out.getProcessor(index_out)

            ip_out.setPixels(ip_prob.getPixels())
            stack_out.setProcessor(ip_out, index_out)

    imp_out.setStack(stack_out)
    imp_out.updateAndDraw()
    imp_out.show()

    # Save the output image
    IJ.saveAs(imp_out, "TIFF", out_path)
    imp_out.close();

    
