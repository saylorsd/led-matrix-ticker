# Import library
from led import LEDMatrixTicker as Ticker
# Import fonts
from fonts import CP437_FONT_ROTATED


# The following imported variables make it easier to feed parameters to the library functions
from led import DIR_L, DIR_R, DIR_U, DIR_D


# Initialise the library and the MAX7219/8x8LED arrays
ticker = Ticker(width=4, font=CP437_FONT_ROTATED, rotated=True)
try:
    ticker.scroll_message("Message", speed=6, repeats=0)

except KeyboardInterrupt:
    ticker.clear_all()
