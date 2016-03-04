#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#include "Arduino.h"

#include "Ethernet.h"
#include "EthernetUdp.h"

#include <coffee.pb.h>
#include <pb_encode.h>
#include <pb_decode.h>

#include "coffee_com.h"
#include "coffee_ctrl.h"
#include "coffee_utility.h"


// General buffer size
#define GEN_BUF_SIZE    64

// General buffer for getting bytes field content and parsing request
struct GeneralBuffer {
  uint8_t buf[GEN_BUF_SIZE];
};


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

    log_debug("Protobuf cannot decode raw data.");
  }
  else {
    log_debug("Protocol decoding succeed!");

    if (rawCmd.type == CoffeeCommand_CommandType_OPERATION) {
      parsed.type = TYP_REQ_OPER;
      parsed.len = BIN_CODE_LEN;

      String debugInfo = "Request type: OPERATION, content: ";
      String debugInfoContent = (char *)decodeBuf.buf;
      log_debug(debugInfo + debugInfoContent);

      memcpy(parsed.content, decodeBuf.buf, BIN_CODE_LEN);
    }
    else if (rawCmd.type == CoffeeCommand_CommandType_QUERY) {
      log_debug("Request type: QUERY");
      parsed.type = TYP_REQ_QSTS;
    }
    else {
      log_debug("Request type: UNKNOWN");
      parsed.type = TYP_REQ_UNKN;
    }
  }

  return parsed;
}


bool cmd_decode_cb(pb_istream_t *stream, const pb_field_t *field, void **arg) {
  GeneralBuffer *bufPtr = (GeneralBuffer *)(*arg);

  pb_read(stream, bufPtr->buf, stream->bytes_left);

  return true;
}


int encode_resp(const ParsedReq *parsed, bool result, uint8_t *buf, int len) {
  // Buffer for getting command content in callback function
  GeneralBuffer encodeBuf;
  // Structure for writing response content in callback function
  Response rawResp;

  // Setting type field
  rawResp.has_type = true;

  // Setting description field
  rawResp.description.funcs.encode = resp_encode_cb;
  rawResp.description.arg = &encodeBuf;


  if (parsed->type == TYP_REQ_OPER) {
    // Prepare for response of performing operations
    if (result) {
      rawResp.type = Response_ResponseType_OK;
      strncpy((char *)encodeBuf.buf, "Operation SUCCEED", GEN_BUF_SIZE);
    }
    else {
      rawResp.type = Response_ResponseType_OPERATION_ERR;
      strncpy((char *)encodeBuf.buf, "Operation FAILED", GEN_BUF_SIZE);
      rawResp.has_results = true;
    }
  }
  else if (parsed->type == TYP_REQ_QSTS) {
    // Prepare for response of querying bean available
    rawResp.type = Response_ResponseType_RESULT;
    strncpy((char *)encodeBuf.buf, "", GEN_BUF_SIZE);
    rawResp.has_results = true;
  }
  else {
    // Prepare for response of unknown format error
    rawResp.type = Response_ResponseType_FORMAT_ERR;
    strncpy((char *)encodeBuf.buf, "Request format UNKNOWN", GEN_BUF_SIZE);
  }

  // Setting results field
  if (rawResp.has_results) {
    // Setting power status result
    rawResp.results.has_POWER = true;
    rawResp.results.POWER = STS_POWER & parsed->content[0];

    rawResp.results.has_WATER = true;
    rawResp.results.WATER = STS_WATER & parsed->content[0];

    rawResp.results.has_BEANS = true;
    rawResp.results.BEANS = STS_BEANS & parsed->content[0];

    rawResp.results.has_TRAY = true;
    rawResp.results.TRAY = STS_TRAY & parsed->content[0];
  }

  // Relate a pb_ostream_t with a buffer
  pb_ostream_t ostreamResp = pb_ostream_from_buffer(buf, (size_t)len);
  bool encodeStatus = pb_encode(&ostreamResp, Response_fields, &rawResp);

  if (is_debug()) {
    if (encodeStatus)
      log_debug("Encode succeed!");
    else
      log_debug("Encode failed!");

    // Assemble debug information
    String respType, respLen;
    if (rawResp.type == Response_ResponseType_OK)
      respType = "OK";
    else if (rawResp.type == Response_ResponseType_RESULT)
      respType = "RESULT";
    else if (rawResp.type == Response_ResponseType_OPERATION_ERR)
      respType = "OPERATION_ERR";
    else
      respType = "FORMAT_ERR";

    char digitBuf[8];
    respLen = itoa(ostreamResp.bytes_written, digitBuf, 10);

    String respTypeHead, respLenHead;
    respTypeHead = "Response type: ";
    respLenHead = ", encoded bytes number: ";

    log_debug(respTypeHead + respType + respLenHead + respLen);
  }

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
