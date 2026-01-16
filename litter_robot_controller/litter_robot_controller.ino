#include <WiFi.h>
#include <WebServer.h>

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Pin Definitions (Must match WIRING.md)
#define PIN_MOTOR_IN1    26
#define PIN_MOTOR_IN2    27
#define PIN_MOTOR_PWM    14

#define PIN_SENSOR_CAT   33  // Weight switch (Active LOW)
#define PIN_SENSOR_HOME  32  // Home position (Active LOW)
#define PIN_SENSOR_DUMP  35  // Dump position (Active LOW)

// Timing Configuration
const unsigned long CAT_WAIT_TIME_MS = 7 * 60 * 1000; // 7 Minutes wait after cat leaves
const unsigned long CYCLE_TIMEOUT_MS = 120 * 1000;    // 2 minutes max cycle time (safety)
const int MOTOR_SPEED = 200; // 0-255

// ---------------------------------------------------------------------------
// State Machine
// ---------------------------------------------------------------------------
enum RobotState {
  STATE_IDLE,
  STATE_CAT_DETECTED,
  STATE_WAITING_FOR_CAT,
  STATE_CYCLING_TO_DUMP,
  STATE_DUMPING_PAUSE,
  STATE_CYCLING_TO_HOME,
  STATE_ERROR
};

RobotState currentState = STATE_IDLE;
unsigned long stateStartTime = 0;
unsigned long catLeftTime = 0;

WebServer server(80);

// ---------------------------------------------------------------------------
// Hardware Abstraction
// ---------------------------------------------------------------------------

void setupMotor() {
  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  pinMode(PIN_MOTOR_PWM, OUTPUT);
  stopMotor();
}

void stopMotor() {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_PWM, 0);
}

void runMotorForward() {
  // Adjust direction based on your wiring
  digitalWrite(PIN_MOTOR_IN1, HIGH);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  analogWrite(PIN_MOTOR_PWM, MOTOR_SPEED);
}

void runMotorReverse() {
  // Adjust direction based on your wiring
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, HIGH);
  analogWrite(PIN_MOTOR_PWM, MOTOR_SPEED);
}

bool isCatPresent() {
  // Assuming active LOW (switch closes to GND when weight is applied)
  return digitalRead(PIN_SENSOR_CAT) == LOW;
}

bool isAtHome() {
  return digitalRead(PIN_SENSOR_HOME) == LOW;
}

bool isAtDump() {
  return digitalRead(PIN_SENSOR_DUMP) == LOW;
}

// ---------------------------------------------------------------------------
// Web Server
// ---------------------------------------------------------------------------

void handleRoot() {
  String html = "<html><head><title>Litter Robot Controller</title>";
  html += "<style>body{font-family:sans-serif; text-align:center; padding:20px;}";
  html += ".state{font-size:24px; font-weight:bold; margin:20px;}";
  html += ".btn{padding:10px 20px; font-size:18px; margin:5px;}</style></head><body>";

  html += "<h1>Litter Robot Status</h1>";
  html += "<div class='state'>Current State: " + getStateName(currentState) + "</div>";

  if (currentState == STATE_IDLE) {
    html += "<p><a href='/cycle'><button class='btn'>Force Clean Cycle</button></a></p>";
  } else {
    html += "<p><a href='/stop'><button class='btn'>Emergency Stop / Reset</button></a></p>";
  }

  html += "<p>Cat Sensor: " + String(isCatPresent() ? "TRIGGERED" : "Clear") + "</p>";
  html += "<p>Home Sensor: " + String(isAtHome() ? "Active" : "Inactive") + "</p>";
  html += "<p>Dump Sensor: " + String(isAtDump() ? "Active" : "Inactive") + "</p>";

  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleCycle() {
  if (currentState == STATE_IDLE) {
    currentState = STATE_CYCLING_TO_DUMP;
    stateStartTime = millis();
    server.sendHeader("Location", "/");
    server.send(303);
  } else {
    server.send(200, "text/plain", "Busy!");
  }
}

void handleStop() {
  stopMotor();
  currentState = STATE_IDLE; // Reset to IDLE
  server.sendHeader("Location", "/");
  server.send(303);
}

String getStateName(RobotState state) {
  switch (state) {
    case STATE_IDLE: return "IDLE";
    case STATE_CAT_DETECTED: return "CAT DETECTED";
    case STATE_WAITING_FOR_CAT: return "WAITING (Timer)";
    case STATE_CYCLING_TO_DUMP: return "CYCLING -> DUMP";
    case STATE_DUMPING_PAUSE: return "DUMPING PAUSE";
    case STATE_CYCLING_TO_HOME: return "CYCLING -> HOME";
    case STATE_ERROR: return "ERROR";
    default: return "UNKNOWN";
  }
}

// ---------------------------------------------------------------------------
// Main Logic
// ---------------------------------------------------------------------------

void setup() {
  Serial.begin(115200);

  setupMotor();

  pinMode(PIN_SENSOR_CAT, INPUT_PULLUP);
  pinMode(PIN_SENSOR_HOME, INPUT_PULLUP);
  pinMode(PIN_SENSOR_DUMP, INPUT_PULLUP); // Note: GPIO 35 is input only, no internal pullup on some boards. Use external 10k resistor if needed.

  // Connect to WiFi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    server.on("/", handleRoot);
    server.on("/cycle", handleCycle);
    server.on("/stop", handleStop);
    server.begin();
  } else {
    Serial.println("\nWiFi Failed! Running offline mode.");
  }
}

void loop() {
  server.handleClient();

  unsigned long now = millis();

  switch (currentState) {

    // -----------------------------------------------------------------------
    // IDLE: Waiting for cat
    // -----------------------------------------------------------------------
    case STATE_IDLE:
      if (isCatPresent()) {
        currentState = STATE_CAT_DETECTED;
        Serial.println("Cat entered!");
      }
      break;

    // -----------------------------------------------------------------------
    // CAT DETECTED: Waiting for cat to leave
    // -----------------------------------------------------------------------
    case STATE_CAT_DETECTED:
      if (!isCatPresent()) {
        // Cat just left
        currentState = STATE_WAITING_FOR_CAT;
        catLeftTime = now;
        Serial.println("Cat left. Starting timer...");
      }
      break;

    // -----------------------------------------------------------------------
    // WAITING: Timer counting down
    // -----------------------------------------------------------------------
    case STATE_WAITING_FOR_CAT:
      // If cat comes back, reset
      if (isCatPresent()) {
        currentState = STATE_CAT_DETECTED;
        Serial.println("Cat returned! Timer paused.");
      }
      // If timer expires, start cycle
      else if (now - catLeftTime > CAT_WAIT_TIME_MS) {
        currentState = STATE_CYCLING_TO_DUMP;
        stateStartTime = now;
        Serial.println("Timer done. Starting cleaning cycle.");
      }
      break;

    // -----------------------------------------------------------------------
    // MOVING TO DUMP POSITION
    // -----------------------------------------------------------------------
    case STATE_CYCLING_TO_DUMP:
      runMotorForward();

      // Safety: If cat enters while moving, STOP
      if (isCatPresent()) {
        stopMotor();
        currentState = STATE_CAT_DETECTED; // Go back to waiting
        return;
      }

      // Check if we reached dump position
      if (isAtDump()) {
        stopMotor();
        currentState = STATE_DUMPING_PAUSE;
        stateStartTime = now;
        Serial.println("Reached Dump Position. Pausing.");
      }

      // Safety Timeout
      if (now - stateStartTime > CYCLE_TIMEOUT_MS) {
        stopMotor();
        currentState = STATE_ERROR;
        Serial.println("Error: Cycle Timeout (Dump)");
      }
      break;

    // -----------------------------------------------------------------------
    // PAUSE AT DUMP (Allow litter to fall)
    // -----------------------------------------------------------------------
    case STATE_DUMPING_PAUSE:
      // Wait for 2 seconds
      if (now - stateStartTime > 2000) {
        currentState = STATE_CYCLING_TO_HOME;
        stateStartTime = now;
        Serial.println("Returning Home.");
      }
      break;

    // -----------------------------------------------------------------------
    // MOVING TO HOME POSITION
    // -----------------------------------------------------------------------
    case STATE_CYCLING_TO_HOME:
      runMotorReverse();

      // Safety
      if (isCatPresent()) {
        stopMotor();
        currentState = STATE_CAT_DETECTED;
        return;
      }

      // Check if we reached home
      if (isAtHome()) {
        stopMotor();
        currentState = STATE_IDLE;
        Serial.println("Cycle Complete. Back to IDLE.");
      }

      // Safety Timeout
      if (now - stateStartTime > CYCLE_TIMEOUT_MS) {
        stopMotor();
        currentState = STATE_ERROR;
        Serial.println("Error: Cycle Timeout (Home)");
      }
      break;

    // -----------------------------------------------------------------------
    // ERROR STATE
    // -----------------------------------------------------------------------
    case STATE_ERROR:
      stopMotor();
      // Blink LED or wait for manual reset via Web UI
      break;
  }
}
