import sys, traceback
import mido
from mido import Message

import time
import queue
from utility import byte_to_json

from constants import MIDI_SYNTH_PORT_KEY, MIN_MIDI_BPM, JSON_INITIAL_DICT

class Sound:

    def __init__(self):    
        self.midi_synth_port_name = None
        self.midi_synth_outport = None
        self.prev_time = None # time for rchecking MIDI port statust
        self.midi_q = queue.Queue()
        self.quit_midi = False
        self.startTime = None # time for checking MIDI message send interval


    def set_port_name(self, synth_name_key):        
        available_ports = mido.get_output_names()
        print("Available MIDI Ports: %s" % available_ports)
            
        for port in available_ports:
            if (synth_name_key in port):
                self.midi_synth_port_name = port
     

    def open_midi_port(self):
        try:
            self.midi_synth_outport = mido.open_output(self.midi_synth_port_name)
            print("MIDI port opened: %s" % self.midi_synth_port_name)
        except:
            print(traceback.format_exc())
            print("Failed to open MIDI port\n")


    def close_midi_port(self):
        
        try:
            self.midi_synth_outport.close()
            print("MIDI port closed: %s" % self.midi_synth_port_name)
        except:
            print(traceback.format_exc())
            print("Failed to close MIDI port\n")


    def check_midi_port(self, synth_name_key):
        if not self.midi_synth_port_name:
            self.set_port_name(synth_name_key)
        
        now = time.time()
        
        if not self.prev_time:
            # At first time open midi port
            self.open_midi_port()
        else:
            # re-open MIDI output port every 5 seconds
            if now - self.prev_time > 5:
                print("check_midi_port: elapsed 5 seconds")
                if not self.midi_synth_outport.closed():
                    self.close_midi_port()
                    print("check_midi_port: closed MIDI port")
                    # time.sleep(0.05)
                self.open_midi_port()
                print("check_midi_port: open MIDI port")

        self.prev_time = now


    def tum(self, channel=0, note=60, velocity=50):        
        self.check_midi_port(MIDI_SYNTH_PORT_KEY)

        msg = Message('note_on', channel=channel, note=note, velocity=velocity, time=100)
        self.midi_synth_outport.send(msg)
        msg = Message('note_off', channel=channel, note=note, velocity=0)
        self.midi_synth_outport.send(msg)


def send_midi(sound):
#def send_midi():
    # sound = Sound()
    byte_item = None
    prev_json_item = None
    json_item =  JSON_INITIAL_DICT
    
    print("sound.send_midi started\n")
    print("sound.quit_midi:%s" % sound.quit_midi)
    
    sound.check_midi_port(MIDI_SYNTH_PORT_KEY)
    sound.startTime = time.time()
    print("sound.send_midi startTime:%s" % sound.startTime)
    while not sound.quit_midi:
        #print("Sound cheeck sound.quit_midi in loop")
        #print("sound.midi_q.empty(): %s" % sound.midi_q.empty())
        while True:
            try:
                byte_item = sound.midi_q.get(block=True, timeout=1)
            except queue.Empty:
                print(traceback.format_exc())
                print("Sound midi_q.get() timeout. Retrying..")
            except:
                print(traceback.format_exc())
            finally:
                # print("Sound.send_midi emptying byte_item %s: " % byte_item)
                if sound.midi_q.empty():
                    break
            
        # print("Sound.send_midi(): byte_item: %s" % byte_item)
        json_item = byte_to_json(byte_item)
        # print("send_midi(): json_item from byte_item: %s" % json_item)
        if (json_item == None):
            json_item = prev_json_item
            # print("send_midi(): json_item from prev_json_item: %s" % prev_json_item)
            
        # if receiver is working and no object in queue, use previous item
        else:
            prev_json_item = json_item

            
        print("sound.send_midi(): json_item: %s" % json_item)
                              
        bpm = int(json_item['bpm']) #purple
        ratio = 1 / (int(json_item['mrt'])) #white
        vl2 = int(json_item['vl2']) #blue
        nt2 = int(json_item['nt2']) #green
        vl1 = int(json_item['vl1']) #yello
        nt1 = int(json_item['nt1']) #red
        
        up1 = int(json_item['up1']) #red
        dr1 = int(json_item['dr1']) #yellow
        up2 = int(json_item['up2']) #green
        dr2 = int(json_item['dr2']) #blue
        ch1 = int(json_item['ch1']) 
        ch2 = int(json_item['ch2']) 
        
        sound.check_midi_port(MIDI_SYNTH_PORT_KEY)
        
        nowTime = time.time()
        elapsedTime = nowTime - sound.startTime
        
        # print(elapsedTime)

        # wait for each interval 
        if (elapsedTime >= 1/(MIN_MIDI_BPM/60)):
            if (dr1 == 0):  # tum every fps
                sound.tum(channel=ch1, note=nt1, velocity=vl1)
            # sound.startTime = time.time() # reset time

        # wait for each interval 
        if (elapsedTime >= 1/(bpm/60)):
            if (dr2 == 0): # tum every interval of bpm
                sound.tum(channel=ch2, note=nt2, velocity=vl2)

            # time.sleep(1/MIN_FPS) # wait every minimum f
            sound.startTime = time.time() # reset time on hit bpm

        time.sleep(1/(MIN_MIDI_BPM/60)) # wait every minimum bpm interval
        
    sound.close_midi_port()
    print("send_midi stopped\n")
