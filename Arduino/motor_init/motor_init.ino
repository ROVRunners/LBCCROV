/**
 * @file Arduino_Bottom_PiControl_2024.ino
 * @brief Control code for 6 motors.
 *
 * This code controls 6 motors:
 *   - Vertical: Front, Rear
 *   - Horizontal: Front Right, Front Left, Rear Right, Rear Left
 *
 * The serial input string format is as follows: "FV RV FR FL RR RL"
 *
 * The code initializes the pins for each motor, reads serial input, extracts values from the input string,
 * converts the values to integers, ensures that the values are within the specified bounds, and sets the speed
 * of each motor accordingly. It also includes a delay to control the rate at which new input is checked.
 *
 * The code also provides functions for clamping a value between a minimum and maximum range, and stopping all
 * motor movements by setting the PWM values to a halt value.
 */
#include <Servo.h>

//   Vertical: Front, Rear
// Motor Front Vertical
int PWMFV = 3;
Servo servoFV;
// Motor Rear Vertical
int PWMRV = 5;
Servo servoRV;
//   Horizontal: Front Right, Front Left, Rear Right, Rear Left
// Motor Front Right
int PWMFR = 6;
Servo servoFR;
// Motor Front Left
int PWMFL = 9;
Servo servoFL;
// Motor Rear Right
int PWMRR = 10;
Servo servoRR;
// Motor Rear Left
int PWMRL = 11;
Servo servoRL;

// Array of servos
Servo servoArr[] = {servoFV, servoRV, servoFR, servoFL, servoRR, servoRL};

// Array of PWM pins
int PWMArr[] = {PWMFV, PWMRV, PWMFR, PWMFL, PWMRR, PWMRL};

// Intermediaries for translation of incoming string.
String stringStream = "";
String value[] = {"0", "0", "0", "0", "0", "0"};
int intStream[] = {0, 0, 0, 0, 0, 0};
int speed[] = {0, 0, 0, 0, 0, 0};

// Halt value for all motors.
int HaltPWM = 1500;

long timeSince = millis();


/**
 * @brief This function is called once at the start of the program.
 * It is used to initialize variables, set pin modes, and perform any other setup tasks.
 */
void setup()
{

  // Initialize serial communication.
  Serial.begin(115200);
  Serial.setTimeout(20);

  Serial.println("Setting up motors.");

  for (int i = 0; i < 6; i++)
  {
    servoArr[i].attach(PWMArr[i]);
    servoArr[i].writeMicroseconds(HaltPWM);
  }

  Serial.println("Motors set up.");
  Serial.println("Waiting to complete initialization.");

  delay(7000);

  Serial.println("Initialization complete.");

  timeSince = millis();

}


/**
 * Extracts values from a string and stores them in an array.
 * The string should contain two values separated by a space.
 * 
 * @param data The input string from which values are extracted.
 */
void getValue(String data)
{
  int count = 0;
  int priorEnd = 0;

  for (int i = 0; i < 6; i++)
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



/**
 * Function to verify the serial input.
 * 
 * This function waits for serial input and verifies its length.
 * If the length is less than or equal to 3, it prints "N/A 2" to the serial monitor.
 */
int verify()
{

  // Wait for serial input.
  while (!Serial)
  {
    // Serial.println("N/A 1");
    delay(100);
    if (millis() - timeSince >= 1000)
    {
      stop();
    }
  }
  
  if (millis() - timeSince >= 1000)
  {
    stop();
  }
  
  // Read and varify its length.
  stringStream = Serial.readStringUntil('\n');
  if (!(stringStream.length() > 5))
  {
    // Serial.println("N/A 2");
    return 0;
  }
  return 1;
}


/**
 * @brief The main loop of the program.
 * 
 * This function is responsible for continuously executing the main logic of the program.
 * It waits for valid serial input, extracts values from the input string, converts the values to integers,
 * ensures that the values are within the specified bounds, and sets the speed of each motor accordingly.
 * It also includes a delay to control the rate at which new input is checked.
 */
void loop()
{
  // Wait for valid serial input.
  if (verify()) {
    timeSince = millis();

    // Extract values from the string. (basically an inefficient .split() function)
    getValue(stringStream);

    // Convert the values to integers.
    for (int i = 0; i < 6; i++)
    {

      speed[i] = abs(value[i].toInt()); // [0] = FV, [1] = RV, [2] = FR, [3] = FL, [4] = RR, [5] = RL

      // Serial.print(speed[i]);
      // Serial.print(", ");

    }
    // Serial.println("");

    // Make sure stuff is within bounds.
    for (int i = 0; i < 6; i++)
    {
      speed[i] = bound(speed[i], 1100, 1900);
    }

    // Set the speed of each motor.
    for (int i = 0; i < 6; i++)
    {
      servoArr[i].writeMicroseconds(speed[i]);
    }
  }
  // If there was no input, sleep.
  else {
    delay(20);
  }

}


/**
 * Clamps a value between a minimum and maximum range.
 *
 * @param val The value to be clamped.
 * @param min The minimum value of the range.
 * @param max The maximum value of the range.
 * @return The clamped value.
 */
int bound(int val, int min, int max)
{
  return max(min(val, max), min);
}


/**
 * Stops all motor movements by setting the PWM values to a halt value.
 */
void stop()
{
  // Set the speed of each motor.
  for (int i = 0; i < 6; i++)
  {
    servoArr[i].writeMicroseconds(HaltPWM);
  }
}