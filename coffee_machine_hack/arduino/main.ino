#include <SPI.h>
#include <Ethernet.h>
#include <EthernetUdp.h>

/* ************************************************************************** */
/*                 Definition of data structures and variables                */
/* ************************************************************************** */

// Coffee Machine Protocol
#define TYP_REQ_OPER    1     // Operation type (turn on/off, brew coffee etc.)
#define TYP_REQ_QUERY   2     // Query type (water tank, coffee bean etc.)
#define TYP_REQ_UNKN    3     // Unknown type (format fault)

#define REQ_SIZE        6     // Correct request size

// Parsed request structure
struct ParsedReq {
  int type;
  char content;
};

// Response buffer size
#define RESP_BUF_SIZE       16


// Machine status, ture for on, false for off
boolean machineStatus = false;


// Network variables setting
// MAC address of Arduino
byte mac[] = {
  0x90, 0xA2, 0xDA, 0x00, 0xFF, 0x24
};
// IP address of Arduino
IPAddress ip(192, 168, 199, 233);

// Port for UDP communication
unsigned int localPort = 8233;
// UDP read buffer size
char readBuffer[UDP_TX_PACKET_MAX_SIZE];

// UDP instance
EthernetUDP udp;

/* ************************************************************************** */
/*                        Initialization and main loop                        */
/* ************************************************************************** */

// Setup network configuration
void setup() {
  // Setup serial output
  Serial.begin(9600);
  
  // Start the Ethernet connection
  Ethernet.begin(mac, ip);
  Serial.println("Ethernet begins");

  // Start UDP
  udp.begin(localPort);
  Serial.println("UDP begins");
}


// Main loop
void loop() {
  // Read a packet if there is available data
  int packetSize = udp.parsePacket();
  if (packetSize) {
    // Output connection information to serial port
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From: ");
    IPAddress remoteAddr = udp.remoteIP();
    for (int i = 0; i < 4; i++) {
      Serial.print(remoteAddr[i], DEC);
      if (i < 3)
        Serial.print(".");
    }
    Serial.print(", port: ");
    Serial.println(udp.remotePort());

    // Read packet into readBuffer
    udp.read(readBuffer, UDP_TX_PACKET_MAX_SIZE);
    Serial.println("Contents:");
    Serial.println(readBuffer);

    // Parsing content
    ParsedReq req = reqParser(readBuffer, packetSize);

    // Perform operation
    char respBuf[RESP_BUF_SIZE];
    int respLen = perform(req, respBuf, RESP_BUF_SIZE);

    // Send response
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.write(respBuf, respLen);
    udp.endPacket();
  }

  // Wait for finishing sending
  delay(10);
}

/* ************************************************************************** */
/*                           Definition of function                           */
/* ************************************************************************** */

/*
 * Function:      reqParser
 * Description:   Parsing the raw request data from Raspberry PI
 * 
 * Args:
 *    buf (char []): the raw data received
 *    len (int): length of the raw data
 * 
 * Returns:
 *    (ParsedReq): parsed result
 */
ParsedReq reqParser(char buf[], int len) {
  ;
}

/*
 * Function:      perform
 * Description:   Performing tasks according to parsed requests
 * 
 * Args:
 *    req (ParsedReq): parsed request
 *    buf (char []): response buffer
 *    len (int): reponse buffer's size
 * 
 * Returns:
 *    (int): response length
 */
int perform(ParsedReq req, char buf[], int len) {
  ;
}

