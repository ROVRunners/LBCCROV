//This code controls two motors

//motor A should be connected between A01 and A02

//motor B should be connected between B01 and B02

// 3, 5, 8, 9, 10, 11, 12
// 1, 2, 4, 6, 7, 13

//The below code defines the output pins on the Arduino will hookup to specified pins on the HBridge

//Motor Left Front

int PWMLF = 3; //Speed control

//Motor Right Front

int PWMRF = 5; //Speed control

//Motor C

int PWMB = 6; //Speed control

//Motor A

int PWMA = 3; //Speed control

//Motor B

int PWMA = 5; //Speed control

//Motor C

int PWMB = 6; //Speed control

String value[] = {"0", "0", "0"};

 

void setup() {

  pinMode(STBY, OUTPUT);

  // Vert Front
  pinMode(PWMA, OUTPUT);

  // Vert Rear
  pinMode(PWMA, OUTPUT);

  // Left Front
  pinMode(PWMB, OUTPUT);

  // Right Front
  pinMode(PWMC, OUTPUT);

  Serial.begin(19200);
  Serial.setTimeout(20);

}

void getValue(String data)
{
  int count = 0;
  int priorEnd = 0;

  for (int i = 0; i < data.length() - 1 && count < 2; i++)
  {
      if (data.charAt(i) == ' ')
      {
          value[count] = data.substring(priorEnd, i);
          count++;
          priorEnd = i+1;
      }
  }
  value[count] = data.substring(priorEnd, data.length());
}

String stringStream = "";
int intStream[] = {0, 0, 0};
int speed[] = {0, 0, 0};
int direction[] = {0, 0, 0};
int negator[] = {1, 1, 1};

void loop(){

  while (!Serial){
    Serial.println("N/A 1");
    delay(100);
  }

  stringStream = Serial.readString();
  if (stringStream.length() > 3) {
    // stringStream.replace("\r\n", "");
    // Serial.println(stringStream);
  } else {
    Serial.println("N/A 2");
  }
  String str = "";

  // for (int i = 0; i < 2; i++) {
  //   stringStream.remove(stringStream.length() - 1);
  // }
  getValue(stringStream);

  for (int i = 0; i < 3; i++) {

    intStream[i] = value[i].toInt(); // [0] = up/down, [1] = forward/back, [2] = pivot
    speed[i] = abs(intStream[i]);
    direction[i] = negator[i] ? intStream[i] >= 0 : -negator[i];
    str += String(i) + ": " + String(speed[i]) + " ----- ";
    // Serial.print(": ");
    // Serial.print(intStream[i]);
    // Serial.print(" ");
    // Serial.print(speed[i]);
    // Serial.print(" ");
    // Serial.print(direction[i]);
    // Serial.print(" ----- ");
  }
  Serial.println(str);

  move(0, speed[0], direction[0]); // Up
  move(1, speed[1], direction[1]); // Forward
  move(2, speed[2], direction[2]); // Pivot

  delay(20);

}


int bound(int val, int min, int max) {
  return max(min(val, max), min);
}

 

void move(int motor, int spd, int dir) {

//Move specific motor at spd and direction

//motor: 0 for B 1 for A

//spd: 0 is off, and 255 is full spd

//direction: 0 clockwise, 1 counter-clockwise

  digitalWrite(STBY, HIGH); //disable standby

  boolean inPin1 = LOW;

  boolean inPin2 = HIGH;

  if(dir == 1){

    inPin1 = HIGH;

    inPin2 = LOW;

  }

  switch (motor) {
    case (0):
      analogWrite(PWMA, spd);
      break;

    case (1):
      analogWrite(PWMB, spd);
      break;

    case (2):
      analogWrite(PWMC, spd);
      // Serial.print(" ## " + String(inPin1) + ", " + String(inPin2) + ", " + String(spd) + " ## ");
      break;

  }

}


// int[] getValue(String data, char separator, int ExpectedItemCount)
// {
//   // Read each command pair 
//   char* command = strtok(input, "&");
//   String results[ExpectedItemCount];
//   int count = 0;

//   while (command != 0 && count < ExpectedItemCount)
//   {
//       // Split the command in two values
//       char* separator = strchr(command, ':');
//       if (separator != 0)
//       {
//           // Actually split the string in 2: replace ':' with 0
//           *separator = 0;
//           int servoId = atoi(command);
//           ++separator;
//           int position = atoi(separator);

//           // Do something with servoId and position
//       }
//       // Find the next command in input string
//       command = strtok(0, "&");
//   }
// }

// String getValue(String data, char separator, int index)
// {
//     int found = 0;
//     int strIndex[] = { 0, -1 };
//     int maxIndex = data.length() - 1;

//     for (int i = 0; i <= maxIndex && found <= index; i++) {
//         if (data.charAt(i) == separator || i == maxIndex) {
//             found++;
//             strIndex[0] = strIndex[1] + 1;
//             strIndex[1] = (i == maxIndex) ? i+1 : i;
//         }
//     }
//     return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
// }

void stop(){

//enable standby 

  digitalWrite(STBY, LOW);

}