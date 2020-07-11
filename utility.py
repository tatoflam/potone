# coding=UTF-8 
import sys, traceback
import json
from constants import JSON_INITIAL_DICT

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
