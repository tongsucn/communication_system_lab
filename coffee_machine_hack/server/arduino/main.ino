#include <SPI.h>
#include <Ethernet.h>
#include <EthernetUdp.h>

#include <string.h>

#include <coffee.pb.h>
#include <pb_encode.h>
#include <pb_decode.h>


/* ************************************************************************** */
/*                 Definition of data structures and variables                */
/* ************************************************************************** */


// Coffee Machine Protocol
#define TYP_REQ_OPER    1     // Operation type (turn on/off, brew coffee etc.)
#define TYP_REQ_QWT     2     // Query type: water tank
#define TYP_REQ_QBA     3     // Query type: bean available
#define TYP_REQ_UNKN    4     // Unknown type (format fault)

#define BIN_CODE_LEN    28    // Machine binary code length

uint8_t lineEnd[] = {0xDB, 0xDB, 0xFF, 0xDF, 0xDB, 0xDB, 0xFB, 0xFB};

// Parsed request structure
struct ParsedReq {
  int type;
  int len;
  uint8_t content[BIN_CODE_LEN];
};

// General buffer for getting bytes field content and parsing request
#define GEN_BUF_SIZE  64
struct GeneralBuffer {
  uint8_t buf[GEN_BUF_SIZE];
};

// Response maximum length
#define RESP_MAX_LEN    64


// Network variables setting
// MAC address of Arduino
byte mac[] = {
  0x90, 0xA2, 0xDA, 0x00, 0xFF, 0x24
};
// IP address of Arduino
IPAddress ip(192, 168, 199, 233);

// Port for UDP communication
uint32_t localPort = 8233;
// UDP read buffer
uint8_t readBuffer[UDP_TX_PACKET_MAX_SIZE];

// UDP instance
EthernetUDP udp;


/* ************************************************************************** */
/*                          Declaration of functions                          */
/* ************************************************************************** */


/*
   Function:      reqParser
   Description:   Parsing the raw request data from Raspberry PI

   Args:
      buf (uint8_t *): the raw data received
      len (int): length of the raw data

   Returns:
      (ParsedReq): parsed request structure
*/
ParsedReq reqParser(uint8_t *buf, int len);

/*
   Function:      cmd_decode_cb
   Description:   Callback function for decoding bytes field "command"

   Args:
      stream (pb_istream_t *): input stream of bytes field
      field (const pb_field_t *): field descriptor in structure
      arg (void **): parameter for storing parsing result

   Returns:
      (bool): return true if parsing succeed, otherwise return false
*/
bool cmd_decode_cb(pb_istream_t *stream, const pb_field_t *field, void **arg);

/*
   Function:      perform
   Description:   Performing tasks according to parsed requests

   Args:
      parsed (ParsedRwq): parsed request
      buf (uint8_t *): response buffer
      len (int): reponse buffer's size

   Returns:
      (int): response length
*/
int perform(uint8_t *buf, int len);

/*
   Function:      resp_encode_cb
   Description:   Callback function for encoding string field "description"

   Args:
      stream (pb_ostream_t *): output stream of string field
      field (const pb_field_t *): field descriptor in structure
      arg (void * const*): parameter for providing parsing result

   Returns:
      (bool): return true if encoding succeed, otherwise return false
*/
bool resp_encode_cb(pb_ostream_t *stream, const pb_field_t *field,
                    void * const *arg);

/*
   Function:      control
   Description:   Control the machine

   Args:
      cmd (uint8_t *): extended command content
      len (int): command length

   Returns:
      (bool): if tasks finish successfully then return true, else false
*/
bool control(uint8_t *cmd, int len);

/*
   Function:      has_water
   Description:   Checking water tank status

   Returns:
      (bool): if water is available then return true, otherwise false
*/
bool has_water();

/*
   Function:      has_bean
   Description:   Checking bean availability

   Returns:
      (bool): if bean is available then return true, otherwise false
*/
bool has_bean();


/* ************************************************************************** */
/*                        Initialization and main loop                        */
/* ************************************************************************** */


// Setup network configuration
void setup() {
  // Setup serial output
  Serial.begin(9600);

  // Start the Ethernet connection
  Ethernet.begin(mac, ip);

  // Start UDP
  udp.begin(localPort);
  Serial.println("Welcome");
}


// Main loop
void loop() {
  // Read a packet if there is available data
  int packetSize = udp.parsePacket();
  if (packetSize) {
    Serial.println("New REQ");

    // Read packet into readBuffer
    udp.read(readBuffer, UDP_TX_PACKET_MAX_SIZE);

    // Parsing content
    Serial.println("==== Parse message ====");
    ParsedReq parsed = reqParser(readBuffer, packetSize);

    // Perform operation
    Serial.println("==== Perform operation ====");
    uint8_t respBuf[RESP_MAX_LEN];
    int respLen = perform(parsed, respBuf, RESP_MAX_LEN);

    Serial.print("0x");
    Serial.println(respBuf[0], HEX);
    Serial.print("0x");
    Serial.println(respBuf[1], HEX);
    Serial.print("0x");
    Serial.println(respBuf[2], HEX);

    // Send response
    Serial.println("==== Send response ====");
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


ParsedReq reqParser(uint8_t *buf, int len) {
  // Structure for storing parsed request
  ParsedReq parsed;
  // Buffer for getting command content in callback function
  GeneralBuffer decodeBuf;
  // Structure for getting command content in callback function
  CoffeeCommand rawCmd;
  // Set callback function for decoding
  rawCmd.command.funcs.decode = cmd_decode_cb;
  rawCmd.command.arg = &decodeBuf;

  // Read received message as input stream
  pb_istream_t istreamCmd = pb_istream_from_buffer(buf, len);

  // Parse input stream
  if (!pb_decode(&istreamCmd, CoffeeCommand_fields, &rawCmd)) {
    parsed.type = TYP_REQ_UNKN;
  }
  else {
    if (rawCmd.type
        == CoffeeCommand_CommandType_OPERATION) {
      parsed.type = TYP_REQ_OPER;
      parsed.len = BIN_CODE_LEN;
      memset(&parsed.content, 255, BIN_CODE_LEN - 8);

      // Formatting command
      for (int i = 0; i < 5; i++)
        for (int j = 0; j < 4; j++) {
          bitWrite(parsed.content[i * 4 + j], 2,
                   bitRead(decodeBuf.buf[i], j * 2));
          bitWrite(parsed.content[i * 4 + j], 5,
                   bitRead(decodeBuf.buf[i], j * 2 + 1));
        }

      // Formatting line ends
      memcpy(&parsed.content[20], lineEnd, 8);
    }
    else if (rawCmd.type
             == CoffeeCommand_CommandType_QUERY) {
      if (decodeBuf.buf[0] == 'W')
        parsed.type = TYP_REQ_QWT;
      else if (decodeBuf.buf[0] == 'B')
        parsed.type = TYP_REQ_QBA;
      else
        parsed.type = TYP_REQ_UNKN;
    }
    else
      parsed.type = TYP_REQ_UNKN;
  }

  return parsed;
}


bool cmd_decode_cb(pb_istream_t *stream, const pb_field_t *field, void **arg) {
  GeneralBuffer *bufPtr = (GeneralBuffer *)(*arg);

  if (stream->bytes_left != 5)
    return false;
  else
    pb_read(stream, bufPtr->buf, stream->bytes_left);

  return true;
}


int perform(ParsedReq parsed, uint8_t *buf, int len) {
  // Buffer for getting command content in callback function
  GeneralBuffer encodeBuf;
  // Structure for writing response content in callback function
  Response rawResp;
  rawResp.has_type = true;
  rawResp.description.funcs.encode = resp_encode_cb;
  rawResp.description.arg = &encodeBuf;

  // Relate a pb_ostream_t with a buffer
  pb_ostream_t ostreamResp = pb_ostream_from_buffer(buf, (size_t)len);

  if (parsed.type == TYP_REQ_OPER) {
    // Perform operation
    bool performSuccess = control(parsed.content, parsed.len);

    // Prepare for response of performing operations
    if (performSuccess) {
      rawResp.type = Response_ResponseType_OK;

      strncpy((char *)encodeBuf.buf,
              "Operation SUCCEED",
              GEN_BUF_SIZE);
    }
    else {
      rawResp.type = Response_ResponseType_ERR;

      strncpy((char *)encodeBuf.buf,
              "Operation FAILED",
              GEN_BUF_SIZE);
    }
  }
  else if (parsed.type == TYP_REQ_QWT) {
    // Check water tank
    bool hasWater = has_water();

    // Prepare for response of querying water tank
    if (hasWater) {
      rawResp.type = Response_ResponseType_OK;

      strncpy((char *)encodeBuf.buf,
              "Water is available",
              GEN_BUF_SIZE);
    }
    else {
      rawResp.type = Response_ResponseType_NO_WATER;

      strncpy((char *)encodeBuf.buf,
              "Water is NOT available",
              GEN_BUF_SIZE);
    }
  }
  else if (parsed.type == TYP_REQ_QBA) {
    // Check bean availablity
    bool hasBean = has_bean();

    // Prepare for response of querying bean available
    if (hasBean) {
      rawResp.type = Response_ResponseType_OK;

      strncpy((char *)encodeBuf.buf,
              "Bean is available",
              GEN_BUF_SIZE);
    }
    else {
      rawResp.type = Response_ResponseType_NO_BEAN;

      strncpy((char *)encodeBuf.buf,
              "Bean is NOT available",
              GEN_BUF_SIZE);
    }
  }
  else {
    // Prepare for response of unknown format error
    rawResp.type = Response_ResponseType_FORMAT_UNKN;

    strncpy((char *)encodeBuf.buf,
            "Request format UNKNOWN",
            GEN_BUF_SIZE);
  }

  pb_encode(&ostreamResp, Response_fields, &rawResp);
  Serial.print("Response description: ");
  Serial.println((char *)encodeBuf.buf);
  Serial.print("Response length: ");
  Serial.println(ostreamResp.bytes_written);

  return ostreamResp.bytes_written;
}


bool resp_encode_cb(pb_ostream_t *stream, const pb_field_t *field,
                    void * const *arg) {
  GeneralBuffer const *bufPtr = (GeneralBuffer const *)(*arg);

  // Tags of string/bytes fields need to be specified manually
  pb_encode_tag_for_field(stream, field);
  return pb_encode_string(stream, bufPtr->buf,
                          strlen((const char *)bufPtr->buf));
}


bool control(uint8_t *cmd, int len) {
  return true;
}


bool has_water() {
  return false;
}


bool has_bean() {
  return true;
}

