#ifndef _COFFEE_COM_H
#define _COFFEE_COM_H


#include <stdint.h>

#include "Ethernet.h"
#include "EthernetUdp.h"

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
#define RESP_MAX_LEN    64    // Response maximum length

// Parsed request structure
struct ParsedReq {
  int type;
  int len;
  uint8_t content[BIN_CODE_LEN];
};


/* ************************************************************************** */
/*                          Declaration of functions                          */
/* ************************************************************************** */

/*
   Function:      setupNetwork
   Description:   Initializing network configuration

   Args:
      udp (EthernetUdp *): Arduino UDP instance
      mac (byte []): MAC address of the Arduino
      ip (const IPAddress *): local IP address
      localPort (uint32_t): local port
 */
void setupNetwork(EthernetUDP *udp, byte mac[], const IPAddress *ip,
                  uint32_t localPort);

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
   Function:      encode_resp
   Description:   Encode response according to operation result

   Args:
      parsed (const ParsedReq *): pointer to parsed request
      result (bool): operation result, true for succeed
      buf (uint8_t *): response buffer
      len (int): reponse buffer's size

   Returns:
      (int): response length
*/
int encode_resp(const ParsedReq * parsed, bool result, uint8_t *buf,
                int len);

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


#endif _COFFEE_COM_H