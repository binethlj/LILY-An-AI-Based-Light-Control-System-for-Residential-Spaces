// ================= PINS =================
int living1Pin = 3;
int living2Pin = 5;

int bedroom1Pin = 9;
int bedroom2Pin = 10;

int bathroom1Pin = 2;
int bathroom2Pin = 4;

int outdoorPin = 8;
int panelPin = 12;

int trigPin = 7;
int echoPin = 6;

// ================= DIMMING =================
int currentLiving1 = 0;
int currentLiving2 = 0;

int currentBedroom1 = 0;
int currentBedroom2 = 0;

int targetLiving1 = 0;
int targetLiving2 = 0;

int targetBedroom1 = 0;
int targetBedroom2 = 0;

unsigned long lastUpdate = 0;
const int fadeDelay = 8;
const int fadeStep = 1;

// ================= BATHROOM =================
bool bathroomState = false;
bool sleepMode = false;

unsigned long lastDetection = 0;
const int detectionCooldown = 2000;

// ================= DISTANCE =================
long readDistance() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0) return -1;

  return duration * 0.034 / 2;
}

// ================= SETUP =================
void setup() {

  Serial.begin(9600);

  pinMode(living1Pin, OUTPUT);
  pinMode(living2Pin, OUTPUT);

  pinMode(bedroom1Pin, OUTPUT);
  pinMode(bedroom2Pin, OUTPUT);

  pinMode(bathroom1Pin, OUTPUT);
  pinMode(bathroom2Pin, OUTPUT);

  pinMode(outdoorPin, OUTPUT);
  pinMode(panelPin, OUTPUT);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  digitalWrite(bathroom1Pin, LOW);
  digitalWrite(bathroom2Pin, LOW);

  digitalWrite(outdoorPin, LOW);
  digitalWrite(panelPin, LOW);
}

// ================= LOOP =================
void loop() {

  // ================= SERIAL =================
  if (Serial.available()) {

    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // ================= SLEEP MODE =================
    if (cmd == "SLEEP_MODE_ON") {

      sleepMode = true;
      bathroomState = false;

      // NIGHT LIGHT ON
      digitalWrite(bathroom1Pin, LOW);
      digitalWrite(bathroom2Pin, HIGH);

      return;
    }

    if (cmd == "SLEEP_MODE_OFF") {

      sleepMode = false;
      bathroomState = false;

      digitalWrite(bathroom1Pin, LOW);
      digitalWrite(bathroom2Pin, LOW);

      return;
    }

    // ================= BATHROOM =================
    if (cmd == "BATHROOM_ON") {

      if (sleepMode) {

        digitalWrite(bathroom1Pin, LOW);
        digitalWrite(bathroom2Pin, HIGH);

      } else {

        digitalWrite(bathroom1Pin, HIGH);
        digitalWrite(bathroom2Pin, HIGH);
      }

      bathroomState = true;
      return;
    }

    if (cmd == "BATHROOM_OFF") {

      digitalWrite(bathroom1Pin, LOW);
      digitalWrite(bathroom2Pin, LOW);

      bathroomState = false;
      return;
    }

    // ================= PANEL =================
    if (cmd == "PANEL_ON") {
      digitalWrite(panelPin, HIGH);
      return;
    }

    if (cmd == "PANEL_OFF") {
      digitalWrite(panelPin, LOW);
      return;
    }

    // ================= OUTDOOR =================
    if (cmd == "OUTDOOR_ON") {
      digitalWrite(outdoorPin, HIGH);
      return;
    }

    if (cmd == "OUTDOOR_OFF") {
      digitalWrite(outdoorPin, LOW);
      return;
    }

    // ================= PWM =================
    int first = cmd.indexOf(',');
    int second = cmd.indexOf(',', first + 1);
    int third = cmd.indexOf(',', second + 1);

    if (first > 0 && second > 0 && third > 0) {

      int p1 = cmd.substring(0, first).toInt();
      int p2 = cmd.substring(first + 1, second).toInt();
      int p3 = cmd.substring(second + 1, third).toInt();
      int p4 = cmd.substring(third + 1).toInt();

      targetLiving1 = map(p1, 0, 100, 0, 255);
      targetLiving2 = map(p2, 0, 100, 0, 255);

      targetBedroom1 = map(p3, 0, 100, 0, 255);
      targetBedroom2 = map(p4, 0, 100, 0, 255);
    }
  }

  // ================= SMOOTH DIMMING =================
  if (millis() - lastUpdate >= fadeDelay) {

    lastUpdate = millis();

    // LIVING 1
    if (currentLiving1 < targetLiving1)
      currentLiving1 += fadeStep;
    else if (currentLiving1 > targetLiving1)
      currentLiving1 -= fadeStep;

    // LIVING 2
    if (currentLiving2 < targetLiving2)
      currentLiving2 += fadeStep;
    else if (currentLiving2 > targetLiving2)
      currentLiving2 -= fadeStep;

    // BEDROOM 1
    if (currentBedroom1 < targetBedroom1)
      currentBedroom1 += fadeStep;
    else if (currentBedroom1 > targetBedroom1)
      currentBedroom1 -= fadeStep;

    // BEDROOM 2
    if (currentBedroom2 < targetBedroom2)
      currentBedroom2 += fadeStep;
    else if (currentBedroom2 > targetBedroom2)
      currentBedroom2 -= fadeStep;

    currentLiving1 = constrain(currentLiving1, 0, 255);
    currentLiving2 = constrain(currentLiving2, 0, 255);

    currentBedroom1 = constrain(currentBedroom1, 0, 255);
    currentBedroom2 = constrain(currentBedroom2, 0, 255);

    analogWrite(living1Pin, currentLiving1);
    analogWrite(living2Pin, currentLiving2);

    analogWrite(bedroom1Pin, currentBedroom1);
    analogWrite(bedroom2Pin, currentBedroom2);
  }

  // ================= ULTRASONIC =================
  long distance = readDistance();

  if (
    distance > 0 &&
    distance < 5 &&
    millis() - lastDetection > detectionCooldown
  ) {

    lastDetection = millis();

    // ================= SLEEP MODE BEHAVIOR =================
    if (sleepMode) {

      bathroomState = !bathroomState;

      // PERSON DETECTED → MAIN LIGHT ON
      if (bathroomState) {

        digitalWrite(bathroom1Pin, HIGH);
        digitalWrite(bathroom2Pin, LOW);
      }

      // EXIT / TOGGLE BACK → NIGHT LIGHT ON
      else {

        digitalWrite(bathroom1Pin, LOW);
        digitalWrite(bathroom2Pin, HIGH);
      }
    }

    // ================= NORMAL MODE =================
    else {

      bathroomState = !bathroomState;

      digitalWrite(
        bathroom1Pin,
        bathroomState ? HIGH : LOW
      );

      digitalWrite(
        bathroom2Pin,
        bathroomState ? HIGH : LOW
      );
    }
  }
}
