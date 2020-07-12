// input board for ATtiny3216
// for checking I2C interface, use Wire library and assign SCL(15) and SDA(14) pin
#include <Wire.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// potentiometer
const int PA4 = 0;
const int PA5 = 1;
const int PA6 = 2;
const int PA7 = 3;
const int PB5 = 4;
const int PB4 = 5;

// switch
const int PC0 = 10;
const int PC1 = 11;
const int PC2 = 12;
const int PC3 = 13;

// I2C SCL:15, SDA14

int p1 = 0;
int p2 = 0;
int p3 = 0;
int p4 = 0;
int p5 = 0;
int p6 = 0;

int s1 = 1;
int s2 = 1;
int s3 = 1;
int s4 = 1;

int delay_time = 100;

int ch1 = 0;
int ch2 = 0;

#define NOTE_HEIGHT   15
#define NOTE_WIDTH    16
static const unsigned char PROGMEM note_bmp[] =
{ B00000000, B11000000,
  B00000000, B11110000,
  B00000000, B11111100,
  B00000000, B11111111,
  B00000000, B11000011,
  B00000000, B11000001,
  B00000000, B11000010,
  B00000001, B10000100,
  B00000001, B10000000,
  B01111001, B10000000,
  B11111111, B00000000,
  B11111111, B00000000,
  B01111111, B00000000,
  B00111111, B00000000,
  B00001111, B00000000 };


char message[256];
uint8_t count;

void display_note(uint8_t w, uint8_t h) {
  display.drawBitmap(
    w, h,
    note_bmp, NOTE_WIDTH, NOTE_HEIGHT, 1);
}

void setup() {
   pinMode(PA4, INPUT);
   pinMode(PA5, INPUT);
   pinMode(PA6, INPUT);
   pinMode(PA7, INPUT);
   pinMode(PB5, INPUT);
   pinMode(PB4, INPUT);

   pinMode(PC0, INPUT);
   pinMode(PC1, INPUT);
   pinMode(PC2, INPUT);
   pinMode(PC3, INPUT);

   Serial.begin(115200);
   
   Wire.swap(1);
   Wire.begin();
   display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
}


void loop() {
//  DynamicJsonDocument doc(256);
  StaticJsonDocument<256> doc;
  
  p1 = map(analogRead(PA4), 0, 1023, 30, 360); // purple: bpm for blue
  p2 = map(analogRead(PA5), 0, 1023, 2, 24); // white: mosaic rate
  p3 = map(analogRead(PA6), 0, 928, 1, 127); // blue: velocity (this value is a device specific tuning)
  p4 = map(analogRead(PA7), 0, 1023, 1, 108); // green: midi note number of blue
  p5 = map(analogRead(PB5), 0, 1023, 1, 127); // yellow: velocity
  p6 = map(analogRead(PB4), 0, 1023, 1, 108); // red: midi note number of yellow

  s1 = digitalRead(PC1); // red: increment midi channel number of yellow
  s2 = digitalRead(PC0); // yellow: note on-off
  s3 = digitalRead(PC2); // green: increment midi channel number of blue
  s4 = digitalRead(PC3); // blue: note on-off

  if (s1 == 0) {
    ch1 += 1;
    if (ch1 > 15) {
      ch1 = 0;
    }
  }
  if (s3 == 0 ){
    ch2 += 1;
    if (ch2 > 15) {
      ch2 = 0;
    }
  }

  doc["bpm"]=p1; // purple
  doc["mrt"]=p2; // white
  doc["vl2"]=p3; // blue
  doc["nt2"]=p4; // green
  doc["vl1"]=p5; // yellow
  doc["nt1"]=p6; // red
  
  doc["up1"]=s1; // red
  doc["dr1"]=s2; // yellow
  doc["up2"]=s3; // green
  doc["dr2"]=s4; // blue
  doc["ch1"]=ch1; // (yellow)
  doc["ch2"]=ch2; // (blue)

//  serializeJsonPretty(doc, Serial);
  serializeJson(doc, Serial);
  Serial.println();

  // display OLED
  display.clearDisplay();

  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);

  // ch1
  display.print("1 RY ");
  display.printf("%2d", ch1);
  display.setTextSize(1);
  display.print("ch");
  display.setTextSize(2);
  display.print(" ");
  if (s2 == 0 ) {
    display_note(100, 0);
  }
  display.println("");

  //ch2
  display.print("2 GB ");
  display.printf("%2d", ch2);
  display.setTextSize(1);
  display.print("ch");
  display.setTextSize(2);
  display.print(" ");
  if (s4 == 0 ) {
    display_note(100, 16);
  }
  display.println("");

  // bpm
  display.printf("%3d", p1);
  display.setTextSize(1);
  display.print("bpm");

  // mosaic rate (# pixel)
  display.setTextSize(2);
  display.print(" ");
  display.printf("%2d", p2);
  display.setTextSize(1);
  display.print("px");

  display.setTextSize(2);
  display.println("");

  // p3
  display.setTextSize(1);
  display.print("B vol.");
  display.printf("%3d", p3);

  // p4
  display.print(" G # ");
  display.printf("%3d\n", p4);

  // p5
  display.print("Y vol.");
  display.printf("%3d",p5);

  // p6
  display.print(" R # ");
  display.printf("%3d", p6);;
  
  display.display();
 
  delay(delay_time);
}
