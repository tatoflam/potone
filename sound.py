import mido
from mido import Message

import time
import queue
from utility import byte_to_json

from constants import MIDI_SYNTH_PORT_KEY, MIN_MIDI_BPM

class Sound():

    midi_synth_port_name = None
    midi_synth_outport = None
    prev_time = None
    midi_q = queue.Queue()
    quit_midi = False
    
    test = 0


    def set_port_name(self, synth_name_key):
        
        available_ports = mido.get_output_names()
        print("Available MIDI Ports: %s" % available_ports)
            
        i = 0
        for port in available_ports:
            if (synth_name_key in port):
                self.midi_synth_port_name = port
     

    def check_midi_port(self, synth_name_key):
        
        if not self.midi_synth_port_name:
            self.set_port_name(synth_name_key)
        
        now = time.time()
        
        if not self.prev_time:
            # At first time open midi port
            self.midi_synth_outport = mido.open_output(self.midi_synth_port_name)
        else:
            # re-open MIDI output port every 5 minutes
            if now - self.prev_time > 5:
                if self.midi_synth_outport:
                    self.midi_synth_outport.close()
                    # time.sleep(0.05)
                self.midi_synth_outport = mido.open_output(midi_synth_port_name)
        self.prev_time = now

    def tum(self, channel=0, note=60, velocity=50):        
        self.check_midi_port(MIDI_SYNTH_PORT_KEY)

        msg = Message('note_on', channel=channel, note=note, velocity=velocity, time=960)
        self.midi_synth_outport.send(msg)
        msg = Message('note_off', channel=channel, note=note, velocity=0)
        self.midi_synth_outport.send(msg)


def send_midi():
    sound = Sound()
    prev_json = None
    
    sound.check_midi_port(MIDI_SYNTH_PORT_KEY)

    print("midi_sender started\n")
    print("quit_midi:%s" % sound.quit_midi)
    
    
    startTime = time.time()
    while not sound.quit_midi:
        while not sound.midi_q.empty():
            byte_item = sound.midi_q.get()
            
        json_item = byte_to_json(byte_item)
        if (json_item == None):
            json_item = prev_json_item
            
        # if receiver is working and no object in queue, use previous item
        else:
            prev_json_item = json_item

            
        print("send_midi(): json_item: %s" % json_item)
                              
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
            
        if (dr1 == 0):  # tum every fps
            sound.tum(channel=ch1, note=nt1, velocity=vl1)
        nowTime = time.time()
        elapsedTime = nowTime - startTime
        
        print(elapsedTime)
        # wait for each interval 
        if (elapsedTime >= 1/(bpm/60)):
            if (dr2 == 0): # tum every interval of bpm
                sound.tum(channel=ch2, note=nt2, velocity=vl2)

            # time.sleep(1/MIN_FPS) # wait every minimum fps interval (30fps)
            startTime = time.time() # reset time
        time.sleep(1/(MIN_MIDI_BPM/60)) # wait every minimum fps interval (30fps)
    

