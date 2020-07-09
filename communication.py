import sys, traceback
import serial
from subprocess import getstatusoutput  

import queue

from constants import SERIAL_RATE, GET_USB_PORT_COMMAND

class Communication:
    
    def __init__(self):
        self.serial_q = queue.Queue()
        self.quit_recv = False
        self.ser = None
        
    
    def init_serial(self):
        # scan opening serial port
        print("Communication.init_serial: %s" % GET_USB_PORT_COMMAND)
        status, outputs = getstatusoutput(GET_USB_PORT_COMMAND)

        for output in outputs.split('\n'):
            try: 
                port = output
                self.ser = serial.Serial(port=port, baudrate=SERIAL_RATE)
                if (self.ser == None):
                    print("Serial port cannot be opened\n")
                    exit(1)

                print("Serial is opened over %s in %i bps\n" % (port, SERIAL_RATE))
                # return ser
            except:
                print(traceback.format_exc())
                print("No device found\n")


def recv_serial(com, sound):

    print("receiver started\n")
    while not com.quit_recv:
        
        data =  com.ser.readline()
        
        # this did not work - print from concurrent thread block the process
        # print("serial received(%s)" % data.encode("utf-8")) .. this did not work
        print("communication.recv_serial: %s" % data)
        # sys.stdout.write("\rserial received(%s)\n" % data)
        # sys.stdout.flush()
        sound.midi_q.put_nowait(data)
        com.serial_q.put_nowait(data)

        # print("receiver: sound.midi_q.empty(): %s" % sound.midi_q.empty())
        # time.sleep(0.1)
    com.serial_q.put("pottone.py stopped")
    com.ser.close()
    print("receiver stopped\n")

