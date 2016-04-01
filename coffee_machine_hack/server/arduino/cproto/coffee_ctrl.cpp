#include <string.h>
#include <stdint.h>

#include "Arduino.h"

#include "coffee_ctrl.h"
#include "coffee_utility.h"


#define CMD_BUF_LEN     28      // Command buffer for machine code
#define MEM_PWR_IDX     4       // Index for getting power status
#define MEM_RSC_IDX     6       // Index for getting water and tray status
#define STS_CHK_TIME    3       // Times for checking status (larger -> stabler)
                                // But 3 should be enough in most cases

#define POWER_AND_FLG   0x02    // And flag for getting power status
#define WATER_AND_FLG   0x02    // And flag for getting water status
#define WATER_OFFSET    1       // Offset for getting water status
#define TRAY_AND_FLG    0X01    // And flag for getting tray status
#define TRAY_OFFSET     0       // Offset for getting tray status

// Line end for the machine code
uint8_t lineEnd[] = {0xDF, 0xFF, 0xDB, 0xDB, 0xFB, 0xFB, 0xDB, 0xDB};
// Delay value
uint8_t intra = 1, inter = 7, afterCmd = 100;
// Status table
uint8_t statusTable = 0;

// Power status, for stabler power status
bool powerStatus;


String control(const uint8_t *cmd, int len) {
  String result = "";
  uint8_t byteSlice[4];

  String cmdContentHead = "Calling command: ";
  String cmdContent = (char *)cmd;
  log_debug(cmdContentHead + cmdContent);

  // Send command to coffee maker
  to_coffee_maker(cmd, len);
  delay(afterCmd);

  // Decode machine code
  while (Serial1.available()) {
    delay(intra); byteSlice[0] = Serial1.read();
    delay(intra); byteSlice[1] = Serial1.read();
    delay(intra); byteSlice[2] = Serial1.read();
    delay(intra); byteSlice[3] = Serial1.read();
    delay(inter);

    result += decode_machine(byteSlice);
  }

  if (is_debug()) {
    char lenBuf[8];

    String respLenHead = "Response length: ";
    String respLen = itoa(result.length(), lenBuf, 10);
    log_debug(respLenHead + respLen);

    String respContentHead = "Response content: ";
    log_debug(cmdContentHead + result);
  }

  return result.substring(0, result.length() - 2);
}


bool is_on() {
  return statusTable & STS_POWER;
}


bool has_water() {
  return statusTable & STS_WATER;
}


bool has_bean() {
  return statusTable & STS_BEANS;
}


bool has_tray() {
  return statusTable & STS_TRAY;
}

uint8_t get_status_table() {
  return statusTable;
}


void to_coffee_maker(const uint8_t *input, int len) {
  uint8_t cmdBuf[CMD_BUF_LEN];
  int cmdLen = len * 4 + sizeof(lineEnd);

  // Encode into machine code format
  encode_machine(cmdBuf, cmdLen, input, len);

  // Send command to machine
  for (int i = 0; i < cmdLen; i += 4) {
    delay(intra); Serial1.write(cmdBuf[i]);
    delay(intra); Serial1.write(cmdBuf[i + 1]);
    delay(intra); Serial1.write(cmdBuf[i + 2]);
    delay(intra); Serial1.write(cmdBuf[i + 3]);
    delay(inter); delay(inter);
  }
}


void encode_machine(uint8_t *buf, int bufLen,
                    const uint8_t *input, int inputLen) {
  // Initialize command buffer
  memset(buf, 255, bufLen);

  // Encode command
  for (int i = 0; i < inputLen; i++) {
    for (int j = 0; j < 4; j++) {
      bitWrite(buf[4 * i + j], 2, bitRead(input[i], 2 * j));
      bitWrite(buf[4 * i + j], 5, bitRead(input[i], 2 * j + 1));
    }
  }

  // Encode command line end
  memcpy(&buf[inputLen * 4], lineEnd, 8);
}


char decode_machine(uint8_t *raw) {
  char decoded;
  bitWrite(decoded, 0, bitRead(raw[0], 2));
  bitWrite(decoded, 1, bitRead(raw[0], 5));
  bitWrite(decoded, 2, bitRead(raw[1], 2));
  bitWrite(decoded, 3, bitRead(raw[1], 5));
  bitWrite(decoded, 4, bitRead(raw[2], 2));
  bitWrite(decoded, 5, bitRead(raw[2], 5));
  bitWrite(decoded, 6, bitRead(raw[3], 2));
  bitWrite(decoded, 7, bitRead(raw[3], 5));
  return decoded;
}


void update_status() {
  log_debug("Updating machine status.");
  int powerAcc = 0, waterAcc = 0, trayAcc = 0;
  String rawResult;
  for (int i = 0; i < STS_CHK_TIME; i++) {
    rawResult = control((uint8_t *)"IC:", 3);
    if (rawResult.length() == 0)
      continue;

    // Getting power status
    char power = rawResult[MEM_PWR_IDX];
    powerAcc += !(power & POWER_AND_FLG);

    // Getting water and tray status
    char resource = rawResult[MEM_RSC_IDX];
    resource = (resource >= '0' && resource <= '9')
               ? resource - '0'
               : resource - 'A' + 10;
    waterAcc += ((resource & WATER_AND_FLG) >> WATER_OFFSET);
    trayAcc += ((resource & TRAY_AND_FLG) >> TRAY_OFFSET);
    delay(100);
  }

  // Updating status table
  // Power
  // Following comment is the previous checking method, not stable
  // statusTable = powerAcc > 0
  statusTable = powerStatus
                ? statusTable | STS_POWER
                : statusTable & ~STS_POWER;

  // Water
  statusTable = !(waterAcc > 0)
                ? statusTable | STS_WATER
                : statusTable & ~STS_WATER;

  // Bean (always 1 for now)
  statusTable |= STS_BEANS;

  // Tray
  statusTable = trayAcc > 0
                ? statusTable | STS_TRAY
                : statusTable & ~STS_TRAY;

  if (is_debug()) {
    Serial.print("[DEBUG] Status table: ");
    Serial.println(statusTable, BIN);

    Serial.print("[DEBUG] Power status: ");
    if (statusTable & STS_POWER)
      Serial.println("OK");
    else
      Serial.println("N.A.");

    Serial.print("[DEBUG] Water status: ");
    if (statusTable & STS_WATER)
      Serial.println("OK");
    else
      Serial.println("N.A.");

    Serial.print("[DEBUG] Tray status: ");
    if (statusTable & STS_TRAY)
      Serial.println("OK");
    else
      Serial.println("N.A.");
  }
}

void set_power(bool status) {
  powerStatus = status;
}
