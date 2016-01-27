#ifndef _COFFEE_CTRL_H
#define _COFFEE_CTRL_H


#include <stdint.h>


/*
   Function:      control
   Description:   Control the machine

   Args:
      cmd (const uint8_t *): extended command content
      len (int): command length

   Returns:
      (bool): if tasks finish successfully then return true, else false
*/
bool control(const uint8_t *cmd, int len);

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


#endif _COFFEE_COM_H