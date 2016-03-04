#include "Arduino.h"

#include "coffee_utility.h"


// Information head for debug.
String debugHeadStyle = "[DEBUG] ";


void log_debug(const String &info) {
#ifdef HACK_DEBUG
  Serial.println(debugHeadStyle + info);
#endif
}


bool is_debug() {
#ifdef HACK_DEBUG
  return true;
#else
  return false;
#endif
}