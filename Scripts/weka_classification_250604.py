from ij import IJ, ImagePlus
from ij.process import ImageProcessor, Blitter
from trainableSegmentation import WekaSegmentation
import os
import sys

#@ String input_dir
#@ String output_dir
#@ String model_path
#@ Boolean skip_existing

# create output folder
#os.makedirs(output_dir, exist_ok=True) # only for Python 3+7
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# get list of all TIFF files in the input directory
tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tiff') or f.endswith('.tif')]

for tiff_file in tiff_files:
    input_path = os.path.join(input_dir, tiff_file)
    
    # Create output filename
    out_name = os.path.splitext(tiff_file)[0] + "_prob.tiff"
    output_path = os.path.join(output_dir, out_name)

    # Skip if output already exists and skip_existing is True
    if skip_existing and os.path.exists(output_path):
        print("Skipping " + tiff_file + " (already processed)")
        continue

    # load the input image
    imp_input = IJ.openImage(input_path)
    [w, h, nch, nsl, nfr] = imp_input.getDimensions()
    n = nch * nsl * nfr
    ncl = 4  # number of classes

    title_input = imp_input.getTitle()
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # create output object
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

    # save tiff
    IJ.saveAs(imp_out, "TIFF", output_path)
    imp_out.close()
