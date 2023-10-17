int mosfetGatePin = 7;

void setup() {
  Serial.begin(9600); // initialize serial communication at 9600 bps
  pinMode(mosfetGatePin, OUTPUT); 
  digitalWrite(mosfetGatePin, LOW); // Ensure MOSFET is OFF at startup
}

void loop() {
  if (Serial.available() > 0) {
    char inChar = Serial.read(); // Read the incoming data
    if (inChar == '1') {
      Serial.println("striking...\n");
      digitalWrite(mosfetGatePin, HIGH); // Turn ON the MOSFET
      delay(5000); // Keep the door strike activated for 5 seconds
      digitalWrite(mosfetGatePin, LOW); // Turn OFF the MOSFET
    }
    if (inChar == 'Q') {  // Add a query-response mechanism
      Serial.println("Arduino_Online");
    }
  }
}
