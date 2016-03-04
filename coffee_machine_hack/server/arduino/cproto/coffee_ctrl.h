#ifndef _COFFEE_CTRL_H
#define _COFFEE_CTRL_H


#include <stdint.h>


/* Machine status table, every bit stands for a status:
   bit 0:   reserve
   bit 1:   power status
   bit 2:   water status
   bit 3:   bean status
   bit 4:   tray status
   bit 5-7: reserve for future using
*/
#define STS_POWER 0x40
#define STS_WATER 0x20
#define STS_BEANS 0x10
#define STS_TRAY  0x08


/* ************************************************************************** */
/*                          Declaration of functions                          */
/* ************************************************************************** */

/*
   Function:      control
   Description:   Control the machine

   Args:
      cmd (const uint8_t *): extended command content
      len (int): command length

   Returns:
      (String): a human-readable return code from machine
*/
String control(const uint8_t *cmd, int len);

/*
   Function:      is_on
   Description:   Checking if the machine is turned on

   Returns:
      (bool): if the machine is turned on then return true, otherwise false
*/
bool is_on();

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

/*
   Function:      has_tray
   Description:   Checking the tray

   Returns:
      (bool): if tray is available then return true, otherwise false
*/
bool has_tray();

/*
   Function:      get_status_table
   Description:   Returning status table of the coffee machine

   Returns:
      (uint8_t): the status table:
         bit 0:   power status
         bit 1:   water status
         bit 2:   bean status
         bit 3:   tray status
         bit 4-7: reserve for future using
*/
uint8_t get_status_table();

/*
   Function:      to_coffee_maker
   Description:   Sending commands to coffee maker

   Args:
      input (uint8_t *): extended command content
      len (int): command length
*/
void to_coffee_maker(const uint8_t *input, int len);

/*
   Function:      encode_machine
   Description:   Encoding raw machine code

   Args:
      buf (uint8_t *): machine code buffer
      bufLen (int): machien code buffer length
      input (const uint8_t *): input command, to be encoded
      inputLen (int): input command length
*/
void encode_machine(uint8_t *buf, int bufLen,
                    const uint8_t *input, int inputLen);

/*
   Function:      decode_machine
   Description:   Decoding raw machine code

   Args:
      raw (uint8_t *): raw byte slice in machine code format, array length 4

   Returns:
      (char): decoded character
*/
char decode_machine(uint8_t *raw);

/*
   Function:      update_status
   Description:   Updating machien status, water/tray availability,
                  need to be called in every main loop of Arduino.
                  +new (10.Feb.2016):
                     Power status check.
*/
void update_status();


#endif _COFFEE_COM_H