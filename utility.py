import json
from constants import JSON_INITIAL_DICT


def byte_to_json(byte_item):
    
    json_item =  JSON_INITIAL_DICT

    # print("video_stream(): byte_item=%s:" % byte_item)
    # b'\x00\n' causes JSONDecodeError 
    if (byte_item != None and byte_item !=  b'\x00\n'):
        try:
            item = byte_item.decode('utf8')
            
            # check stop order from receiver
            # if (item == SERIAL_STOP):
            #    print("video_stream(): got Stop from queue")   

            json_item = json.loads(item)
    
        except json.decoder.JSONDecodeError:
            print("video_stream(): JSONDecodeError:%s" % byte_item)
            print(traceback.format_exc())
        except EOFError:
            print("video_stream(): EOFError:%s" % byte_item)
            print(traceback.format_exc())
        # else:
            # print("video_stream(): item=%s" % item)
        
    return json_item
