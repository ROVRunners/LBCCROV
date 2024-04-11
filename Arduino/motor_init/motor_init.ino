#include <Servo.h>

int outputPin = 9;       // LED connected to digital pin 9
int pwmFrequency = 1500;  // Desired PWM frequency in Hz
Servo servo;

void setup() {
  servo.attach(outputPin);
  servo.writeMicroseconds(pwmFrequency);
  delay(7000);
  // Adjust the duty cycle as needed
  servo.writeMicroseconds(1700);
  delay(5000);
  servo.writeMicroseconds(1500);
  delay(5000)
}

void loop() {
}