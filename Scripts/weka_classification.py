from ij import IJ, ImagePlus
from trainableSegmentation import WekaSegmentation
import os
from java.lang import Runtime

#@ String input_dir
#@ String output_dir
#@ String model_path
#@ Boolean skip_existing

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tiff') or f.endswith('.tif')]

#tiff_files = ['240522_C2_25_pos24.tiff']

for tiff_file in tiff_files:
    input_path = os.path.join(input_dir, tiff_file)
    base_name = os.path.splitext(tiff_file)[0]
    file_output_dir = os.path.join(output_dir, base_name)
    output_path = os.path.join(output_dir, base_name)
    
    tiff_path=os.path.join(output_dir, base_name + '_probs.tiff')

    # Skip if output already exists and skip_existing is True
    if skip_existing and (os.path.exists(output_path) or os.path.exists(tiff_path)):
        print("Skipping " + tiff_file + " (already processed)")
        continue
    print("Processing " + tiff_file)
    imp_input = IJ.openImage(input_path)
    dimensions = imp_input.getDimensions()
    width, height, n_channels, n_slices, n_frames = dimensions
    total_slices = n_channels * n_slices * n_frames
    
    print("Configuring Weka")
    # Configure Weka
    weka = WekaSegmentation(False)
    weka.loadClassifier(model_path)

    # Folder to store slices for each file
    if not os.path.exists(file_output_dir):
        os.makedirs(file_output_dir)

    for i in range(total_slices):
        print("  Slice " + str(i+1) + " of " + str(total_slices) +" ("+tiff_file+")")

        # Check if output already exists
        slice_name = base_name + "_prob_slice%04d.tiff" % (i + 1)
        slice_output_path = os.path.join(file_output_dir, slice_name)

        imp_input.setSlice(i + 1)
        ip = imp_input.getProcessor()
        imp_target = ImagePlus("target", ip)

        # Run Weka classifier
        weka.setTrainingImage(imp_target)
        weka.applyClassifier(True)
        imp_prob = weka.getClassifiedImage()

        # Save to file
        IJ.saveAs(imp_prob, "TIFF", slice_output_path)

        # Cleanup
        imp_prob.close()
        imp_target.close()
        imp_prob = None
        imp_target = None
        
    # Clean up memory
    Runtime.getRuntime().gc()

    imp_input.close()
    imp_input = None
