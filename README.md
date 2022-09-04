# pi-power-optimization
This is a python program for regulating the power usage of the raspberry pi platform
## Running program
Please run it as root e.g "sudo python3 main.py"

The objective of this program was to preserve energy used by a raspberry pi 4 model B in a wireless sensor network (WSN).
The pi board is a great and vasatile tool but one of its greatest weakness is that, it has no in-built mechinsm for regulating power usage like putting the board to sleep in less busy hours. This program helps to control the different power hungry peripherals of the board using shell scripting embedded in python code. This makes direct calls to the raspbian operating system.

The program does not use any third-party python packages. It solely rely on the multiprocessing package shipped with Python. The Linux shell script calls are invoked using the multiprocessing package.

The peripherals in mind when writing this scripts were the hdmi ports, usb ports, onboard leds, wifi, bluetooth, ram clocking speed, gpu clocking speed and cpu clocking speed. The user can enable or disable any of these features as desired.

## Disclaimer
When disabling this features please make sure you have additional means of controlling the board. I prefer using the ssh support to remotely control the board as you experiment. Also note the note all features may not work for your board, as the boards have some difference in some way.
If you have any suggessions, I highly welcome them to improve this program.
