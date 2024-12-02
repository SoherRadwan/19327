#include <DHT.h>
#define RLOAD 22.0
#include "MQ135.h"
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
// Declaration for SSD1306 display connected using software SPI (default case):
#define OLED_MOSI   9
#define OLED_CLK   10
#define OLED_DC    11
#define OLED_CS    12
#define OLED_RESET 13
#define buzzer 5
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT,
  OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);
MQ135 gasSensor = MQ135(A0);
int val;
int sensorPin = A0;
int sensorValue = 0;

#define DHToPIN 3 // Digital pin D3 connected to the DHT sensor
#define DHTiPIN 4
#define DHToTYPE DHT11
#define DHTiTYPE DHT11
DHT dhto(DHToPIN, DHToTYPE);
DHT dhti(DHTiPIN, DHTiTYPE);
void setup() {

Serial.begin(9600);
 pinMode(sensorPin, INPUT);
 pinMode(buzzer, OUTPUT);

dhto.begin();
dhti.begin();
}
void loop() {

float ho = dhto.readHumidity();

float to = dhto.readTemperature();

//if (isnan(ho) || isnan(to)) {}

Serial.print("Humidity out: ");

Serial.print(ho);

Serial.print(" %\t");

Serial.print("Temperature out: ");

Serial.print(to);

Serial.println(" *C");
float hi = dhti.readHumidity();

float ti = dhti.readTemperature();

//if (isnan(ho) || isnan(to)) {}

Serial.print("Humidity IN: ");

Serial.print(hi);

Serial.print(" %\t");

Serial.print("Temperature IN: ");

Serial.print(ti);

Serial.println(" *C");
float ppm = gasSensor.getPPM();
Serial.print ("CO2: ");
Serial.print (ppm);
Serial.println ("  ppm");

 float threshold = 60*ho/100.0;
 //Serial.println (threshold);
if (hi>threshold && ti > 25){
Serial.println ("alarm");
  digitalWrite(buzzer , HIGH);
  delay (300);
  digitalWrite(buzzer , LOW);
}

delay(1000);

}
