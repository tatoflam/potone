# coding=UTF-8 
import sys, traceback

import math
import numpy as np
import cv2
import time, datetime

from constants import KEY_ESC, KEY_SAVE, WINDOW_ORG, WINDOW_DIFF, WINDOW_CANNY, \
     WINDOW_INVERTDIFF, WINDOW_MOSAIC, WINDOW_MOSAIC_DIFF, WINDOW_MOSAIC_INVERTDIFF, \
     PICTURE_DIR, JSON_INITIAL_DICT, MIN_FPS, MIDI_IMGAE_CHANNEL_LIST
from utility import byte_to_json, json_to_byte


def mosaic(frame, ratio=0.05):
    imageSmall = cv2.resize(frame, None, fx=ratio, fy=ratio,
                            interpolation=cv2.INTER_NEAREST)
    frame = cv2.resize(imageSmall, frame.shape[:2][::-1],
                        interpolation=cv2.INTER_NEAREST)
    return frame, imageSmall

def invert_color(frame):
    # invert color
    frame = cv2.bitwise_not(frame.astype(np.uint8))
    return frame


def video_stream(com, sound):
    item = None
    byte_item = None
    prev_json_item = None
    json_item =  JSON_INITIAL_DICT
    ratio = 0.05
    COLOR = 1
    GRAY = 0
    color = COLOR
    interval = 10
    
    np.set_printoptions(threshold=np.inf)
    
    cv2.namedWindow(WINDOW_ORG, cv2.WINDOW_NORMAL) 
    # cv2.namedWindow(WINDOW_DIFF, cv2.WINDOW_NORMAL)
    cv2.namedWindow(WINDOW_CANNY, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_INVERTDIFF, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_MOSAIC, cv2.WINDOW_NORMAL)
    # cv2.namedWindow(WINDOW_MOSAIC_DIFF, cv2.WINDOW_NORMAL) 
    cv2.namedWindow(WINDOW_MOSAIC_INVERTDIFF, cv2.WINDOW_NORMAL)
    
    try:
        # global com
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
            while not com.serial_q.empty():
                byte_item = com.serial_q.get_nowait()
            
            json_item = byte_to_json(byte_item)
            if (json_item == None):
                json_item = prev_json_item
            
            # if receiver is working and no object in queue, use previous item
            else:
                prev_json_item = json_item

            
            print("video_stream(): json_item: %s" % json_item)
                                  
            bpm = int(json_item['bpm']) # purple
            mrt = int(json_item['mrt'])
            
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
            
            # convert image to float 
            fFrame = iFrame.astype(np.float32) 

            #diff 
            dFrame = cv2.absdiff(fFrame, bFrame) 

            # convert to gray scale
            gray = cv2.cvtColor(dFrame.astype(np.uint8), cv2.COLOR_RGB2GRAY) 

            # derieve outline
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
            ratio = 1 / mrt # white
            
            mFrame, mFrameSmall = mosaic(iFrame, ratio)
            mdFrame, mdFrameSmall = mosaic(dFrame,  ratio)
            midFrame, midFrameSmall = mosaic(idFrame, ratio)
            mcannyFrame, mcannyFrameSmall = mosaic(cannyFrame, ratio)

            

            note_rate = 127/midFrameSmall.shape[0]
            # channel_rate = 16/midFrameSmall.shape[1]
            channel_rate = len(MIDI_IMGAE_CHANNEL_LIST)/midFrameSmall.shape[1]
            
            
            print("note_rate: %s" % note_rate)
            print("channel_rate: %s" % channel_rate)

            
            midFrameSmallMean = midFrameSmall[:, :, :].mean(axis=2)
            
            print("----Frame-----")
            # print(midFrameSmall)
            print(midFrameSmallMean)
            
            pixel_list = list(zip(*np.where(midFrameSmallMean < 245)))
            for pixel in pixel_list:
                # print("y: %s" % pixel[0])
                # print("x: %s" % pixel[1])
                # print("y type: %s" % type(pixel[0]))
                
                # assign MIDI note number (upper side is higher number), same behavior withgreen note number
                json_item["nt2"]= int(127 - int(pixel[0]) * note_rate)
                
                # assign MIDI channel, same behavior with green switch
                json_item["ch2"]= MIDI_IMGAE_CHANNEL_LIST[int(int(pixel[1]) * channel_rate)]
                
                # flag to turn on without pushing blue switch
                json_item["img"]= 1
                
                byte_item = json_to_byte(json_item)
                sound.midi_q.put_nowait(byte_item)
                print("image video_sterma(image to sound): %s" % json_item)
                
            # print(type(mcannyFrameSmall))
            print(mcannyFrameSmall.shape)
            # print(mcannyFrameSmall.size)            
            # print(mcannyFrameSmall.dtype)            
            print("----Frame-----")

            # display frame
            cv2.imshow(WINDOW_ORG, iFrame) 
            # cv2.imshow(WINDOW_DIFF, dFrame.astype(np.uint8))
            cv2.imshow(WINDOW_CANNY, cannyFrame.astype(np.uint8))
            cv2.imshow(WINDOW_INVERTDIFF, idFrame.astype(np.uint8)) 
            cv2.imshow(WINDOW_MOSAIC, mFrame.astype(np.uint8))
            # cv2.imshow(WINDOW_MOSAIC_DIFF, mdFrame.astype(np.uint8)) 
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