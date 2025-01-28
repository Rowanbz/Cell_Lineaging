import os
import csv

from ij import IJ
from ij import WindowManager

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LabelImageDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter

from ij.plugin import FolderOpener
from ij.measure import Measurements
from ij.plugin import HyperStackConverter

from ij.gui import Overlay, Roi
from java.awt import Color

def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

def isROIAtEdge(imp, roi):
    width = imp.getWidth()
    height = imp.getHeight()
    x_roi = roi.getPolygon().xpoints
    y_roi = roi.getPolygon().ypoints

    min_x_roi = min(x_roi)
    max_x_roi = max(x_roi)

    min_y_roi = min(y_roi)
    max_y_roi = max(y_roi)

    if ((min_x_roi <= 0) or (max_x_roi >= width) or (min_y_roi <= 0) or (max_y_roi >= height)):
        contact_edge =True
    else:
        contact_edge =False
    
    return contact_edge
    
def getCellClass(prob_interphase, prob_mitosis, prob_death):
	cell_class = 'interphase'
	if prob_mitosis > prob_interphase:
		cell_class = 'mitotic'
	if prob_death > prob_mitosis and prob_death > prob_interphase:
		cell_class = 'dead'
	return cell_class
	
def getfilelist (path, filetype):
    file_list = [os.path.join(path, f)
    for f in os.listdir(path)
    if f.endswith(str('.'+filetype))]
    return file_list

# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(os.sys)
os.sys.setdefaultencoding('utf-8')

############## Select the files ###############
mask_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/7_revised_masks"
prob_dir = "/Users/u2260235/Documents/Y3 Project/prob_workflow_241111/6_mask_classes_csv"
save_dir = "/Users/u2260235/Documents/Y3 Project/tracking_workflow_241119/3_tracks"

mask_files=getfilelist(mask_dir, 'tiff')
basenames = [
    os.path.basename(file).replace("_masks.tiff", "")
    for file in mask_files
]

for file_id in range(len(basenames)): # goes through every file
	print("Processing file: " + basenames[file_id])

	############## Parameters ###############
	mask_path = mask_dir + '/' + basenames[file_id] + '_masks.tiff'
	save_path = save_dir + '/' + basenames[file_id] + '_tracks.csv'
	
	prob_name = basenames[file_id] + '_mask_classes.csv'
	prob_path = os.path.join(prob_dir, prob_name)
	
	w_clip = 150
	h_clip = 150
	

	imp = IJ.openImage(mask_path) # Load mask
	
	#imp.show()
	[w, h, nch, nsl, nfr]=imp.getDimensions()
	imp= HyperStackConverter.toHyperStack(imp, 1, 1, nch*nsl*nfr, "Grayscale")
	
	# Reads the csv
	probs = []
	with open(prob_path, 'r') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			probs.append(row)  # Each row is appended as a list


	############ TrackMate #############
	model = Model()
	model.setLogger(Logger.IJ_LOGGER) # log
	
	settings = Settings(imp)
	
	## Spot detector: Label Image Detector
	settings.detectorFactory = LabelImageDetectorFactory()
	settings.detectorSettings = {
	    'TARGET_CHANNEL' : 1,
	    'SIMPLIFY_CONTOURS' : True,
	}  
	
	## Tracker: LAP Tracker
	settings.trackerFactory = SparseLAPTrackerFactory()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings() # almost good enough
	settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
	settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
	settings.trackerSettings['LINKING_MAX_DISTANCE'] = 50.0
	settings.trackerSettings['ALLOW_GAP_CLOSING'] = True
	settings.trackerSettings['MAX_FRAME_GAP'] = 5
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 70.0
	
	
	# Add ALL the feature analyzers known to TrackMate. They will 
	# yield numerical features for the results, such as speed, mean intensity etc.
	settings.addAllAnalyzers()
	
	#### Process
	trackmate = TrackMate(model, settings) # intiate the tracking by making an instance
	
	## initial check
	ok = trackmate.checkInput()
	print(ok)
	if not ok:
	    os.sys.exit(str(trackmate.getErrorMessage()))
	
	## actual run
	ok = trackmate.process()
	print(ok)
	if not ok:
	    os.sys.exit(str(trackmate.getErrorMessage()))
	
	#### Display the trackmate results
	# A selection.
	selectionModel = SelectionModel( model )
	
	# Echo results with the logger we set at start:
	model.getLogger().log( str( model ) )
	
	# The feature model, that stores edge and track features.
	fm = model.getFeatureModel()
	
	
	############ Save the results #############
	
	# Create csv columns
	f = open(str(save_path), "w")
	f.write("track_id,spot_id,mask_id,fr,X,Y,edge,p_interphase,p_mitosis,p_death,cell_class\n")
	
	
	# Iterate over all the tracks that are visible.
	for id in model.getTrackModel().trackIDs(True):
	 
	    # Fetch the track feature from the feature model.
	    v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
	    model.getLogger().log('')
	    model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())
	 
	    # Get all the spots of the current track.
	    track = model.getTrackModel().trackSpots(id)
	    
	    #title_clip = "Track_%03d"%(id)
	    #imp_clip = IJ.createImage(title_clip, "32-bit black", w_clip, h_clip, nsl)
	    #imp_clip.show()
	    
	    overlay = Overlay()
	    
	    for spot in track:
	        sid = spot.ID()
	        # Fetch spot features directly from spot.
	        # Note that for spots the feature values are not stored in the FeatureModel
	        # object, but in the Spot object directly. This is an exception; for tracks
	        # and edges, you have to query the feature model.
	        x=spot.getFeature('POSITION_X')
	        y=spot.getFeature('POSITION_Y')
	        t=spot.getFeature('FRAME')
	        q=spot.getFeature('QUALITY')
	        snr=spot.getFeature('SNR_CH1')
	        median=spot.getFeature('MEDIAN_INTENSITY_CH1')
	        model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q) + ', snr='+str(snr) + ', median = ' + str(median))
	        #print(x)
	        
	        fr = int(t+1)
	        X = int(x)
	        Y = int(y)
	        imp.setSlice(fr)
	        IJ.doWand(imp, X, Y, 0.0, "8-connected")
	        #IJ.run(imp, "Fit Spline", "")
	        roi = imp.getRoi()
	        
	        roi_at_edge = isROIAtEdge(imp, roi)
	        
			# Add prob data
            for i in range(1,len(probs)):
                if int(probs[i][0]) == t and int(probs[i][1]) == median:
                    p_interphase = float(probs[i][4])
                    p_mitosis = float(probs[i][5])
                    p_death = float(probs[i][6])  # Select the value in column 6
                    #print('x')

                    cell_class = getCellClass(p_interphase, p_mitosis, p_death)

	        f.write("%d,%d,%d,%d,%d,%d,%s,%0.5f,%0.5f,%0.5f,%s\n"%(id, sid, median, fr, X, Y, roi_at_edge, p_interphase, p_mitosis, p_death, cell_class))

	        #print(id, sid, fr, x, y, area, mean)
        print("Saved: " + save_path)
	
	        
	f.close()
	imp.close()