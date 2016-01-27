#include <SPI.h>
#include <EthernetUdp.h>

#include <coffee_com.h>
#include <coffee_ctrl.h>


/*
   Function:      perform
   Description:   Performing tasks according to parsed requests

   Args:
      parsed (const ParsedRwq *): parsed request
      buf (uint8_t *): response buffer
      len (int): reponse buffer's size

   Returns:
      (bool): operation result, true for succeed
*/
bool perform(const ParsedReq *parsed);

// Network variables
// MAC address of Arduino
byte mac[] = {
  0x90, 0xA2, 0xDA, 0x00, 0xFF, 0x24
};

// IP address of Arduino
IPAddress ip(192, 168, 199, 233);
// Port for UDP communication
uint32_t localPort = 8233;

// UDP instance
EthernetUDP udp;


// Initialization
void setup() {
  // Setup serial output
  Serial.begin(9600);

  // Setup network
  setupNetwork(&udp, mac, &ip, localPort);
  Serial.println("Welcome");
  Serial.print("Working at ");
  Serial.print(Ethernet.localIP());
  Serial.print(":");
  Serial.println(localPort);
}


// Main loop
void loop() {
  // UDP read buffer
  uint8_t readBuffer[UDP_TX_PACKET_MAX_SIZE];

  // Read a packet if there is available data
  int packetSize = udp.parsePacket();
  if (packetSize) {
    Serial.println("New REQ");

    // Read packet into readBuffer
    udp.read(readBuffer, UDP_TX_PACKET_MAX_SIZE);

    // Parsing content
    Serial.print("Parse message... ");
    ParsedReq parsed = reqParser(readBuffer, packetSize);

    // Perform operation
    Serial.print("Perform operation... ");
    bool result = perform(&parsed);

    // Encode response
    Serial.print("Encode response... ");
    uint8_t respBuf[RESP_MAX_LEN];
    int respLen = encode_resp(&parsed, result, respBuf, RESP_MAX_LEN);

    // Send response
    Serial.print("Send response... ");
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.write(respBuf, respLen);
    udp.endPacket();
    Serial.println("Done!");
  }

  // Wait for finishing sending
  delay(10);
}


bool perform(const ParsedReq *parsed) {
  if (parsed->type == TYP_REQ_OPER)
    return control(parsed->content, parsed->len);
  else if (parsed->type == TYP_REQ_QWT)
    return has_water();
  else if (parsed->type == TYP_REQ_QBA)
    return has_bean();
  else
    return false;
}
