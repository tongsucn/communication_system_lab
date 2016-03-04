// #include <SoftwareSerial.h>
// SoftwareSerial mySerial(10, 11); // RX TX

#ifndef bitRead
#define bitRead(value, bit) (((value) >> (bit)) & 0x01)
#define bitSet(value, bit) ((value) |= (1UL << (bit)))
#define bitClear(value, bit) ((value) &= ~(1UL << (bit)))
#define bitWrite(value, bit, bitvalue) (bitvalue ? bitSet(value, bit) : bitClear(value, bit))
#endif

byte z0, z1, z2, z3;
byte x0, x1, x2, x3, x4;
byte d0, d1, d2, d3;
byte intra = 1, inter = 7;
String hexval;

String EEPROMDump = "";

// TODO: melkkoffie, twee koffie, twee espressi
// TODO: make this an array and iterate all functions over it
int t_koffie, t_ristretto, t_cappuccino, t_espresso, t_latte_macchiato, t_macchiato;
int o_koffie, o_ristretto, o_cappuccino, o_espresso, o_latte_macchiato, o_macchiato;

//FA:04: 1 coffee  extra
//FA:05: 2 coffee [extra]
//FA:06: 1 espresso
//FA:07: 2 espresso
//FA:08: Dampfbezug
//FA:09: Dampf: portion
//FA:0B: Pulver
//FA:0F: Filter Ja? - Programmiermodus?

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial.println("Starting coffeehacker");
  getInput("TY");
  delay(5000);
  getInput("IC:");
  //getInput("AN:01");
  //delay(1000);
  //getInput("FA:0F");
  //delay(2000);

  //Serial.println(getCounter(179));
  //Serial.println(getCounter(180));
  
  //getInput("FA:05");
  //getInput("FA:06");
  //dumpEEProm();
  //Serial.println(EEPROMDump);
  //getInput("FA:03");
}

int getInput(String input) {
  toCoffeeStr(input);
  String r = "";

  while(Serial1.available()) {
    delay (intra); d0 = Serial1.read();
    delay (intra); d1 = Serial1.read();
    delay (intra); d2 = Serial1.read();
    delay (intra); d3 = Serial1.read();
    delay (inter);
    r += char(fromCoffeemaker(d0,d1,d2,d3));
  }
    Serial.print(r);
  /*for(int x = 0; x < r.length(); x++) {
    Serial.print(String(r[x], HEX));
  }*/
  //Serial.println("");
}

int getCounter(uint16_t offset, int tries = 0)
{
  hexval = String(offset, HEX);
  while(hexval.length() < 2) hexval = "0" + hexval;

  /*toCoffeemaker('R'); delay(inter);
  toCoffeemaker('E'); delay(inter);
  toCoffeemaker(':'); delay(inter);
  toCoffeemaker('0'); delay(inter);
  toCoffeemaker(hexval[0]); delay(inter);
  toCoffeemaker(hexval[1]); delay(inter);
  toCoffeemaker(hexval[2]); delay(inter);
  toCoffeemaker(0x0D); delay(inter);
  toCoffeemaker(0x0A); delay(100);*/

  //Serial.println(hexval);

  toCoffeeStr("RE:" + hexval + "\r\n");

  String r = "";

  while(Serial1.available()) {
    delay (intra); d0 = Serial1.read();
    delay (intra); d1 = Serial1.read();
    delay (intra); d2 = Serial1.read();
    delay (intra); d3 = Serial1.read();
    delay (inter);
    r += char(fromCoffeemaker(d0,d1,d2,d3));
  }
  for(int x = 0; x < r.length(); x++) {
    Serial.print(String(r[x], HEX));
  }

  if (r.length() == 9) {
    String hex = r.substring(3,7);
    int number = (int)strtol(hex.c_str(), NULL, 16);
    return number;
  } else {
    if (tries >= 4) {
      Serial.println("Retries didn't work");
      return -1;
    }
    return getCounter(offset, tries + 1);
    return -1;
  }
}

void dumpEEProm() {
  #define start 0
  #define len 1024
  for(uint16_t x = start; x <= start + len; x += 1) {
    Serial.print("[" + String(x) + "] ");
    word res = getCounter(x);
  Serial.println("");
    if (res <= 0xFFF) {
      EEPROMDump += "0";
    }
    if (res <= 0xFF) {
      EEPROMDump += "0";
    }
    if (res <= 0xF) {
      EEPROMDump += "0";
    }
    EEPROMDump += String(res, HEX);
    EEPROMDump += " ";
    if ((x+1) % 16 == 0) {
      //Serial.println(String(x) + " / 255");
      EEPROMDump += "\r\n";
    }
  }
}

void loop() {
  while(Serial1.available()) {
    delay (intra); d0 = Serial1.read();
    delay (intra); d1 = Serial1.read();
    delay (intra); d2 = Serial1.read();
    delay (intra); d3 = Serial1.read();
    delay (inter);
    char fC = fromCoffeemaker(d0,d1,d2,d3);
    //Serial.print(String(fC, HEX) + " ");
    //Serial.println(char(fC));
  }
  delay(1000);
  getInput("IC:01b");
  return;
  o_koffie = t_koffie;
  o_ristretto = t_ristretto;
  o_cappuccino = t_cappuccino;
  o_espresso = t_espresso;
  o_latte_macchiato = t_latte_macchiato;
  o_macchiato = t_macchiato;

  Serial.println("------ reading values");
  t_koffie = getCounter(0x282);
  t_ristretto = getCounter(0x281);
  t_cappuccino = getCounter(0x284);
  t_espresso = getCounter(0x280);
  t_latte_macchiato = getCounter(0x285);
  t_macchiato = getCounter(0x286);

  Serial.print("koffie:.........."); Serial.println(t_koffie);
  Serial.print("cappuccino:......"); Serial.println(t_cappuccino);
  Serial.print("espresso:........"); Serial.println(t_espresso);
  Serial.print("ristretto:......."); Serial.println(t_ristretto);
  Serial.print("latte macchiato:."); Serial.println(t_latte_macchiato);
  Serial.print("macchiato:......."); Serial.println(t_macchiato);
  
  /*Serial.println("On.");
  toCoffeStr("AN:01");
  delay(5 * 1000);
  Serial.println("Off.");
  toCoffeStr("AN:02");
  delay(10 * 1000);
  delay(10 * 1000);
  delay(10 * 1000);
  delay(10 * 1000);*/
}

void toCoffeeStr(String z) {
  //Serial.println(z);
  int x = 0;
  for (x = 0; x < z.length(); x++) {
    byte bt = z[x];
    toCoffeemaker(bt);
    delay(inter);
  }
  toCoffeemaker(0x0D); delay(inter);
  toCoffeemaker(0x0A); delay(100);
}

byte fromCoffeemaker(byte x0, byte x1, byte x2, byte x3) {
  bitWrite(x4, 0, bitRead(x0,2));
  bitWrite(x4, 1, bitRead(x0,5));
  bitWrite(x4, 2, bitRead(x1,2));
  bitWrite(x4, 3, bitRead(x1,5));
  bitWrite(x4, 4, bitRead(x2,2));
  bitWrite(x4, 5, bitRead(x2,5));
  bitWrite(x4, 6, bitRead(x3,2));
  bitWrite(x4, 7, bitRead(x3,5));
  return x4;
}

byte toCoffeemaker(byte z) {
  z0 = 255;
  z1 = 255;
  z2 = 255;
  z3 = 255;

  bitWrite(z0, 2, bitRead(z,0));
  bitWrite(z0, 5, bitRead(z,1));
  bitWrite(z1, 2, bitRead(z,2));
  bitWrite(z1, 5, bitRead(z,3));
  bitWrite(z2, 2, bitRead(z,4));
  bitWrite(z2, 5, bitRead(z,5));
  bitWrite(z3, 2, bitRead(z,6));
  bitWrite(z3, 5, bitRead(z,7));

  delay(intra); Serial1.write(z0);
  delay(intra); Serial1.write(z1);
  delay(intra); Serial1.write(z2);
  delay(intra); Serial1.write(z3);
  delay(inter);
  /*Serial.print(String(z0, HEX) + " ");
  Serial.print(String(z1, HEX) + " ");
  Serial.print(String(z2, HEX) + " ");
  Serial.println(String(z3, HEX));*/
}

