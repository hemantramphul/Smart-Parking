#include <Servo.h>
// Connection from Raspberry Pi 4 to Arduino

Servo P1_SERVO; // Create servo object to control Parking 1 servo
Servo P2_SERVO; // Create servo object to control Parking 2 servo
int P1_LED1_PIN = 5; // Assign as YELLOW Led 1 (Parking 1)
int P1_LED2_PIN = 6; // Assign as YELLOW Led 2 (Parking 1)
int P2_LED1_PIN = 9; // Assign as YELLOW Led 1 (Parking 2)
int P2_LED2_PIN = 10; // Assign as YELLOW Led 2 (Parking 2)

int P1_SERVO_PIN = 11; // Assign servo (Parking 1)
int P2_SERVO_PIN = 12; // Assign servo (Parking 1)

String MSG; // Read Input
bool P1_AVAILABLE = true; // Disponibility of Parking 1
bool P2_AVAILABLE = true; // Disponibility of Parking 2

int pos = 0; // Variable to store the servo position

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(P1_LED1_PIN, OUTPUT);
  pinMode(P1_LED2_PIN, OUTPUT);
  pinMode(P2_LED1_PIN, OUTPUT);
  pinMode(P2_LED2_PIN, OUTPUT);
  P1_SERVO.attach(11);  // Attaches the servo on pin 11 to the servo object
  P2_SERVO.attach(12);  // Attaches the servo on pin 12 to the servo object
  
  P1_SERVO.write(map(0, 0, 1023, 0, 180)); // Status: Upper (default) - Parking 1
  P2_SERVO.write(map(0, 0, 1023, 0, 180)); // Status: Upper (default) - Parking 2
  
  delay(10);
  ParkingAvailable();
}

void loop() {
  // Read serial port
  ReadSerialPort();

  // Available: Parking 1 and Parking 2
  if (MSG == "1P1") { // Available: P1_LED1_PIN ON, P1_LED2_PIN OFF
    digitalWrite(P1_LED1_PIN, HIGH); // (Parking 1)
    digitalWrite(P1_LED2_PIN, LOW); // (Parking 1)
    P1_SERVO.write(map(0, 0, 1023, 0, 180)); // Status: Upper (default) - Parking 1
    Serial.println("Parking 1 available!");
  } else if (MSG == "1P2") { // Available: P2_LED2_PIN ON, P2_LED2_PIN OFF
    digitalWrite(P2_LED1_PIN, HIGH); // (Parking 2)
    digitalWrite(P2_LED2_PIN, LOW); // (Parking 2)
    P2_SERVO.write(map(0, 0, 1023, 0, 180)); // Status: Upper (default) - Parking 2
    Serial.println("Parking 2 available!");
  }
  
  // Reserved: Parking 1 and Parking 2
  if (MSG == "2P1") { // Reserved: P1_LED1_PIN ON, P1_LED2_PIN ON
    digitalWrite(P1_LED1_PIN, HIGH); // (Parking 1)
    digitalWrite(P1_LED2_PIN, HIGH); // (Parking 1)
    Serial.println("Parking 1 reserved!");
  } else if (MSG == "2P2") { // Reserved: P2_LED1_PIN ON, P2_LED2_PIN ON
    digitalWrite(P2_LED1_PIN, HIGH); // (Parking 2)
    digitalWrite(P2_LED2_PIN, HIGH); // (Parking 2)
    Serial.println("Parking 2 reserved!");
  }

  // Reserved and Parked: Parking 1 and Parking 2
  if (MSG == "3P1") { // Reserved and Parked: P1_LED1_PIN OFF, P1_LED2_PIN ON
    digitalWrite(P1_LED1_PIN,LOW); // (Parking 1)
    digitalWrite(P1_LED2_PIN,HIGH); // (Parking 1)
    P1_SERVO.write(map(0, 0, 1023, 180, 180)); // Status: Lower/Close - Parking 1
    Serial.println("Parking 1 reserved and parked!");
  } else if (MSG == "3P2") { // Reserved and Parked: P1_LED1_PIN OFF, P1_LED2_PIN ON
    digitalWrite(P2_LED1_PIN,LOW); // (Parking 2)
    digitalWrite(P2_LED2_PIN,HIGH); // (Parking 2)
    P2_SERVO.write(map(0, 0, 1023, 180, 180)); // Status: Lower/Close (default) - Parking 2
    Serial.println("Parking 2 reserved and parked!");
  }

  // Not Reserved and Parked: Parking 1 and Parking 2
  if (MSG == "4P1") { // Reserved and Parked: P1_LED1_PIN OFF, P1_LED2_PIN ON/BLINK
    digitalWrite(P1_LED1_PIN,LOW); // (Parking 1)
    BlinkLedParking1(); // (Parking 1)
    Serial.println("Parking 1 reserved and parked!");
  } else if (MSG == "4P2") { // Reserved and Parked: P1_LED1_PIN OFF, P1_LED2_PIN ON/BLINK
    digitalWrite(P2_LED1_PIN,LOW); // (Parking 2)
    BlinkLedParking2(); // (Parking 2)
    Serial.println("Parking 2 reserved and parked!");
  }

  delay(100); // Wait
}

void ReadSerialPort() {
  MSG = "";
  // Check availability
  if (Serial.available()) {
    delay(10);
    while (Serial.available() > 0) {
      MSG += (char)Serial.read();
    }
    Serial.flush();
  }
}

void ParkingAvailable() {
  digitalWrite(P1_LED1_PIN, HIGH); // (Parking 1)
  digitalWrite(P1_LED2_PIN, LOW); // (Parking 1)
  digitalWrite(P2_LED1_PIN, HIGH); // (Parking 2)
  digitalWrite(P2_LED2_PIN, LOW); // (Parking 2)
}

void BlinkLedParking1() {
  while (Serial.available() < 2) {
    //Serial.println(Serial.available());
    digitalWrite(P1_LED2_PIN, HIGH); // (Parking 1)
    delay(500);
    digitalWrite(P1_LED2_PIN, LOW); // (Parking 1)
    delay(500);
  }
}

void BlinkLedParking2() {
  while (Serial.available() < 2) {
    //Serial.println(Serial.available());
    digitalWrite(P2_LED2_PIN, HIGH); // (Parking 2)
    delay(500);
    digitalWrite(P2_LED2_PIN, LOW); // (Parking 2)
    delay(500);
  }
}
