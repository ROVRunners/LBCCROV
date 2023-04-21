#include <PS2X_lib.h> // Bill Porter's PS2 Library
#include <Ethernet.h>
#include <EthernetUdp.h>
#define SD_SS 4//sets up ethernet communication ports, don't need to change this part


//general Ethernet object declarations
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };//connection for ethernet
IPAddress localIp(192, 168, 1, 251);    // local ip address
IPAddress destIp(192, 168, 1, 15);      // destination ip address
IPAddress ip(192, 168, 1, 15);
IPAddress remIp(92, 168, 1, 176);
unsigned int localPort = 5678;      // local port to listen on
unsigned int port = 5678;               // destination port

int count; // amount of inputs

EthernetUDP Udp;//object initialization

PS2X ps2x;

const int serverPort = 4080;
bool lasers = false, tilt = false, sensors = false;
int timer1;
int timer2;
const byte arraylength = 7, maximum = 255, minimum = 0, middle = (maximum-minimum) / 2, deadzone = 30;
byte message[arraylength], packetBuffer[arraylength], offset = 10;
int left_magnitude, right_magnitude, LY, LYC, LX, LXC, RY, RYC, RX, RXC, L1R1, LR1,countbut, mag, temperature, i;
float depth;

int count_arr[] = {1, 1, 2, 3};
int countbut_arr[] = {1,1,2};

bool controller = true
bool toggle = false

void setup() {  
  Serial.begin(9600); // Allows serial moniter
  ps2x.config_gamepad(5, 3, 6, 2, false, false); // (clock, command, attention, data, Pressures, Rumble)
  Ethernet.begin(mac, localIp);    // Static IP version
  Ethernet.begin(mac, ip);
  Udp.begin(port);
  Udp.begin(localPort);
  
}

void loop() {
  timer1 = millis();
  read_PS2(); // Reads the PS2 values and adjusts the analog stick values to useful ranges
  buttons(); // Reads PS2 button values
  fillmessage();  //fills the array that is to be sent
  sendmessage();  //sends the array to the slave arduino
  //print_sent(); //prints out all the information to be sent in the array
  //print_recieved();//prints out the data that was recieved

  delay(30);
}

void fillmessage(){
  //fills the array with controller values that will be sent over ethernet
  message[0] = LX; // Strafe
  message[1] = LY; // forwards/backwards
  message[2] = RX; // Turn
  message[3] = RY; // Tilt forwards/back
  message[4] = count; 
  message[5] = L1R1; // Up/down
  message[6] = countbut; 
}

void sendmessage(){//sends the message
  Udp.beginPacket(destIp, port);
  Udp.write(message,arraylength);
  Udp.endPacket();
  
  delay(50);
}

void print_sent(){ // a loop to walk through the sent ethernet packet, to look at the values it contains
  Serial.println();
  for(i = 0; i < arraylength; i++){
    Serial.print(message[i]);
    Serial.print(" ");
  }
}

void print_recieved(){
  Serial.println();
  for(i = 0; i < arraylength; i++){
    Serial.print(packetBuffer[i]);
    Serial.print(" ");
  }
}

int check_count(int controller_value){ //this function checks to see if the input is in deadspace
  if(controller_value == middle){      // if it is in deadspace it maps the value to a 0 if it is not
    return 0;                         // it then becomes a one 
  }
   else{
    return 1;
  }
}

int check_deadzone(int controller_value){
  //if toggle is in deadband it sets the value to 0(middle variable)
  //returns the middle of the possible controller value if the controller value isn't past the deadzone area
  //Essentially making it so small unwanted movements in the controller won't cause the thrusters to move
  if(abs(controller_value-middle)>deadzone){
    controller_value = controller_value;
  }
  else{
    controller_value = middle;
  }
  return controller_value;
}

void read_PS2(){
  if controller {
    ps2x.read_gamepad(); //Needs to be called at least once a second
    
    LY = ps2x.Analog(PSS_LY); //left Stick Up and Down  //Analog Stick readings
    LX = ps2x.Analog(PSS_LX); //Left Stick Left and Right
    RY = ps2x.Analog(PSS_RY); //Right Stick Up and Down
    RX = ps2x.Analog(PSS_RX); //Right Stick Left and Right
  }
  else {
    if (Serial.available() >= 2) {
      int num1 = Serial.read();
      int num2 = Serial.read();

      LY = 255; //left Stick Up and Down  //Analog Stick readings
      LX = 128; //Left Stick Left and Right
      RY = 128 * 2 * num1; //Right Stick Up and Down
      RX = 128 * 2 * num2; //Right Stick Left and Right
    }
    else {
      LY = 128; //left Stick Up and Down  //Analog Stick readings
      LX = 128; //Left Stick Left and Right
      RY = 128; //Right Stick Up and Down
      RX = 128; //Right Stick Left and Right
    }
  }

  if (ps2x.Button(PSB_L1) && ps2x.Button(PSB_R1) && ps2x.Button(PSB_START)) {
    if !toggle {
      controller = !controller
      toggle = true
    }
  }
  else {
    toggle = false
  }
    
  LY = check_deadzone(LY);//sets to Middle if it's within a certain range
  LX = check_deadzone(LX);
  RY = check_deadzone(RY);
  RX = check_deadzone(RX);

  LYC = check_count(LY); // toggles the counters between 1 and 0
  LXC = check_count(LX);
  RYC = check_count(RY);
  RXC = check_count(RX);

  count = count_arr[LYC + LXC + RXC]; //Counts the number of inputs being used 
  
}

void buttons(){ //A function to go and check if any buttons on the controller have been pressed
  ps2x.read_gamepad();
  if (ps2x.Button(PSB_L1)){ // the ps2x.Button() function returns true or false depending if the button has been pressed
    L1R1=minimum; //Value to represent full down
    LR1 = 1; //Counter variable so multiple inputs can be used
  } 
  else if (ps2x.Button(PSB_R1)){
    L1R1=maximum; // Value to represent full up
    LR1 = 1;
  } else{
    L1R1=middle;
  }
  countbut = countbut_arr[RYC+LR1];
  }
  
  
