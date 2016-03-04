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

byte tankStatus, dtStatus;

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial.println("Starting coffeehacker");
  delay(5000);
  getASCIIResponse("TY", "Type: ");
  Serial.println("");
}

void loop() {
  tankStatus = 0;
  dtStatus = 0;
  collectInputData();
  Serial.print("STATUS UPDATE:\n");
  checkWaterTank();
  checkDripTray();
  Serial.print("\n");
  //getBitResponse("IC:","IC: ");
  //delay(200);
  //Serial.println("");
}

void collectInputData(){
  for(int x = 0; x < 10; x++) {
    toCoffeeStr("IC:");
    String r = "";
    while(Serial1.available()) {
      delay (intra); d0 = Serial1.read();
      delay (intra); d1 = Serial1.read();
      delay (intra); d2 = Serial1.read();
      delay (intra); d3 = Serial1.read();
      delay (inter);
      r += char(fromCoffeemaker(d0,d1,d2,d3));
    }
    tankStatus += ((getVal(r[6])&0x02)>> 1);
    dtStatus += (getVal(r[6])&0x01);
    delay(100);  
  }  
}

void checkWaterTank(){
  if(tankStatus > 0)   Serial.print("Water Tank: Refill\n");
  else  Serial.print("Water Tank: Ok\n");
}

void checkDripTray(){
  if(dtStatus > 0)  Serial.print("Drip Tray: Ok\n");
  else   Serial.print("Drip Tray: Removed\n");
  
}

int getASCIIResponse(String input, String Note) {
  toCoffeeStr(input);
  String r = Note;

  while(Serial1.available()) {
    delay (intra); d0 = Serial1.read();
    delay (intra); d1 = Serial1.read();
    delay (intra); d2 = Serial1.read();
    delay (intra); d3 = Serial1.read();
    delay (inter);
    r += char(fromCoffeemaker(d0,d1,d2,d3));
  }
    Serial.println(r);
}

int getBitResponse(String input, String Note) {
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
  Serial.print(Note);
  for(int x = 3; x < r.length()-2; x++) {
    Serial.print(byteToBit(getVal(r[x])));Serial.print(" ");
  }
  Serial.println(""); 
}

byte getVal(char c){
  if(c >= '0' && c <= '9') return (byte)(c-'0'); 
  else return (byte)(c-'A'+10);
}

String byteToBit(byte c){
  String r = "";
  r+=(c/8?'1':'0');
  r+=(c%8/4?'1':'0');
  r+=(c%4/2?'1':'0');
  r+=(c%2/1?'1':'0');
  return r;
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
}
