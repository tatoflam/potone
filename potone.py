import sys, traceback

import time, datetime
import concurrent.futures

from constants import KEY_RECEIVER_STOP

from image import video_stream
from communication import Communication, recv_serial
from sound import Sound, send_midi
from utility import byte_to_json

def main():        
    com = Communication()
    sound = Sound()

    try:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        # start MIDI as a concurrent executor
        sound.quit_midi = False
        midi_sender = executor.submit(send_midi, sound)

        # init serial communication
        # ser = com.init_serial()
        com.init_serial()
        
        # start serial as a concurrent executor
        quit_recv = False
        serial_receiver = executor.submit(recv_serial, com, sound)

        # start video stream
        video_stream(com , sound)

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
                com.ser.write(str.encode(key))
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
        print("main is waiting for stopping threas")
        # do not wait the queue empty as AVR is working asynchronouly
        # serial_q.join()
        
        com.quit_recv = True
        sound.quit_midi = True
        # wait until executor(receiver) finishes
        while not serial_receiver.done():
            time.sleep(1)
        
        while not midi_sender.done():
            time.sleep(1)

        print("main finished")
        exit(0)

if __name__ == "__main__":
    main()
 