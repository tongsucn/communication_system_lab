# Coffee Machine Hack Project
    Author: Dominik Chmiel, Sebastian Kruse, Tong Su

## Introduction

This is a coffee machine hacking project. It aims to implement remote controlling of coffee machine. The target machine is Jura IMPRESSA S90, which has a serial at the back of the machine.

## Requirement

### Server

Platform: Raspberry PI

Environment: [Arch Linux for Raspberry PI](https://wiki.archlinux.org/index.php/Raspberry_Pi), Python 3.5+, [Protocol Buffers 3](https://developers.google.com/protocol-buffers/), [CherryPy](http://www.cherrypy.org/)

### Coffee Machine Controller

Platform: Arduino

Environment: nanopb

### Android App

Enviroment: Android 4.4+

## System Architecture

The system contains three main parts: The coffee machine (Jura IMPRESSA S90), the controller (Pandorica) and clients (WebApp or Android App).

![System Architecture]()

### Coffee Machine (Jura IMPRESSA S90)

Currently the only supported coffee machine is the Jura IMPRESSA S90. Its available control commands are shown in Appendix.

### Controller

#### Controller (Arduino)

The Arduino takes charge in controlling the coffee machine directly. It sends commands commands to coffee machine by using serial port. The coffee machine's control protocol is available [here](https://web.archive.org/web/20150403060045/http://protocol-jura.do.am/index/protocol_to_coffeemaker/0-7). The Arduino exchanges messages with Server (Raspberry PI) by using UDP protocol. It connects to the router by using official Ethernet shield and a cable. The exchanged messages is based on Protocol Buffers (Protobuf 3). The Protobuf does not support C (de)serialization. Therefore we hire the 3rd-party plugin called nanopb to make Arduino use the Protobuf. We call this exchange protocol the Backend Communication Protocol. The Arduino code is now well commented, if someone needs the debug information, just uncomment the ```HACK_DEBUG``` flag in ```coffee_utility.h```.

#### Server (Raspberry PI)

The server typically runs on the Raspberry PI (prefer Raspberry PI 2 or higher). It can also deployed on laptop. The PI is connected to router, and its port 8080 is forwarded on router's port 8080 for clients. The Backend Communication Protocol is parsed and handled in Python (Python 3.5 or higher).

A web server is also running on the PI. It's based on CherryPy and provides a Web App for users. Users can access this Web App on their smartphone or PC.

In addition, the server provides the cup detection function, which is based on opencv 3 and a web camera. It will detect if a cup is available on the tray. If not, requests like "making a cup of espresso" cannot be processed.

To setup the server, a python installation with version 3.4 or greater is required. Additionally, the modules cherrypy and bcrypt need to be installed.

For the cup-detection to work, opencv 3.0.0 or greater alongside numpy needs to be installed.

On an Arch-system, the following AUR-Packet can be used: https://aur.archlinux.org/packages/opencv-git/

#### Router

The router is used for connecting the Arduino and the Raspberry PI. Furthermore, it communicates with the clients in LAN or Internet. The router will forward the Raspberry's port 8080 on router's port 8080. So the clients (Web browser and Android App) can access the server (Raspberry PI) with 8080 port and router's address. Such architecture will hide the existence of the Arduino and related communication from internal outside view.

### Clients

#### Web App

A login/register page is provided by the web server on Raspberry PI. After login, users will be able to control the coffee machine to turn it ON/OFF, make coffee etc.

#### Android App

## Appendix

### Jura IMPRESSA S90 Controlling Commands:

|Command|Desctiption|Alternative|Comments
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
|`IC:`|Read input values|||

|IC: (Nibbles)|MSB| | |LSB|
|:-:|:-:|:-:|:-:|:-:|
|5 (MSB|-|-|-|-|
|4|-|-|-|-|
|3|-|-|-|-|
|2|-|-|Water Tank Status: <br /> 0: Ok <br/> 1: Refill|Drip Tray Status: <br /> 0: Removed <br /> 1: tbd <br /> Alternating: Inserted|
|1|-|-|-|-|
|0 (LSB)|-|-|-|-|

## Reference:

Arch Linux: [https://wiki.archlinux.org/index.php/Raspberry_Pi](https://wiki.archlinux.org/index.php/Raspberry_Pi)

CherryPy: [http://www.cherrypy.org/](http://www.cherrypy.org/)

Protobuf: [https://developers.google.com/protocol-buffers](https://developers.google.com/protocol-buffers)

nanopb: [http://koti.kapsi.fi/jpa/nanopb/](http://koti.kapsi.fi/jpa/nanopb/)
