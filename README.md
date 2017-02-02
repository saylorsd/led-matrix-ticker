# LED Matrix Text Ticker

## Enable SPI
Step aken from https://learn.sparkfun.com/tutorials/raspberry-pi-spi-and-i2c-tutorial. Refer to there for more information.

1. Run `sudo raspi-config`.  
2. Use the down arrow to select `Advanced Options`  
3. Arrow down to `SPI`.  
4. Select `ye`s when it asks you to enable SPI,  
5. Also select yes when it asks about automatically loading the kernel module.  
6. Use the right arrow to select the `<Finish>` button.  
7. Select `yes` when it asks to reboot.  

## Pin Layout
| Board Pin | Name | RPi Pin | RPi Function      |
|-----------|------|---------|-------------------|
| 1         | VCC  | 2       | 5V                |
| 2         | GND  | 6       | GND               |
| 3         | DIN  | 19      | GPIO 10 (MOSI)    |
| 4         | CS   | 24      | GPIO 8 (SPI CS0)  |
| 5         | CLK  | 23      | GPIO 11 (SPI CLK) |

## Acknowlegements
I used a lot of code (especially the low-level technical parts) from [tutRPi's multilinemAX7219 repo](https://github.com/tutRPi/multilineMAX7219).  
Which is an "improved and extended version" of [JonA1961's MAX7219array]( https://github.com/JonA1961/MAX7219array).  
