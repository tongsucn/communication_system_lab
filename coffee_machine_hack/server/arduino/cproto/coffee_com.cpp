#include <string.h>
#include <stdint.h>

#include "Arduino.h"

#include "Ethernet.h"
#include "EthernetUdp.h"

#include <coffee.pb.h>
#include <pb_encode.h>
#include <pb_decode.h>

#include "coffee_com.h"


// General buffer size
#define GEN_BUF_SIZE    64

// General buffer for getting bytes field content and parsing request
struct GeneralBuffer {
  uint8_t buf[GEN_BUF_SIZE];
};

// Line end for the machine code
uint8_t lineEnd[] = {0xDB, 0xDB, 0xFF, 0xDF, 0xDB, 0xDB, 0xFB, 0xFB};


void setupNetwork(EthernetUDP *udp, byte mac[], const IPAddress *ip,
                  uint32_t localPort) {
  // Start the Ethernet connection
  Ethernet.begin(mac, *ip);
  // Start UDP
  udp->begin(localPort);
}


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
      if (decodeBuf.buf[0] == 'W') {
        parsed.type = TYP_REQ_QWT;
      }
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


int encode_resp(const ParsedReq *parsed, bool result, uint8_t *buf,
                int len) {
  // Buffer for getting command content in callback function
  GeneralBuffer encodeBuf;
  // Structure for writing response content in callback function
  Response rawResp;
  rawResp.has_type = true;
  rawResp.description.funcs.encode = resp_encode_cb;
  rawResp.description.arg = &encodeBuf;

  // Relate a pb_ostream_t with a buffer
  pb_ostream_t ostreamResp = pb_ostream_from_buffer(buf, (size_t)len);

  if (parsed->type == TYP_REQ_OPER) {
    // Prepare for response of performing operations
    if (result) {
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
  else if (parsed->type == TYP_REQ_QWT) {
    // Prepare for response of querying water tank
    if (result) {
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
  else if (parsed->type == TYP_REQ_QBA) {
    // Prepare for response of querying bean available
    if (result) {
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
