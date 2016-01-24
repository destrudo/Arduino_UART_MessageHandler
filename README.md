# Arduino_UART_MessageHandler
Simple control for Arduino pins and NeoPixels via UART.

# Current State
I don't consider it production worthy, but it works.  It needs more testing.

Expect debugging messages to be turned on and off willy nilly between commits.

### Software
Software is not technically required if you want to manually generate messages and send them on your teletype.  However I made something just for generating them.  You can acquire it at https://github.com/destrudo/py_aumh

### Firmware Notes
1. UART_MessageHandler
  - Possible Changes:
    * Possibility for actual C++ abstractness in adding new endpoint message handlers. *This would change a lot of stuff in terms of code, but it would still behave the same way.*
    * Adding in control methods for the UART_MH class for doing things such as manually setting limits.
    * A pin-in-use array that classes will respond to.
  - State:
    * Not going to change very much in the near future, pretty well tested where it stands currently.

2. UART_Neopixel
  - Possible Changes:
    * May split off each of the classes and structures into separate files.
    * A pin-in-use array that classes will respond to.
  - State:
    * It's tested and seems to work as expected.

3. UART_Digital
  - Possible Changes:
    * We might want to designate a pin to controlling an analog switch array or something (Which could be undone via management commands post-boot) so that as little effort as possible goes into using this in applications that can't start in the way that the bootloader will start. (A custom Arduino bootloader would fix this too.)
  - State:
    * Relatively well tested on a Mega 2560 from both firmware and controller.

# Protocol
The message protocol is a simple 12 byte command header for which the second to last bit is the sum of the preceeding 10 bytes.

####### If there's some nice lightweight open protocol with version information that works, which I overlooked... swing me a line.  I *really* would prefer to conform to an existing standard.