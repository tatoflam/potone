KEY_ESC = 27    # Esc key
KEY_SAVE = 's'  # Save image key
KEY_RECEIVER_STOP = 'f'
# Stop receiver key
MIN_MIDI_BPM = 360  
MIN_FPS = 20   # minimum interval to process image and sound (30 fps)   

WINDOW_ORG = "Original" 
WINDOW_DIFF = "Diff"
WINDOW_CANNY = "Canny" 
WINDOW_INVERTDIFF = "InvertDifference" 
WINDOW_MOSAIC = "Mosaic"
WINDOW_MOSAIC_DIFF = "MosaicDIff"
WINDOW_MOSAIC_INVERTDIFF = "MosaicInvertDIff"
PICTURE_DIR = "./picture/"
FRAME_HIGHT = 245
MID_PX_MEAN_THREASHOLD = 230

SERIAL_STOP = "stop"
SERIAL_RATE = 115200
GET_USB_PORT_COMMAND="../bin/checkUSB_linux.sh | awk '/D307RG9Y/{print($1)}'"

#JSON_INITIAL_DICT = {'vol':1, 'mrt':1, 'efd':1, 'eft':1, 'sus':1, 'bpm':30,
#                  'img':0, 'pup':0, 'pdn':0, 'drm':0}
JSON_INITIAL_DICT = {'bpm':30, 'mrt':1, 'vl2':1, 'nt2':1, 'vl1':1, 'nt1':1,
                  'up1':0, 'dr1':0, 'up2':0, 'dr2':0, 'ch1':0, 'ch2':0 , 'img':0}

MIDI_SYNTH_PORT_KEY = "FLUID Synth"
MIDI_IMGAE_CHANNEL_LIST = [2, 9, 12, 15]
MIDI_HIGEHST_NOTE_NUM = 108 # under 127
