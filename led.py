import spidev
import time
from random import randrange

from fonts import CP437_FONT, SINCLAIRS_FONT, LCD_FONT, TINY_FONT, \
    CP437_FONT_ROTATED, SINCLAIRS_FONT_ROTATED, LCD_FONT_ROTATED, TINY_FONT_ROTATED

# Optional: It is also possible to change the default font for all the library functions:
DEFAULT_FONT = CP437_FONT_ROTATED  # Note: some fonts only contain characters in chr(32)-chr(126) range
ROTATED = True  # set to true if using rotated fonts

# Registers in the MAX7219 matrix controller (see datasheet)
MAX7219_REG_NOOP = 0x0
MAX7219_REG_DIGIT0 = 0x1
MAX7219_REG_DIGIT1 = 0x2
MAX7219_REG_DIGIT2 = 0x3
MAX7219_REG_DIGIT3 = 0x4
MAX7219_REG_DIGIT4 = 0x5
MAX7219_REG_DIGIT5 = 0x6
MAX7219_REG_DIGIT6 = 0x7
MAX7219_REG_DIGIT7 = 0x8
MAX7219_REG_DECODEMODE = 0x9
MAX7219_REG_INTENSITY = 0xA
MAX7219_REG_SCANLIMIT = 0xB
MAX7219_REG_SHUTDOWN = 0xC
MAX7219_REG_DISPLAYTEST = 0xF

# Scroll & wipe directions, for use as arguments to various library functions
# For ease of use, import the following constants into the main script
DIR_U = 1  # Up
DIR_R = 2  # Right
DIR_D = 4  # Down
DIR_L = 8  # Left
DIR_RU = 3  # Right & up diagonal scrolling for gfx_scroll() function only
DIR_RD = 6  # Right & down diagonal scrolling for gfx_scroll() function only
DIR_LU = 9  # Left & up diagonal scrolling for gfx_scroll() function only
DIR_LD = 12  # Left & down diagonal scrolling for gfx_scroll() function only

NO_OP = [0, 0]  # 'No operation' tuple: 0x00 sent to register MAX_7219_NOOP


def rotate(direction):
    if direction == DIR_L:
        return DIR_U
    elif direction == DIR_U:
        return DIR_L
    elif direction == DIR_R:
        return DIR_D
    elif direction == DIR_D:
        return DIR_R


class LEDMatrixTicker(object):
    def __init__(self, width=1, brightness=1, font=DEFAULT_FONT, rotated=False):
        """
        :param width: number of 8x8 matrices in line
        :param brightness: brightness of leds (0-15)
        :param font: font to use as default
        :param rotated: true if
        """
        self.width = width
        self.brightness = brightness
        self.font = font
        self.rotated = rotated
        self.matrices = range(width)

        # Open SPI bus#0 using CS0 (CE0)
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

        self.set_brightness(brightness)

    def send_reg_byte(self, register, data):
        """
        Send one byte of data to one register via SPI port, then raise CS to latch
        Note that subsequent sends will cycle this tuple through to successive MAX7219 chips
        :param register: register in which to rwrite data
        :param data: data writtent to register
        """

        self.spi.xfer([register, data])

    def send_bytes(self, datalist):
        """
        Send sequence of bytes (should be [register,data] tuples) via SPI port, then raise CS
        Included for ease of remembering the syntax rather than the native spidev command, but also to avoid reassigning to 'datalist' argument
        """
        self.spi.xfer2(datalist[:])

    def send_matrix_reg_byte(self, matrix, register, data):
        # Send one byte of data to one register in just one MAX7219 without affecting others
        if matrix in self.matrices:
            padded_data = NO_OP * (self.width - 1 - matrix) + [register, data] + NO_OP * matrix
            self.send_bytes(padded_data)

    def send_all_reg_byte(self, register, data):
        """
        Send the same byte of data to the same register in all of the MAX7219 chips

        :param register:  register to which byte is sent
        :param data: data sent to registers
        """
        self.send_bytes([register, data] * self.width)

    def clear(self, matrix_list):
        """
        Clear one or more specified MAX7219 matrices (argument(s) to be specified as a list even if just one)

        :param matrix_list: list of matrices to clear
        """

        for matrix in matrix_list:
            if matrix in self.matrices:
                for col in range(8):
                    self.send_matrix_reg_byte(matrix, col + 1, 0)

    def clear_all(self):
        """
        Clear all of the connected MAX7219 matrices
        """
        for col in range(8):
            self.send_all_reg_byte(col + 1, 0)

    def set_brightness(self, intensity):
        """
        Set a specified brightness level on all of the connected MAX7219 matrices

        :param intensity: how bright from 0(dimmest) to 15(brightest)
        :param num_matrices: the number of matrices
        :return:
        """

        intensity = int(max(0, min(15, intensity)))
        self.send_bytes([MAX7219_REG_INTENSITY, intensity] * self.width)

    def send_matrix_letter(self, matrix, char, font=None):
        """
        Send one character from the specified font to a specified MAX7219 matrix

        :param matrix: index of targeted matrix
        :param char: the character to write in matrix
        :param font: font in which to display char
        """
        if not font:
            font = self.font

        if matrix in self.matrices:
            for col in range(8):
                self.send_matrix_reg_byte(matrix, col + 1, font[ord(char)][col])

    def send_matrix_shifted_letter(self, matrix, curr_char, next_char, progress, direction=DIR_L,
                                   old_font=None, new_font=None, rotated=ROTATED):
        """
        Send to one MAX7219 matrix a combination of two specified characters, representing a partially-scrolled position

        :param matrix: targeted matrix
        :param curr_char: old character
        :param next_char:  new character
        :param progress: how many pixels the characters are shifted: 0(all old) - 7(one step from all new)
        :param direction: direction in which new char shifts in
        :param font: font in which to display chars
        """
        if not old_font:
            old_font = self.font
        if not new_font:
            new_font = self.font

        curr_char = old_font[ord(curr_char)]
        next_char = new_font[ord(next_char)]
        show_char = [0, 0, 0, 0, 0, 0, 0, 0]
        progress = progress % 8

        # if the displays need to be rotated
        if rotated:
            direction = rotate(direction)

        if matrix in self.matrices:
            for col in range(8):
                if direction == DIR_L:
                    show_char[col] = curr_char[col + progress - (0 if col + progress < 8 else 8)]
                elif direction == DIR_R:
                    show_char[col] = curr_char[col - progress + (0 if col >= progress else 8)]
                elif direction == DIR_U:
                    show_char[col] = (curr_char[col] >> progress) + (next_char[col] << (8 - progress))
                elif direction == DIR_D:
                    show_char[col] = (curr_char[col] << progress) + (next_char[col] >> (8 - progress))

                self.send_matrix_reg_byte(matrix, col + 1, show_char[col])

    def scroll_message(self, message, repeats=0, speed=3, split_str=" ", direction=DIR_L, font=DEFAULT_FONT, finish=True):
        """
        Scroll some text messages across the lines, for a specified number of times (repeats)

        :param message: string message to display
        :param repeats: number of times to display - 0 for indefinite
        :param speed: how fast the message scrolls - 0(slowest) to 9(fastest)
        :param split_str: string to put between instances of message
        :param direction: direction to scroll in
        :param font:
        :param finish: Clears matrices at end of repeats if True
        """
        delay = 0.5 ** speed
        remainder = ""
        if repeats <= 0:
            indef = True
        else:
            indef = False

        counter = 0
        while indef or (counter < repeats):
            # First run is front padded
            if not counter:
                msg = " " * self.width + message + split_str
            # Last run is end padded
            elif counter == (repeats - 1):
                msg = message + " " * self.width
            else:
                msg = message + split_str
            counter +=1

            msg = remainder + msg
            print("m", msg)
            remainder = self.scroll_string(msg, delay)
            print("r", remainder)

        if finish:
            self.clear_all()

    def scroll_string(self, message, delay, direction=DIR_L, font=None, pad=True):
        matrices = self.matrices if direction == DIR_L else reversed(self.matrices)

        for c in range(len(message) - (len(matrices) - 1)):
            for stage in range(8):  # stage in the shift process
                for matrix in matrices:
                    old_char = message[matrix + c]
                    try:
                        new_char = message[matrix + c + 1]
                    except IndexError:
                        print(message[-self.width:])
                        return message[-self.width:]

                    self.send_matrix_shifted_letter(matrix, old_char, new_char, stage, direction=direction)
                time.sleep(delay)
