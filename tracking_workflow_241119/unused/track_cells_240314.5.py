import sys,os

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


def find_global_min_and_max(imp):
    sl = imp.getSlice()
    global_max = -1000
    global_min = 1000
    [w, h, nch, nsl, nfr]=imp.getDimensions()
    for i in range(nsl):
        imp.setSlice(i+1)
        stat=imp.getStatistics()
        
        local_max = stat.max
        if local_max > global_max:
            global_max = local_max
        local_min = stat.min
        if local_min < global_min:
            global_min = local_min
    out = {"min":global_min, "max":global_max}
    imp.setSlice(sl)
    return out



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

# We have to do the following to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

############## Parameters ###############
#@ File (label="Select the original input", style="file") original_path
#@ File (label="Select a directory of masks", style="directory") mask_dir
#@ File (label="Select the death probability image", style="file") death_path
#@ File (label="File to save the result", style="save") save_path
#@ File (label="Directory to save the cell clips", style="directory") out_dir

w_clip = 150
h_clip = 150

imp = FolderOpener.open(str(mask_dir), "")
#imp.show()
[w, h, nch, nsl, nfr]=imp.getDimensions()
imp= HyperStackConverter.toHyperStack(imp, 1, 1, nch*nsl*nfr, "Grayscale")

imp_original = IJ.openImage(str(original_path))
#imp_original.show()
stat=find_global_min_and_max(imp_original)
global_min =stat["min"]
global_max =stat["max"]

print(global_min)
print(global_max)

imp_death = IJ.openImage(str(death_path))

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

# skip filter
#filter2 = FeatureFilter('TRACK_DISPLACEMENT', 10, True)
#settings.addTrackFilter(filter2)

#### Process
trackmate = TrackMate(model, settings) # intiate the tracking by making an instance

## initial check
ok = trackmate.checkInput()
print(ok)
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))

## actual run
ok = trackmate.process()
print(ok)
if not ok:
    sys.exit(str(trackmate.getErrorMessage()))

#### Display the trackmate results
# A selection.
selectionModel = SelectionModel( model )

# Read the default display settings.
#ds = DisplaySettingsIO.readUserDefault()

#displayer =  HyperStackDisplayer( model, selectionModel, imp, ds )
#displayer.render()
#displayer.refresh()

# Echo results with the logger we set at start:
model.getLogger().log( str( model ) )

# The feature model, that stores edge and track features.
fm = model.getFeatureModel()


############ Save the results #############

f = open(str(save_path), "w")
f.write("track_id,spot_id,mask_id,fr,X,Y,area,mean,edge,p_death\n")

# Iterate over all the tracks that are visible.
for id in model.getTrackModel().trackIDs(True):
 
    # Fetch the track feature from the feature model.
    v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
    model.getLogger().log('')
    model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())
 
    # Get all the spots of the current track.
    track = model.getTrackModel().trackSpots(id)
    
    title_clip = "Track_%03d"%(id)
    imp_clip = IJ.createImage(title_clip, "32-bit black", w_clip, h_clip, nsl)
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
        smean=spot.getFeature('MEAN_INTENSITY_CH1')
        model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q) + ', snr='+str(snr) + ', mean = ' + str(smean))
        #print(x)
        
        fr = int(t+1)
        X = int(x)
        Y = int(y)
        imp.setSlice(fr)
        IJ.doWand(imp, X, Y, 0.0, "8-connected")
        #IJ.run(imp, "Fit Spline", "")
        roi = imp.getRoi()
        
        roi_at_edge = isROIAtEdge(imp, roi)
        imp_original.setSlice(fr)
        imp_original.setRoi(roi)
        area = IJ.getValue(imp_original, "Area")
        mean = IJ.getValue(imp_original, "Mean")
        
        imp_death.setSlice(fr)
        imp_death.setRoi(roi)
        prob_death = IJ.getValue(imp_death, "Mean")
        
        #print(id, sid, fr, x, y, area, mean)
        f.write("%d,%d,%d,%d,%d,%d,%0.3f,%0.5f,%s,%0.5f\n"%(id, sid, smean+1, fr, X, Y, area, mean, roi_at_edge, prob_death))
        
        x_clip = x - w_clip/2
        y_clip = y - h_clip/2
        roi_clip = Roi(x_clip, y_clip, w_clip, h_clip)
        
        imp_original.setSlice(fr)
        imp_original.setRoi(roi_clip)
        
        imp2 = imp_original.crop()
        imp2.copy()
        imp2.close()
        
        imp_clip.setSlice(fr)
        x_paste = int(max([-x_clip,0]))
        y_paste = int(max([-y_clip,0]))
        imp_clip.paste(x_paste, y_paste)
        
        x_roi = roi.getBounds().x
        y_roi = roi.getBounds().y
        
        roi.setLocation(x_roi-x_clip, y_roi - y_clip)
        roi.setPosition(fr)
        roi.setStrokeColor(Color.cyan)
        overlay.add(roi)
           
    imp_clip.setOverlay(overlay)
    imp_clip.resetRoi()
    #imp_clip.resetDisplayRange()
    imp_clip.setDisplayRange(global_min, global_max)
    IJ.run(imp_clip, "RGB Color", "");
    out_path = os.path.join(str(out_dir), "%s.avi"%(title_clip))
    #IJ.saveAs(imp_clip, "TIFF", str(out_path))
    IJ.run(imp_clip, "AVI... ", "compression=JPEG frame=10 save=%s"%(out_path));
    imp_clip.close() 
        
f.close()
imp_original.close()
imp_death.close()
imp.close()