import os

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
        contact_edge = True
    else:
        contact_edge = False

    return contact_edge


# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(os.sys)
os.sys.setdefaultencoding('utf-8')

############## Select the files ###############

#@ String mask_dir
#@ String output_dir
#@ Integer linking_max_distance

mask_files = [f for f in os.listdir(mask_dir) if f.endswith('.tiff')]


if not os.path.exists(output_dir): # creates output folder
    os.makedirs(output_dir)

for mask_file in mask_files:  # Goes through every file
    print("Processing file: " + str(mask_file))

    ############## Parameters ###############
    w_clip = 150
    h_clip = 150

    mask_path = os.path.join(mask_dir, mask_file)
    imp = IJ.openImage(mask_path)

    out_name = mask_file.replace("_masks.tiff", "_tracks.csv")
    output_path = os.path.join(output_dir, out_name)

    # imp.show()
    [w, h, nch, nsl, nfr] = imp.getDimensions()
    imp = HyperStackConverter.toHyperStack(imp, 1, 1, nch * nsl * nfr, "Grayscale")

    ############ TrackMate #############
    model = Model()
    model.setLogger(Logger.IJ_LOGGER)  # log

    settings = Settings(imp)

    ## Spot detector: Label Image Detector
    settings.detectorFactory = LabelImageDetectorFactory()
    settings.detectorSettings = {
        'TARGET_CHANNEL': 1,
        'SIMPLIFY_CONTOURS': True,
    }

    ## Tracker: LAP Tracker
    settings.trackerFactory = SparseLAPTrackerFactory()
    settings.trackerSettings = settings.trackerFactory.getDefaultSettings()  # almost good enough
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
    trackmate = TrackMate(model, settings)  # initiate the tracking by making an instance

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
    selectionModel = SelectionModel(model)

    # Echo results with the logger we set at start:
    model.getLogger().log(str(model))

    # The feature model, that stores edge and track features.
    fm = model.getFeatureModel()

    ############ Save the results #############

    # Create csv columns
    print("Processing: " + output_path)
    f = open(str(output_path), "w")
    f.write("track_id,spot_id,mask_id,fr,X,Y,edge\n")

    # Iterate over all the tracks that are visible.
    for id in model.getTrackModel().trackIDs(True):

        # Fetch the track feature from the feature model.
        v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
        model.getLogger().log('')
        model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())

        # Get all the spots of the current track.
        track = model.getTrackModel().trackSpots(id)

        overlay = Overlay()

        for spot in track:
            sid = spot.ID()
            # Fetch spot features directly from spot.
            x = spot.getFeature('POSITION_X')
            y = spot.getFeature('POSITION_Y')
            t = spot.getFeature('FRAME')
            q = spot.getFeature('QUALITY')
            snr = spot.getFeature('SNR_CH1')
            median = spot.getFeature('MEDIAN_INTENSITY_CH1')

            model.getLogger().log('\tspot ID = ' + str(sid) + ': x=' + str(x) + ', y=' + str(y) + ', t=' + str(t) + ', q=' + str(q) + ', snr=' + str(snr) + ', median = ' + str(median))

            fr = int(t + 1)
            X = int(x)
            Y = int(y)
            imp.setSlice(fr)
            IJ.doWand(imp, X, Y, 0.0, "8-connected")
            roi = imp.getRoi()

            roi_at_edge = isROIAtEdge(imp, roi)

            f.write("%d,%d,%d,%d,%d,%d,%s\n" % (id, sid, median, fr, X, Y, roi_at_edge))
        print('Saved: ' + output_path)

    f.close()
    imp.close()
