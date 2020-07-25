import paho.mqtt.client as mqtt
import ssl
import subprocess
import json

endpoint = "a2toz7cb5zl4er-ats.iot.ap-northeast-1.amazonaws.com" 
port = 8883
topic_to_aws ="fa2020jp/topic0"
topic_from_aws = "fa2020jp/topic0"
rootCA = "/home/pi/awsiot/AmazonRootCA1.pem" # root certificate
cert = "/home/pi/awsiot/a35d03aab7-certificate.pem.crt" # client certificate
key = "/home/pi/awsiot/a35d03aab7-private.pem.key" # client key

seq = 0
count = 0

def on_connect(client, userdata, flags, rc):
    global count
    global seq
    print("Connected")
    if rc==0:
        print("connected OK Returned code=",rc)
        seq = 0
    else:
        print("Bad connection Returned code=",rc)
    # client.subscribe(topic_from_aws)
    
def on_disconnect(client, userdata,rc=0):
    print("mqtt: on_disconnect result code "+str(rc))
    client.loop_stop()
    print("mqtt: on_disconnect client.loop_stop()")
        

def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload)
    

def connect_mqtt():
# if __name__ == '__main__':
    #https://www.eclipse.org/paho/clients/python/docs/#connect-reconnect-disconnect 
    client = mqtt.Client(client_id="rpi")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.tls_set(ca_certs=rootCA, certfile=cert, keyfile=key, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    client.connect(endpoint, port=port, keepalive=60)
    client.loop_start()
    
    print("MQTT client connected and called client.loop_start()")

    return client


def publish(client, json_item):
    global count
    global seq
    count = count + 1
    seq = seq + 1
    
    client.publish(topic_to_aws, json_item)

def disconnect_mqtt(client):
    client.disconnect()
    print("MQTT client disconnected")

