# =============================================================================
# TASK PARAMETER DEFINITION (should appear on GUI) init trial objects values
# =============================================================================
# IBL rig root folder
IBLRIG_FOLDER = 'C:\\iblrig'
IBLRIG_DATA_FOLDER = None  # If None data folder will be ..\\iblrig_data from IBLRIG_FOLDER
# SOUND, AMBIENT SENSOR, AND VIDEO RECORDINGS
RECORD_SOUND = True
RECORD_AMBIENT_SENSOR_DATA = True
RECORD_VIDEO = True
OPEN_CAMERA_VIEW = True  # if RECORD_VIDEO == True OPEN_CAMERA_VIEW is True
# REWARDS
AUTOMATIC_CALIBRATION = True  # Wether to look for a calibration session and func to define the valve opening time
CALIBRATION_VALUE = 0.067  # calibration value for 3ul of target reward amount (ignored if automatic ON)
REWARD_TYPE = 'Water 10% Sucrose'  # Water, Water 10% Sucrose, Water 15% Sucrose, Water 2% Citric Acid (Guo et al.. PLoS One 2014)
REWARD_AMOUNT = 3.  # (µl) Target resward amount
# TASK
NTRIALS = 2000  # Number of trials for the current session
USE_VISUAL_STIMULUS = True  # Run the visual stim in bonsai
BONSAI_EDITOR = False  # Whether to open the visual stim Bonsai editor or not
# STATE TIMERS
ITI = 1  # Length of gray screen between trials
DELAY_TO_STIM_CENTER = 10  # mean of normal dist with sd of 2
# VISUAL STIM
STIM_POSITIONS = [-35, 35]  # All possible positions for this session (deg)
STIM_FREQ = 0.10  # cycle/visual degree
STIM_ANGLE = 0.  # Vertical orientation of Gabor patch - NOT IN USE
STIM_SIGMA = 7.  # (azimuth_degree²) Size of Gabor patch
# CONTRASTS
CONTRAST_SET = [1.]  # Full contrast set, used if adaptive contrast = False