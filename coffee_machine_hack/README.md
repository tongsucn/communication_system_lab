# Coffee Machine Hack (in development)
    Author: Dominik Chmiel, Sebastian Kruse, Tong Su

![attention](https://upload.wikimedia.org/wikipedia/en/8/89/Construction_Icon_small.png "NOTE")
**The project is still in development**

## Progress:

### **Coffee maker hack** (**100%**)

|Command|Desctiption|Alternative|Comments|
|:-:|:-:|:-:|:-:|
|`AN:01`|Turn ON|`FA:01`||
|`AN:02`|Turn OFF|`FA:02`||
|`AN:03`|Test display|||
|`AN:04`|Test leds (buttons' lighting)|||
|`AN:05`|Test buttons||Can only be cancelled by starting another test mode|
|`FA:03`|Cleaning|||
|`FA:04`|Make product 1|||
|`FA:05`|Make product 2|||
|`FA:06`|Make product 3|||
|`FA:07`|Make product 4|||
|`FA:08`|Make steam (perm.)|||
|`FA:09`|Make steam (portion)|||
|`FA:0B`|Make coffee (powder)|||
|`FA:0F`|Programming mode|||
|`RE:`|Read memory|||
|`RT:`|Read memory line|||

### Coffee maker lower layer API (for Arduino) (60%)

Setup a series of C-APIs for Arduino communication program.

`control, has_water, has_bean`

### **Protocol Buffers for Arduino** (**100%**)

The **nanopb** ([Link](http://koti.kapsi.fi/jpa/nanopb/)) is employed here for the communication between the Arduino and Raspberry PI.

### **Communication between the Arduino and Raspberry PI** (**100%**)

Protocol Buffers work.

### **Raspberry PI communication interface abstraction** (**100%**)

### Web Server (50%)

### Cup detection (0%)

### Android App (0%)

## Reference:

Protobuf: [https://developers.google.com/protocol-buffers](https://developers.google.com/protocol-buffers)
nanopb: [http://koti.kapsi.fi/jpa/nanopb/](http://koti.kapsi.fi/jpa/nanopb/)
