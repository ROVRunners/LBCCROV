
#include <SPI.h>        
#include <Ethernet.h>
#include <EthernetUdp.h>
#include <Servo.h>
#include <TM1637.h>
#include <Wire.h>
#define serverPort 4080

//setting up ethernet
#define SD_SS 4//sets up ethernet communication ports, don't need to change this part
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };//connection for ethernet
IPAddress localIp(192, 168, 1, 251);    // local ip address
IPAddress destIp(192, 168, 1, 15);      // destination ip address
IPAddress ip(192, 168, 1, 15);
IPAddress remIp(92, 168, 1, 176);
unsigned int localPort = 5678;      // local port to listen on
unsigned int port = 5678;               // destination port
EthernetUDP Udp;//initializes objects

//OneWire oneWire(temp_pin); 
//DallasTemperature sensors(&oneWire);

Servo thrusterA;
Servo thrusterB;
Servo thrusterC;
Servo thrusterD;
Servo thrusterE;
Servo thrusterF;

const int halt = 1500, arraylength = 7, middle = 127, ScaleFactor=2.34375 ; 
int stick_value, go, reverse, up_down;

int a, b, c, d, e, f;// value from the analog sticks from the controller

int i, j;
byte movement, lasers, tilt, sense; // Determines what direction the ROV needs to go.
float thruster_adjust, temp, pH_value, initial_depth, depth; // Changes the % of full thrust the motors use.
byte packetBuffer[arraylength], message[arraylength]; // Array that is recieved and output message.


void setup(){
  Serial.begin(9600);//allows serial moniter

  //ethernet setup
  pinMode(SD_SS, OUTPUT);//sets up ethernet
  digitalWrite(SD_SS, HIGH);
  Ethernet.begin(mac,localIp);
  Ethernet.begin(mac,ip);
  Udp.begin(port);
  Udp.begin(localPort);

  thrusterA.attach(3);//sets up thruster pins and halts them
  thrusterB.attach(5);
  thrusterC.attach(6);
  thrusterD.attach(9); 
  thrusterE.attach(7);//up/down
  thrusterF.attach(8);//up/down
  thrusterA.writeMicroseconds(halt);
  thrusterB.writeMicroseconds(halt);  
  thrusterC.writeMicroseconds(halt);  
  thrusterD.writeMicroseconds(halt);  
  thrusterE.writeMicroseconds(halt);
  thrusterF.writeMicroseconds(halt);
}

void loop() 
{ 
  recieve();        //recieves the array and puts it inside 
  //print_recieved();
  thrusters_go();   //Sends out the pulse to the ESC's
  //print_values(); //prints out  
  delay(50);
}
void recieve(){//recieves data from ethernet and puts it in packetBuffer array
  int packetSize = Udp.parsePacket();
  IPAddress remote = Udp.remoteIP();
  Udp.read(packetBuffer,arraylength);

  int LX, LY, RX, RY, count, L1R1, countbut;
  LX = packetBuffer[0];
  LY = packetBuffer[1];
  RX = packetBuffer[2];
  RY = packetBuffer[3];
  count = packetBuffer[4];
  L1R1 = packetBuffer[5];
  countbut = packetBuffer[6];

  a = (Remap(LY,-1)+Remap(LX,-1)+Remap(RX,-1))/count + halt;//Thruster A  This set of functions remaps the controller range to the expected values for the ESC's
  b = (Remap(LY,1)+Remap(LX,-1)+Remap(RX,-1))/count + halt;//Thruster B   It also is then able to flip the range depending on the orientation of the thrusters
  c = (Remap(LY,-1)+Remap(LX,1)+Remap(RX,-1))/count + halt;//Thruster C
  d = (Remap(LY,-1)+Remap(LX,-1)+Remap(RX,-1))/count + halt;//Thruster D
  e = (Remap(RY,1)+Remap(L1R1,1))/countbut + halt; //Z-axis Thrust
  f = (Remap(RY,1)+Remap(L1R1,-1))/countbut + halt; 
}

void thrusters_go(){ // A function to convert the integer values into the corresponding PWM Signal for the speed controllers 
  thrusterA.writeMicroseconds(a);
  thrusterB.writeMicroseconds(b);  
  thrusterC.writeMicroseconds(c);  
  thrusterD.writeMicroseconds(d);
  thrusterE.writeMicroseconds(e);
  thrusterF.writeMicroseconds(f);
}

void print_recieved(){
  Serial.println();
  for(i = 0; i < arraylength; i++){
    Serial.print(packetBuffer[i]);
    Serial.print(" ");
  }
}

void print_values(){
  Serial.print(a);
  Serial.print(" ");
  Serial.print(b);
  Serial.print(" ");
  Serial.print(c);
  Serial.print(" ");
  Serial.print(d);
  Serial.print(" ");
  Serial.print(e);
  Serial.print(" ");
  Serial.print(f);
  Serial.print(" ");
}

int Remap(int controller_value, int orientation){ // A function which remaps the controller input from a range of 0-255
  int thruster_value = (controller_value - middle)*(ScaleFactor)*orientation; // This function converts it to a range from -300 to 300
  return thruster_value;                                                      // This is used to orientate the thrusters thrust and increase
}                                                                             // the values to the needed range
