// Litter-Robot Control Sketch for Arduino Nano

// Pin definitions
#define HALL_HOME 2     // Hall sensor for home position (LOW when detected)
#define HALL_DUMP 3     // Hall sensor for dump position (LOW when detected)
#define CAT_SENSOR 4    // Cat sensor switch (LOW when cat detected)
#define BTN_CYCLE 5     // Optional cycle button (LOW when pressed)
#define BTN_EMPTY 6     // Optional empty button
#define BTN_FILL 7      // Optional fill button
#define LED_GREEN 8     // Optional status LEDs
#define LED_YELLOW 9
#define LED_RED 10
#define MOTOR_PWM 11    // PWM for speed (255 = full)
#define MOTOR_IN1 12    // Forward
#define MOTOR_IN2 13    // Reverse
#define CURRENT_PIN A0  // Optional current sense (from L298N or ACS712)

// Constants
const unsigned long WAIT_AFTER_CAT = 420000;  // 7 minutes in ms
const int ROTATION_TIMEOUT = 60000;           // 1 min max rotation time
const int CURRENT_THRESHOLD = 800;            // Adjust based on motor (analog value ~1A)

enum State { IDLE, WAITING, CYCLING, DUMPING, HOMING, ERROR };
State currentState = IDLE;

unsigned long catExitTime = 0;
bool catDetected = false;

// Function Prototypes
void rotateCW();
void rotateCCW();
void stopMotor();
bool monitorRotation(int targetHall);
void reverseBriefly();
void checkButtons();

void setup() {
  pinMode(HALL_HOME, INPUT_PULLUP);
  pinMode(HALL_DUMP, INPUT_PULLUP);
  pinMode(CAT_SENSOR, INPUT_PULLUP);
  pinMode(BTN_CYCLE, INPUT_PULLUP);
  pinMode(BTN_EMPTY, INPUT_PULLUP);
  pinMode(BTN_FILL, INPUT_PULLUP);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  pinMode(MOTOR_PWM, OUTPUT);

  digitalWrite(LED_GREEN, HIGH);  // Ready
  stopMotor();
}

void loop() {
  checkButtons();  // Optional manual overrides

  switch (currentState) {
    case IDLE:
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(LED_YELLOW, LOW);
      digitalWrite(LED_RED, LOW);
      if (digitalRead(CAT_SENSOR) == LOW) {  // Cat entered
        catDetected = true;
      } else if (catDetected) {  // Cat exited
        catDetected = false;
        catExitTime = millis();
        currentState = WAITING;
      }
      break;

    case WAITING:
      digitalWrite(LED_YELLOW, HIGH);  // In use/waiting
      if (millis() - catExitTime >= WAIT_AFTER_CAT) {
        currentState = CYCLING;
      }
      if (digitalRead(CAT_SENSOR) == LOW) {  // Cat re-entered
        catExitTime = millis();  // Reset timer
      }
      break;

    case CYCLING:
      digitalWrite(LED_YELLOW, HIGH);
      rotateCW();  // Rotate to sift/dump
      if (monitorRotation(HALL_DUMP)) {
        delay(2000);  // Pause at dump
        currentState = HOMING;
      }
      break;

    case HOMING:
      rotateCCW();  // Return to home
      if (monitorRotation(HALL_HOME)) {
        currentState = IDLE;
      }
      break;

    case ERROR:
      digitalWrite(LED_RED, HIGH);
      stopMotor();
      // Reset after 10s or button press
      delay(10000);
      currentState = IDLE;
      break;
  }
}

// Motor functions
void rotateCW() {
  digitalWrite(MOTOR_IN1, HIGH);
  digitalWrite(MOTOR_IN2, LOW);
  analogWrite(MOTOR_PWM, 255);  // Full speed; adjust if too fast
}

void rotateCCW() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, HIGH);
  analogWrite(MOTOR_PWM, 255);
}

void stopMotor() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
  analogWrite(MOTOR_PWM, 0);
}

// Monitor rotation for position or error
bool monitorRotation(int targetHall) {
  unsigned long startTime = millis();
  while (millis() - startTime < ROTATION_TIMEOUT) {
    if (digitalRead(CAT_SENSOR) == LOW) {  // Cat interrupt
      reverseBriefly();
      currentState = ERROR;
      return false;
    }
    // Optional: Uncomment if Current Sensor is connected
    /*
    if (analogRead(CURRENT_PIN) > CURRENT_THRESHOLD) {  // Obstruction
      reverseBriefly();
      currentState = ERROR;
      return false;
    }
    */
    if (digitalRead(targetHall) == LOW) {
      stopMotor();
      return true;
    }
  }
  currentState = ERROR;  // Timeout
  return false;
}

void reverseBriefly() {
  // Reverse direction for 2s to clear pinch
  if (digitalRead(MOTOR_IN1) == HIGH) {
    rotateCCW();
  } else {
    rotateCW();
  }
  delay(2000);
  stopMotor();
}

// Optional manual buttons
void checkButtons() {
  if (digitalRead(BTN_CYCLE) == LOW) {
    currentState = CYCLING;
  }
  if (digitalRead(BTN_EMPTY) == LOW) {
    // Rotate to dump and hold
    rotateCW();
    while (digitalRead(BTN_EMPTY) == LOW);  // Hold until release
    currentState = HOMING;
  }
  if (digitalRead(BTN_FILL) == LOW) {
    // Slight rotation for fill, adjust as needed
    rotateCCW();
    delay(5000);  // 5s example
    stopMotor();
  }
}
