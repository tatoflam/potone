/*
This is a sample template program for ESP32 connecting to 
AWS IoT over MQTT to make distributed machine device for group 
project of Machine design and mechanial design in   
FabAcademy 2020 (students at Fablab Kamakura and Kannai).

As this code contains certification information, PLEASE 
DO NOT UPLOAD THIS SOURCE CODE to ANY SHARABLE PLACE 
DIRECTLY(including FabAcademy page). If you need to upload
this to sharable place, PLEASE MAKE SURE YOU DELETE
VALUES OF rootCA, certificate and privateKey CHARACTORS. 

For preparation, please find PubSubClient.h in youf local 
library and chhange #define MQTT_MAX_PACKET_SIZE 128 to 512. 

For using this, please update as follows. 
1) Set your ssid and password
2) Configure your topic (or for your use to publish/receive message) 
3) Specify your topic name to subscribe in connectAWSIoT()
4) Write your logic on receiving message in mqttCallback()
5) Write your logic for publishing message in mqttLoop()  // <-optional
*/

#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include <EEPROM.h>

// pin assignment for LED blink
const int S1 = 4;
const int S2 = 16;
const int S3 = 17;

const int DirPin = 25;    // this pin defines direction CW or CCW
const int StepPin = 26;   // pulse this pin to move one step

int motorSpeed = 1000;      // Set step delay for motor in microseconds (smaller is faster)
int currPos = 0; // relative position to start music 
//int initSet = 1050;
int updownMsec = 20;

int maxSteps = 1150;   // maximum steps
int testVar = 0;       // to check if maxsteps is stored

uint8_t EEmaxSteps = 4;
uint8_t EEcurrStep = 8;
uint8_t EEsetInit = 12;

bool noInit = true;
bool debugPrint = true;

// steps per flet
const int f03 = 0;
const int f04 = 156;
const int f05 = 302;
const int f06 = 438;
const int f07 = 563;
const int f09 = 805;
const int f10 = 906;
const int f11 = 1011;

// 1) set your ssid and password ----------
char *ssid = "HM-G24";
char *password = "hommaHome";
// 1) end ---------------------------------
 
// AWS_IOT endpoint setting (fixed)
const char *endpoint = "a2toz7cb5zl4er-ats.iot.ap-northeast-1.amazonaws.com";
const int port = 8883;
//char deviceId[4]; // random device ID in 4 digit hexadecimal (max: ffff) 
byte mac_addr[6];
char deviceId[20];

// 2) configure your topic (or for your use to connect to other people) ----- 
// Topic name needs to be format in "fa2020jp/topic[*]"
// Topic for publishing (if you do not need to publish, you do not need pubTopic. 
char *pubTopic0 = "fa2020jp/topic0";

// Topic for subscribing
char *subTopic0 = "fa2020jp/topic0";

// 2) end -----------------------------------------------------------

const char* rootCA = "-----BEGIN CERTIFICATE-----\n" \
"-----END CERTIFICATE-----\n";
 
const char* certificate = "-----BEGIN CERTIFICATE-----\n" \
"-----END CERTIFICATE-----\n";
 
const char* privateKey = "-----BEGIN RSA PRIVATE KEY-----\n" \
"-----END RSA PRIVATE KEY-----\n";
 
WiFiClientSecure httpsClient;
PubSubClient mqttClient(httpsClient);

int highlow_interval = 20; // duration between ON / OFF for solenoid
 
void setup() {
    Serial.begin(115200);

    pinMode(S1, OUTPUT);
    pinMode(S2, OUTPUT);
    pinMode(S3, OUTPUT);

    EEPROM.begin(32);  // start EEprom
  
    // Make pins as Outputs
    pinMode(StepPin, OUTPUT);
    pinMode(DirPin, OUTPUT);

    // start from RollDown
    digitalWrite(DirPin, LOW);
 
    // Start WiFi connection
    Serial.println("Connecting to ");
    Serial.print(ssid);
    WiFi.begin(ssid, password);

    // wait until WiFi connected
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWifi Connected.");
 
    // Configure certification and MQTT Client
    httpsClient.setCACert(rootCA);
    httpsClient.setCertificate(certificate);
    httpsClient.setPrivateKey(privateKey);
    mqttClient.setServer(endpoint, port);
    mqttClient.setCallback(mqttCallback);

    // EEPROM setting
    initEEPROM();
    
    // Set device Id from Mac Address
    WiFi.macAddress(mac_addr);
    sprintf(deviceId, "%02X:%02X:%02X:%02X:%02X:%02X", mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
    
    connectAWSIoT();

}


void initEEPROM(){
    // get the values from EEprom
    // first the maximum number of steps that can be done
//    EEPROM.get(EEmaxSteps,testVar);
//    if (testVar > 0){
//       maxSteps=testVar;
//    }
    // get the last set position
    EEPROM.get(EEcurrStep,testVar);
    if (testVar > 0){
       currPos=testVar;
    } else {
       currPos=0;
    }
    // move the shutter to start position
    EEPROM.get(EEsetInit,testVar);
    if (testVar == 0){
       currPos=maxSteps;
//       rollDown(400);
//       rollUp(maxSteps);
       noInit = false;
    }
}



void rollDown(int doSteps) {
    digitalWrite(DirPin, LOW);
    delay(8);
    //digitalWrite(DirPin, HIGH);
    for (int i=1; i <= doSteps; i++){
        currPos++;
        if (currPos >= maxSteps){
            currPos=maxSteps;
            break;
        }
        digitalWrite(StepPin, HIGH);
        delayMicroseconds(motorSpeed);
        digitalWrite(StepPin,LOW );
        delayMicroseconds(motorSpeed); 
    }
    if (debugPrint ==true){
       Serial.println("Down to position " + String(currPos));
    }
    stopRoll();
}

void rollUp(int doSteps) {
    digitalWrite(DirPin, HIGH);
    delay(8);
    //digitalWrite(DirPin, LOW);
    for (int i=1; i <= doSteps; i++){
        currPos--; 
        if (currPos < 5){
          currPos=0;
          break;
        }
        digitalWrite(StepPin, HIGH);
        delayMicroseconds(motorSpeed);
        digitalWrite(StepPin,LOW);
        delayMicroseconds(motorSpeed);
        
    }
    if (debugPrint ==true){
       Serial.println("up to position " + String(currPos));
    }
    stopRoll();
}

void stopRoll(){
    // write current position to EEprom
    writeData(EEcurrStep,currPos);
    if (debugPrint ==true){
       Serial.println("Stop");
    }
    digitalWrite(DirPin, HIGH);
      delay(50);
}

void writeData(uint8_t addr, int datInt){
    testVar = 0;
    // to conserve flash memory only write when differs
    EEPROM.get(addr,testVar);
    if (datInt != testVar){
       EEPROM.put(addr,datInt);
       EEPROM.commit();
       if (debugPrint ==true){
          String tcl="0 -> initialise needed 1-> not needed";
          if (addr==4) {
            tcl="maximum Steps";
          } else if (addr==8) {
           
          } tcl="current position"; 
          Serial.print("Updated EEPROM data: " + tcl + " with value: ");
          testVar = 0; 
          // retrieve the data to show the stored value
          EEPROM.get(addr,testVar);
          Serial.println(testVar);
       }   
    }   
}

 
void connectAWSIoT() {
    while (!mqttClient.connected()) {
        
        if (mqttClient.connect(deviceId)) {
            Serial.print("mqtt Connected - deviceId: ");
            Serial.println(deviceId);
            // QoS 0 is sending message only 1 time (the fastest)
            // QoS 1 is returning puback to publisher after send message successfully
            // QoS 2 is sending message only 1 time with validation (the slowest)
            // AWS IoT only allows QoS 0 or 1. 
            int qos = 0;

            // 3) Specify your topic name to subscribe ----------- 
            mqttClient.subscribe(subTopic0, qos);
            // 3) end --------------------------------------------
            Serial.println("Subscribed.");
        } else {
            Serial.print("mqttClient.connect() Failed - deviceId:");
            Serial.println(deviceId);
            Serial.print("Error state=");
            Serial.println(mqttClient.state());
            // Wait every 5 seconds until connect to MQTT broker
            delay(5000);
        }
    }
}

int pushSolenoids(int t1, int t2, int t3){
    int binNumber = t1*4 + t2*2 + t3*1;
    /*  HIGH/LOW map for S1, S2, S3 solenoids
     *  0, 0, 0  = 0
     *  0, 0, 1  = 1
     *  0, 1, 0  = 2
     *  0, 1, 1  = 3
     *  1, 0, 0  = 4
     *  1, 0, 1  = 5
     *  1, 1, 0  = 6
     *  1, 1, 1  = 7
     */
    int overhead = 5; // overhead for pushing solenoid
    switch(binNumber){
        case 0:
            digitalWrite(S1, LOW);
            digitalWrite(S2, LOW);
            digitalWrite(S3, LOW);
            break;
        case 1:
            digitalWrite(S3, HIGH);
            delay(highlow_interval);
            digitalWrite(S3, LOW);
            break;
        case 2:
            digitalWrite(S2, HIGH);
            delay(highlow_interval);
            digitalWrite(S2, LOW);
            break;
        case 3:
            digitalWrite(S2, HIGH);
            digitalWrite(S3, HIGH);
            delay(highlow_interval);
            digitalWrite(S2, LOW);
            digitalWrite(S3, LOW);
            break;
        case 4:
            digitalWrite(S1, HIGH);
            delay(highlow_interval);
            digitalWrite(S1, LOW);
            break;
        case 5:
            digitalWrite(S1, HIGH);
            digitalWrite(S3, HIGH);
            delay(highlow_interval);
            digitalWrite(S1, LOW);
            digitalWrite(S3, LOW);
            break;
        case 6:
            digitalWrite(S1, HIGH);
            digitalWrite(S2, HIGH);
            delay(highlow_interval);
            digitalWrite(S1, LOW);
            digitalWrite(S2, LOW);
            break;
        case 7:
            digitalWrite(S1, HIGH);
            digitalWrite(S2, HIGH);
            digitalWrite(S3, HIGH);
            delay(highlow_interval);
            digitalWrite(S1, LOW);
            digitalWrite(S2, LOW);
            digitalWrite(S3, LOW);
            break;
  }
  overhead = overhead + highlow_interval;
  return overhead;
}


void arpeggio_long(int wait){
    int oh; // overhead
    oh = pushSolenoids(0, 0, 1);
    delay(wait - oh);
    oh = pushSolenoids(1, 0, 0);
    delay(wait/2 - oh);
    oh = pushSolenoids(0, 1, 0);
    delay(wait/2 - oh);
    oh = pushSolenoids(0, 0, 1);
    delay(wait/2 - oh);
    pushSolenoids(1, 0, 0);
    delay(wait/2 - oh);
    oh = pushSolenoids(0, 1, 0);    
//    delay(wait - oh);

}


void arpeggio(int wait){
    int oh; // overhead
    oh = pushSolenoids(1, 0, 0);
    delay(wait*2 - oh);
    oh = pushSolenoids(0, 1, 0);
    delay(wait*2 - oh);
    pushSolenoids(1, 0, 1);
}

void arpeggio_short(int wait){
    int oh; // overhead
    oh = pushSolenoids(1, 0, 1);
    delay(wait - oh);
    oh = pushSolenoids(0, 1, 0);
    delay(wait - oh);
    oh = pushSolenoids(0, 0, 1);
    delay(wait - oh);
    pushSolenoids(1, 1, 0);
//    delay(wait - oh);
//    oh = pushSolenoids(1, 1, 1);
//    delay(wait - oh);
//    oh = pushSolenoids(1, 1, 1);
}


void mqttCallback(char* topic, byte* payload, unsigned int length) {
    DynamicJsonDocument doc(256);
    
    // Write serial monitor
    Serial.print("Received. topic=");
    Serial.println(topic);

    // deserialize
    DeserializationError error = deserializeJson(doc, payload);
    if (error) {
        Serial.print("deserializeJson() failed with code ");
        Serial.println(error.c_str());
        return;
    }
    
    // 4) Write your logic on received message -----------------

    // dump Json in readable format
//    serializeJsonPretty(doc, Serial);
//    Serial.println();
    // parse Json (retrieve int value from for each track)

    int seq = doc["seq"].as<int>();
    int interval = doc["interval"].as<int>();
//    int oh; // overhead for each beat (returned by pushSolenoids())

    int t1 = doc["t1"].as<int>();
    int t2 = doc["t2"].as<int>();
//    int t3 = doc["t3"].as<int>();
//    int t4 = doc["t4"].as<int>();
//    int t5 = doc["t5"].as<int>();
//    int t6 = doc["t6"].as<int>();

    Serial.println("-----t1:" + String(t1) + ", t2:" + String(t2));

    int wait = interval / 4;

//    pushSolenoids(0, 0, 1);

    switch (seq % 16) {
        case 1:
            // start from f03
            arpeggio_long(wait);
            rollDown(50);
            delay(updownMsec);
            rollUp(50);
            break;
        case 2:
 //           delay(wait);
            pushSolenoids(0, 1, 1);
            rollDown(f05-f03); //  to f05
            break;
        case 3:  // f05
            arpeggio_long(wait);
            rollDown(50);
            delay(updownMsec);
            rollUp(50);
            break;
        case 4:
 //           delay(wait);
            pushSolenoids(1, 1, 1);
            rollDown(f07-f05); //  to f07
            break;
        case 5:  // f07
            arpeggio_long(wait);
            rollDown(50);
            delay(updownMsec);
            rollUp(50);
            break;
        case 6:
 //           delay(wait);
            pushSolenoids(1, 1, 1);
            rollUp(f07-f05); //  to f05
            break;
        case 7:
            arpeggio_long(wait);
            rollDown(50);
            delay(updownMsec);
            rollUp(50);
            break;
        case 8:
            pushSolenoids(0, 1, 1);
            rollDown(f07-f05); //  to f07
            break;
            
        case 9:  // f07
            arpeggio_short(wait/2);
            rollUp(f07-f06);
            break;
        case 10: // f06
            arpeggio_short(wait/2);
            rollUp(f06-f05);
            break;
        case 11:  // f05
            arpeggio_short(wait/2);
            rollUp(f05-f04);
            break;
        case 12: // f04
            arpeggio_short(wait/2);
            rollDown(f05-f04);
            break;
        case 13: // f05
            pushSolenoids(1,1,1);
            rollDown(30);
            delay(updownMsec);
            rollUp(30);
            delay(updownMsec);
            rollDown(20);
            delay(updownMsec);
            rollUp(20);
            break;
        case 14: // f04
            arpeggio(wait/2);
            rollUp(f05-f04);       
            break;
        case 15: // f06
            arpeggio_long(wait);
            rollDown(50);
            delay(updownMsec);
            rollUp(50);
            break;

        case 0:  
            arpeggio(wait/2);
            rollUp(f04-f03);
            break;
   }
   
    // 4) end -------------------------------------------------
}

 
void mqttLoop() {
    if (!mqttClient.connected()) {
        connectAWSIoT();
    }
    mqttClient.loop();

      byte var = Serial.read();
      // var - 0x30; // for getting number from ASCII HEX
      // "0" is input, initialize position value in program and EEPROM 
      if  (var - 0x30 == 0) {
//          rollUp(maxSteps);
          currPos=0;
          writeData(EEcurrStep,currPos);
          Serial.print("position initialized to: ");
          Serial.println(currPos);
      }

    // 5) ----- Write your logic for publishing message from here ----- 
    // (If you are not pubishing anything, you can delete following code)

    // Publisher publishes folowing element
    // seq: sequence status (start from 1 when start sound)
    // count: count (start from 1 when start publisher process (on Node-RED in RaspPi)
    // t1: melody1 (in MIDI note name)
    // t2: melody2 (ex. harmony, in MIDI note name)
    // t3: code,  (in MIDI note name)
    // t4: rhythm1 (8 beat, front)       1, 0, 1, 0, 1, 0, 1, 0
    // t5: rhythm2 (8 beat, back)        0, 1, 0, 1, 0, 1, 0, 1
    // t6: rhythm3 (8 beat, variation)   1, 1, 0, 1, 0, 1, 1, 0
    // interval: interval in delay

//    mqttClient.disconnect();
    // 5) end---------------------------------------------------
}
 
 
void loop() {
  mqttLoop();
}
