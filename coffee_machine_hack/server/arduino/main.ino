#include <stdio.h>

#include <SPI.h>
#include <EthernetUdp.h>

#include <coffee_com.h>
#include <coffee_ctrl.h>


/*
   Function:      perform
   Description:   Performing tasks according to parsed requests

   Args:
      parsed (ParsedRwq *): parsed request

   Returns:
      (bool): operation result, true for succeed
*/
bool perform(ParsedReq *parsed);

// Network variables
// MAC address of Arduino
byte mac[] = {
  0x90, 0xA2, 0xDA, 0x00, 0xFF, 0x24
};

// IP address of Arduino
IPAddress ip(192, 168, 10, 233);
// Port for UDP communication
uint32_t localPort = 8233;

// UDP instance
EthernetUDP udp;


// Initialization
void setup() {
  // Setup serial output
  Serial.begin(9600);
  Serial1.begin(9600);

  // Setup network
  setupNetwork(&udp, mac, &ip, localPort);
  Serial.print("Initializing network configuration... ");
  Serial.print("Working at ");
  Serial.print(Ethernet.localIP());
  Serial.print(":");
  Serial.println(localPort);

  // Turn on the machine
  Serial.print("Initializing coffee machine... ");
  String result = control((const uint8_t *)"AN:01", 5);
  if (String("ok:") == result) {
    Serial.println("Done!");
    Serial.println("Welcome!");
  }
  else {
    Serial.println("Failed!");
    Serial.print("Return value: ");
    Serial.println(result.length() > 0 ? result : "N/A");
  }
}


// Main loop
void loop() {
  // UDP read buffer
  uint8_t readBuffer[UDP_TX_PACKET_MAX_SIZE];

  // Read a packet if there is available data
  int packetSize = udp.parsePacket();
  if (packetSize) {
    Serial.println("\n==== New request...");
#ifdef HACK_DEBUG
    Serial.print("Request from: ");
    Serial.print(udp.remoteIP());
    Serial.print(":");
    Serial.println(udp.remotePort());
#endif

    // Read packet into readBuffer
    udp.read(readBuffer, UDP_TX_PACKET_MAX_SIZE);

    // Parsing content
    Serial.println("\n==== Parse message...");
    ParsedReq parsed = reqParser(readBuffer, packetSize);

    // Self-checking
    Serial.println("\n==== System self-checking...");
    update_status();

    // Perform operation
    Serial.println("\n==== Perform operation...");
    bool result = perform(&parsed);

    // Encode response
    Serial.println("\n==== Encode response...");
    uint8_t respBuf[RESP_MAX_LEN];
    int respLen = encode_resp(&parsed, result, respBuf, RESP_MAX_LEN);

    // Send response
    Serial.println("\n==== Send response...");
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.write(respBuf, respLen);
    udp.endPacket();
    Serial.println("Done!");
  }

  // Wait for finishing sending
  delay(10);
}


bool perform(ParsedReq *parsed) {
  switch (parsed->type) {
    // Perform operation type commands, e.g. turn on/off, make coffee etc.
    case TYP_REQ_OPER:
      return String("ok:") == control(parsed->content, parsed->len);
    case TYP_REQ_QSTS:
      parsed->len = 1;
      parsed->content[0] = get_status_table();

      // Checking every status
      if (is_on() && has_water() && has_bean() && has_tray())
        return true;
      else
        return false;

    default:
      return false;
  }
}
