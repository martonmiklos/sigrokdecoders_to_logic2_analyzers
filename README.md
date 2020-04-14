### Convert Sigrok Decoders to Logic 2.x Analyzers

## What the heck?

Starting from Saleae Logic 2.2.6 it supports so called High level analyzers for SPI, I2C, UART written in python.

Sigrok has a plenty of analyzers written also in python.

It all adds up: let's write a wrapper to joy the sigrok analyzers withint the Saleae Logic.

## Usage
The plan is to create a 'fake' sigrokdecode.py which will do the Logic input frame -> sigrok frame -> sigrok decoder -> sigrok decoded frame -> Logic frame conversion.
(And the settings/annotiation conversion in the similar way.)

Other than this a wrapper class will be generated for each sigrok analyzer which will be compatible with the Logic analyzer format.

The generation of these classes is automated by the convert.py script:

It will select the supported (I2C/SPI/UART based) analyzers from the libsigrokdecode submodule.

## Achtung, warning, pozor!
The code is pretty rough it did not even been tested with Logic yet.

Stay tuned!
