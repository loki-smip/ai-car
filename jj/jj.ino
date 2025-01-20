#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

// === CONFIGURABLE CONSTANTS ===
const char* ssid = "loki"; // Primary Wi-Fi SSID
const char* password = "12345678"; // Primary Wi-Fi Password
const char* fallback_ssid = "ESP32-Car";      // Fallback Access Point SSID
const char* fallback_password = "12345678";   // Fallback Access Point Password
const char* hostname = "esp32-car";          // mDNS Hostname

// Motor Pins (L298N)
const int motor1Pin1 = 15; // IN1
const int motor1Pin2 = 2;  // IN2
const int enable1Pin = 13; // ENA
const int motor2Pin1 = 4;  // IN3
const int motor2Pin2 = 16; // IN4
const int enable2Pin = 12; // ENB

// WebServer on port 80
WebServer server(80);

// Fallback Mode
bool fallback_mode = false;

// Motor speed (0-255)
int motorSpeed = 255; // Default speed: full speed

// === Function Prototypes ===
void handleRoot();
void handleForward();
void handleLeft();
void handleRight();
void handleReverse();
void handleStop();
void handleSetSpeed();
void setupFallbackAP();

// === Web Interface ===
const char html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
    html { font-family: Helvetica; text-align: center; }
    .button { background-color: #4CAF50; border: none; color: white; padding: 16px; margin: 4px; cursor: pointer; font-size: 20px; }
    .button-stop { background-color: #f44336; }
    .slider { width: 50%; }
  </style>
</head>
<body>
  <h1>ESP32 Car Control</h1>
  <p><button class="button" onclick="fetch('/forward')">FORWARD</button></p>
  <p>
    <button class="button" onclick="fetch('/left')">LEFT</button>
    <button class="button button-stop" onclick="fetch('/stop')">STOP</button>
    <button class="button" onclick="fetch('/right')">RIGHT</button>
  </p>
  <p><button class="button" onclick="fetch('/reverse')">REVERSE</button></p>
  <p>
    <label for="speed">Speed:</label>
    <input type="range" id="speed" class="slider" min="0" max="255" value="255" onchange="setSpeed(this.value)">
    <p id="speedValue">Speed: 255</p>
  </p>

  <script>
    function setSpeed(value) {
      document.getElementById('speedValue').innerHTML = "Speed: " + value;
      fetch('/setSpeed?value=' + value);
    }
  </script>
</body>
</html>)rawliteral";

// === Web Handlers ===
void handleRoot() {
  server.send(200, "text/html", html);
}

void handleForward() {
  Serial.println("Forward");
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, HIGH);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, HIGH);
  analogWrite(enable1Pin, motorSpeed); // Adjust speed with PWM
  analogWrite(enable2Pin, motorSpeed); // Adjust speed with PWM
  server.send(200);
}

void handleLeft() {
  Serial.println("Left");
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, HIGH);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, LOW);
  analogWrite(enable1Pin, motorSpeed); // Adjust speed with PWM
  analogWrite(enable2Pin, motorSpeed); // Adjust speed with PWM
  server.send(200);
}

void handleRight() {
  Serial.println("Right");
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, HIGH);
  analogWrite(enable1Pin, motorSpeed); // Adjust speed with PWM
  analogWrite(enable2Pin, motorSpeed); // Adjust speed with PWM
  server.send(200);
}

void handleReverse() {
  Serial.println("Reverse");
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, HIGH);
  digitalWrite(motor2Pin2, LOW);
  analogWrite(enable1Pin, motorSpeed); // Adjust speed with PWM
  analogWrite(enable2Pin, motorSpeed); // Adjust speed with PWM
  server.send(200);
}

void handleStop() {
  Serial.println("Stop");
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, LOW);
  analogWrite(enable1Pin, 0); // Stop motor 1
  analogWrite(enable2Pin, 0); // Stop motor 2
  server.send(200);
}

// Handle speed change
void handleSetSpeed() {
  if (server.hasArg("value")) {
    motorSpeed = server.arg("value").toInt();
    Serial.print("Speed set to: ");
    Serial.println(motorSpeed);
  }
  server.send(200);
}

// === Setup Fallback AP ===
void setupFallbackAP() {
  WiFi.softAP(fallback_ssid, fallback_password);
  IPAddress IP = WiFi.softAPIP();
  Serial.println("Fallback AP started");
  Serial.print("IP address: ");
  Serial.println(IP);
  fallback_mode = true;
}

// === Setup and Loop ===
void setup() {
  Serial.begin(115200);

  // Motor Pins as Outputs
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(motor2Pin1, OUTPUT);
  pinMode(motor2Pin2, OUTPUT);
  pinMode(enable1Pin, OUTPUT);  // Motor speed control (ENA)
  pinMode(enable2Pin, OUTPUT);  // Motor speed control (ENB)

  // Start WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 20000) {
    delay(500);
    Serial.print("...");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nWiFi connection failed. Starting fallback AP...");
    setupFallbackAP();
  } else {
    Serial.println("\nWiFi connected.");
    Serial.println("IP Address: " + WiFi.localIP().toString());

    if (!MDNS.begin(hostname)) {
      Serial.println("Error starting mDNS");
    }
    Serial.println("mDNS responder started");
  }

  // Define Web Server Routes
  server.on("/", handleRoot);
  server.on("/forward", handleForward);
  server.on("/left", handleLeft);
  server.on("/right", handleRight);
  server.on("/reverse", handleReverse);
  server.on("/stop", handleStop);
  server.on("/setSpeed", handleSetSpeed);  // Route for speed control
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
