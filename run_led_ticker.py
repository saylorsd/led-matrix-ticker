#! /usr/bin/python
import sys
import argparse

from led import LEDMatrixTicker as Ticker
from fonts import CP437_FONT_ROTATED



parser = argparse.ArgumentParser(description='Run scrolling LED matrix ticker')

parser.add_argument('-r', '--redis', action='store_true', dest='use_redis', default=False, help='whether the message will come from redis or not')
parser.add_argument('-s', '--speed', type=int, nargs='?', dest='speed', default=5, help='speed at which the ticker will scroll (0-10)' )
parser.add_argument('-w', '--width', type=int, nargs='?',  dest='width', default=8, help='width of ticker (number of 8x8 matrices)')

results = parser.parse_args();

use_redis = results.use_redis
speed = results.speed
width = results.width

print('Starting LED Ticker')
print('Speed: {}'.format(speed))
print('Width: {}'.format(width))
print('Source: {}'.format('redis' if use_redis else 'hardcoded'))

# Initialise the library and the MAX7219/8x8LED arrays
ticker = Ticker(width=width, font=CP437_FONT_ROTATED, rotated=True)

try:
    if use_redis:
        ticker.scroll_redis_key(speed=speed, repeats=0)
    else:
        ticker.scroll_message('Message', speed=speed, repeats=0)

except KeyboardInterrupt:
    ticker.clear_all()