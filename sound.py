import mido
from mido import Message
import time

from constants import MIDI_SYNTH_PORT_KEY

midi_synth_port_name = None
midi_synth_outport = None
prev_time = None

def set_port_name(synth_name_key):
    
    global midi_synth_port_name
    
    available_ports = mido.get_output_names()
    print("Available MIDI Ports: %s" % available_ports)
        
    i = 0
    for port in available_ports:
        if (synth_name_key in port):
            midi_synth_port_name = port
 

def check_midi_port(synth_name_key):
    global midi_synth_port_name
    global midi_synth_outport
    global prev_time
    
    if not midi_synth_port_name:
        set_port_name(synth_name_key)
    
    now = time.time()
    
    if not prev_time:
        # At first time open midi port
        midi_synth_outport = mido.open_output(midi_synth_port_name)
    else:
        # re-open MIDI output port every 5 minutes
        if now - prev_time > 5:
            if midi_synth_outport:
                midi_synth_outport.close()
                # time.sleep(0.05)
            midi_synth_outport = mido.open_output(midi_synth_port_name)
    prev_time = now

def tum(note=60, velocity=50):
    check_midi_port(MIDI_SYNTH_PORT_KEY)
    
    msg = Message('note_on', note=note, velocity=velocity, time=960)
    midi_synth_outport.send(msg)
    msg = Message('note_off', note=note, velocity=0)
    midi_synth_outport.send(msg)
    
