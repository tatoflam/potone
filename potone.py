import sys, traceback
import serial
from subprocess import getstatusoutput  

import math
import numpy as np
import cv2
import time, datetime
import concurrent.futures
import queue
import json

from constants import KEY_ESC, KEY_SAVE, KEY_RECEIVER_STOP, WINDOW_ORG, WINDOW_DIFF, \
     WINDOW_INVERTDIFF, WINDOW_MOSAIC, WINDOW_MOSAIC_INVERTDIFF, PICTURE_DIR, SERIAL_PORT, \
     SERIAL_STOP, LIST_USB_COMMAND, JSON_INITIAL_DICT, MIDI_SYNTH_PORT_KEY, MIN_FPS
from image import invert_color, mosaic
from sound import Sound, send_midi
from utility import byte_to_json

serial_q = queue.Queue()
quit_recv = False
quit_midi = False
midi_synth_port = None
sound = Sound()

def video_stream():
    item = None
    byte_item = None
    prev_json_item = None
    json_item =  JSON_INITIAL_DICT
    ratio = 0.05
    COLOR = 1
    GRAY = 0
    color = COLOR
    interval = 10
    
    cv2.namedWindow(WINDOW_ORG, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_DIFF, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_INVERTDIFF, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_MOSAIC, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_MOSAIC_INVERTDIFF, cv2.WINDOW_NORMAL)
    
    try:
        global serial_q
        # global midi_q

        sourceVideo = cv2.VideoCapture(0)
        if not sourceVideo.isOpened():
            print("Cannot open camera\n")
            exit(1)
            
        # read the first frame
        hasNext, iFrame = sourceVideo.read()
        # if frame is read correctly ret is True
        if not hasNext:
            print("Can't receive frame (stream end?). Exiting ...\n")
            exit()

        height = iFrame.shape[0]
        width = iFrame.shape[1]
        # got integer result deviding values by "//"
        iFrame = cv2.resize(iFrame, (width//2, height//2))

        # change image upside down and flip it
        iFrame = cv2.flip(iFrame, 0)

        # read background frame
        bFrame = np.zeros_like(iFrame, np.float32)
        
        startTime = time.time()
        
        while True:
            
            # Get message from AVR input board
            while not serial_q.empty():
                byte_item = serial_q.get()
            
            json_item = byte_to_json(byte_item)
            if (json_item == None):
                json_item = prev_json_item
            
            # if receiver is working and no object in queue, use previous item
            else:
                prev_json_item = json_item

            
            print("video_stream(): json_item: %s" % json_item)
                                  
            bpm = int(json_item['bpm']) # purple
            ratio = 1 / (int(json_item['mrt'])) # white
            
            vl2 = int(json_item['vl2']) #blue
            nt2 = int(json_item['nt2']) #green
            vl1 = int(json_item['vl1']) #yellow
            nt1 = int(json_item['nt1']) #red
            
            up1 = int(json_item['up1']) #red
            dr1 = int(json_item['dr1']) #yellow
            up2 = int(json_item['up2']) #green
            dr2 = int(json_item['dr2']) #blue
            ch1 = int(json_item['ch1'])
            ch2 = int(json_item['ch2']) 

            nowTime = time.time()
            elapsedTime = nowTime - startTime
            print(elapsedTime)
            # wait for each interval
            
#            if ((elapsedTime + 1/MIN_FPS) >= 1/(bpm/60)):    
            # convert image to float 
            fFrame = iFrame.astype(np.float32) 

            #diff 
            dFrame = cv2.absdiff(fFrame, bFrame) 

            # convert to gray scale
            gray = cv2.cvtColor(dFrame.astype(np.uint8), cv2.COLOR_RGB2GRAY) 

            # derive outline
            cannyFrame = cv2.Canny(gray, 50, 110) 

            ret, thresh = cv2.threshold(gray, 127, 255, 0) 
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                                     cv2.CHAIN_APPROX_SIMPLE) 

            i = 0 
            sv = 0 
            ix = 0 

            for cnt in contours: 
                area = cv2.contourArea(cnt) 
                if  area > sv: 
                    sv = area 
                    ix = i 
                i = i + 1 

            cx = 0 
            cy = 0 

            if ix > 0 and sv > 10 : 
                M = cv2.moments(contours[ix]) 
                if M['m00'] != 0 : 
                    cx = int(M['m10']/M['m00']) 
                    cy = int(M['m01']/M['m00']) 
                    # print('x:' + str(cx) + ' y:' + str(cy) + ' area:' + str(sv))

            # update background 
            cv2.accumulateWeighted(fFrame, bFrame, 0.025) 

            # invert color
            idFrame = invert_color(dFrame)

            # convert to mosaic
            mFrame = mosaic(iFrame, ratio)
            midFrame = mosaic(idFrame, ratio)

            # display frame
            cv2.imshow(WINDOW_ORG, iFrame) 
            # cv2.imshow(WINDOW_DIFF, dFrame.astype(np.uint8))
            cv2.imshow(WINDOW_DIFF, cannyFrame.astype(np.uint8))
            cv2.imshow(WINDOW_INVERTDIFF, idFrame.astype(np.uint8)) 
            cv2.imshow(WINDOW_MOSAIC, mFrame.astype(np.uint8)) 
            cv2.imshow(WINDOW_MOSAIC_INVERTDIFF, midFrame.astype(np.uint8)) 


            # read next frame
            hasNext, iFrame = sourceVideo.read() 
            iFrame = cv2.resize(iFrame, (width//2, height//2))
            iFrame = cv2.flip(iFrame, 0)


            title = WINDOW_MOSAIC

            k = cv2.waitKey(1)
            if k == KEY_ESC: # wait for ESC key to exit
                break
            
            elif k == ord(KEY_SAVE): # wait for 's' key to save image
                dt_now = datetime.datetime.now().strftime('%Y%m%d%H%M')
                image_path = PICTURE_DIR + title + '_' + dt_now + '.jpg'
                cv2.imwrite(image_path, iFrame)
                print("Saved image at %s" % image_path)
                
            # startTime = time.time() # reset time
            time.sleep(1/MIN_FPS) # wait every minimum fps interval (30fps)

    except:
        print("error")
        print(traceback.format_exc())
    finally:
        # When everything done, release the capture
        sourceVideo.release()
        cv2.destroyAllWindows()


def recv_serial(s):
    global serial_q
    global quit_recv
    global sound

    print("receiver started\n")
    while not quit_recv:
        
        data =  s.readline()
        
        # this did not work - print from concurrent thread block the process
        # print("serial received(%s)" % data.encode("utf-8")) .. this did not work
        print("receiver: serial received: %s" % data)
        # sys.stdout.write("\rserial received(%s)\n" % data)
        # sys.stdout.flush()
        serial_q.put(data)
        sound.midi_q.put(data)
        # time.sleep(0.5)
    serial_q.put("pottone.py stopped")
    print("receiver stopped\n")



def init_serial():

    # scan opening serial port
    status, outputs = getstatusoutput(LIST_USB_COMMAND)

    for output in outputs.split('\n'):
        try: 
            port = output
            s = serial.Serial(port=port, baudrate=SERIAL_PORT)
            print("Serial is opened over %s in %i bps\n" % (port, SERIAL_PORT))
            return s
        except:
            print(traceback.format_exc())
            print("No device found\n")
        

def main():        
    global serial_q
    global quit_recv
    global midi_synth_port
    global sound

    try:
        s = init_serial()
        if (s == None):
            print("Serial port cannot be opened\n")
            exit(1)

        # start serial as a concurrent executor
        quit_recv = False
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        receiver = executor.submit(recv_serial, s)
        
        quit_midi = False
        midi_sender = executor.submit(send_midi)


        # start video stream
        video_stream()

        # this block is for stoping process with terminating receive after video_stream()finished
        while True:
            try:
                key = input()
                time.sleep(1) # wait for checking input
                if(key == KEY_RECEIVER_STOP):
                    print("accepted f command for stopping \n")
                    break
                    
                # if anything from standard input, write back to AVR.
                key += "\n"
                s.write(str.encode(key))
            except:
                print(traceback.format_exc())
                print("\nstop receiver and midi sender thread\n")
                exit(1)
        
    except concurrent.futures.CancelledError:
        print(traceback.format_exc())
        print("executor is cancelled\n")
    except:
        print(traceback.format_exc())
    finally:
        print("main is waiting")
        # do not wait the queue empty as AVR is working asynchronouly
        # serial_q.join()
        
        quit_recv = True
        sound.quit_midi = True
        # wait until executor(receiver) finishes
        while not receiver.done():
            time.sleep(1)
        s.close
        while not midi_sender.done():
            time.sleep(1)

        print("main finished")
        exit(0)

if __name__ == "__main__":
    main()
 
