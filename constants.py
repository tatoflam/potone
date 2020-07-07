KEY_ESC = 27    # Esc key
KEY_SAVE = 's'  # Save image key
KEY_RECEIVER_STOP = 'f'
# Stop receiver key
INTERVAL= 33     # インターバル 

WINDOW_ORG = "Original" 
WINDOW_DIFF = "Difference" 
WINDOW_INVERTDIFF = "InvertDifference" 
WINDOW_MOSAIC = "Mosaic"
WINDOW_MOSAIC_INVERTDIFF = "MosaicInvertDIff"
PICTURE_DIR = "./picture/"

SERIAL_STOP = "stop"
SERIAL_PORT = 115200
LIST_USB_COMMAND="ls -1 /dev/ttyUSB*"

#JSON_INITIAL_DICT = {'vol':1, 'mrt':1, 'efd':1, 'eft':1, 'sus':1, 'bpm':30,
#                  'img':0, 'pup':0, 'pdn':0, 'drm':0}
JSON_INITIAL_DICT = {'bpm':30, 'mrt':1, 'vl2':1, 'nt2':1, 'vl1':1, 'nt1':1,
                  'up1':0, 'dr1':0, 'up2':0, 'dr2':0, 'ch1':0, 'ch2':0}


MIDI_SYNTH_PORT_KEY = "FLUID Synth"
