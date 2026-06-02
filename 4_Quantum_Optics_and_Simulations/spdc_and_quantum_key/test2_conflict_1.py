const int laserPin = 7;
const int sensorLeft = A0;
const int sensorRight = A1;

int R1 = 0;
int R2 = 0;
bool calibrated = false;

String bitstream = "";
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 1000;  // Send every 1 second
const int sampleCount = 100;

void calibrateSensors() {
  long sumL = 0;
  long sumR = 0;

  digitalWrite(laserPin, HIGH);  // Turn ON laser for calibration
  delay(100);

  for (int i = 0; i < sampleCount; i++) {
    sumL += analogRead(sensorLeft);
    sumR += analogRead(sensorRight);
    delay(5);
  }

  R1 = sumL / sampleCount;
  R2 = sumR / sampleCount;

  digitalWrite(laserPin, LOW);  // Turn OFF laser after calibration
  calibrated = true;
  Serial.print("[Calibration] R1: "); Serial.print(R1);
  Serial.print("  R2: "); Serial.println(R2);
}

void setup() {
  pinMode(laserPin, OUTPUT);
  Serial.begin(115200);
  calibrateSensors();
}

void loop() {
  if (!calibrated) return;

  digitalWrite(laserPin, HIGH);    // Turn ON laser
  delayMicroseconds(50);
  int valL = analogRead(sensorLeft);
  int valR = analogRead(sensorRight);
  digitalWrite(laserPin, LOW);     // Turn OFF laser
  delayMicroseconds(50);

  // Calculate deviation from reference
  int devL = abs(valL - R1);
  int devR = abs(valR - R2);

  if (devL > devR) {
    bitstream += "0";
  } else if (devR > devL) {
    bitstream += "1";
  } // discard if equal

  // Periodically send bitstream
  if (millis() - lastSendTime >= sendInterval) {
    if (bitstream.length() > 0) {
      Serial.println(bitstream);
      bitstream = "";
    }
    lastSendTime = millis();
  }


}
