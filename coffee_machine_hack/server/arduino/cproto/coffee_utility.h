#ifndef _COFFEE_UTILITY_H
#define _COFFEE_UTILITY_H


#include <stdint.h>

#include <Arduino.h>

// Debug flag for printing debug information
#define HACK_DEBUG


/* ************************************************************************** */
/*                          Declaration of functions                          */
/* ************************************************************************** */

/*
   Function:      log_debug
   Description:   Print debug information

   Args:
      info (const String &): debug information
*/
void log_debug(const String &info);

/*
   Function:      is_debug
   Description:   Return true if the debug mode is on

   Returns:
      (bool): return true if the debug mode is on
*/
bool is_debug();

#endif