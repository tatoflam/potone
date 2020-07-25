# coding=UTF-8 
import sys, traceback
import json
from constants import JSON_INITIAL_DICT

seq = 0
count = 0
t4 = 0
t5 = 1
interval = 2000

def byte_to_json(byte_item):
    
    json_item =  JSON_INITIAL_DICT

    # print("video_stream(): byte_item=%s:" % byte_item)
    # b'\x00\n' causes JSONDecodeError 
    if (byte_item != None and b'\x00' not in byte_item):
        try:
            item = byte_item.decode('utf8')
            json_item = json.loads(item)
    
        except json.decoder.JSONDecodeError:
            print("Utility byte_to_json: JSONDecodeError:%s" % byte_item)
            print(traceback.format_exc())
        except EOFError:
            print("Utility byte_to_joson: EOFError:%s" % byte_item)
            print(traceback.format_exc())

    return json_item


def json_to_byte(json_item):
    if (json_item != None):
        try:
            byte_item = json.dumps(json_item).encode('utf8')
        except json.encoder.JSONDecodeError:
            print("Utility json_to_byte: JSONDecodeError:%s" % byte_item)
            print(traceback.format_exc())
        except EOFError:
            print("Utility json_to_byte: EOFError:%s" % byte_item)
            print(traceback.format_exc())

    return byte_item


#def make_mqtt_json(seq, ,count, t1, t2, t3, t4, t5, t6, interval):
def make_mqtt_json(vl1, nt1, vl2, nt2, bpm):
    global seq
    global count
    global t4
    global t5
    
    seq = seq + 1
    count = count + 1
    
    if (t4 == 0 and t5 == 1):
        t4 = 1
        t5 = 0
    else:
        t4 = 0
        t5 = 1
    
    mqtt_dict = {'seq':seq, 'count':count, 't1':vl1, 't2':vl2, 't3':nt1,
                 't4':t4,'t5':t5, 't6':nt2, 'interval':int(60000/bpm)}
    
    # return json object
    return json.dumps(mqtt_dict)
