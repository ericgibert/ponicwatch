#!/usr/bin/python3
"""
Original dvelopment from Dan Woodruff
https://bitbucket.org/dewoodruff/mcp23017-python-3-library-with-interrupts

Adapted to work with pigpio and python3 by Eric gibert

"""
import time
import math


class IC_MCP23017(object):
    # constants
    OUTPUT = 0
    INPUT = 1
    LOW = 0
    HIGH = 1

    INTMIRRORON = 1
    INTMIRROROFF = 0
    # int pin starts high. when interrupt happens, pin goes low
    INTPOLACTIVELOW = 0
    # int pin starts low. when interrupt happens, pin goes high
    INTPOLACTIVEHIGH = 1
    INTERRUPTON = 1
    INTERRUPTOFF = 0
    INTERRUPTCOMPAREDEFAULT = 1
    INTERRUPTCOMPAREPREVIOUS = 0

    # register values for use below
    IOCONMIRROR = 6
    IOCONINTPOL = 1

    # i2c protocol
    IODIRA = 0x00
    IODIRB = 0x01
    GPINTENA = 0x04
    GPINTENB = 0x05
    DEFVALA = 0x06
    DEFVALB = 0x07
    INTCONA = 0x08
    INTCONB = 0x09
    IOCON = 0x0A  # 0x0B is the same
    GPPUA = 0x0C
    GPPUB = 0x0D
    INTFA = 0x0E
    INTFB = 0x0F
    INTCAPA = 0x10
    INTCAPB = 0x11
    GPIOA = 0x12
    GPIOB = 0x13
    OLATA = 0x14
    OLATB = 0x15

    def __init__(self, pig, address, num_gpios=16, busnum=1):
        """
        Create the driver to communicate with the MCP23017 chip by i2c
        :param pig: pigpio from the controller
        :param address: 0x20 when the 3 pins are grounded
        :param num_gpios: up to 16 for MCP23017
        :param busnum: bus number in (0,1) ; 0 for older version of Raspi
        """
        assert 0 <= num_gpios <= 16, "Number of GPIOs must be between 0 and 16"
        self.i2c_handle = pig.i2c_open(busnum, address)
        self.address = address
        self.num_gpios = num_gpios
        self.pig = pig

        # set defaults
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IODIRA, 0xFF)  # all inputs on port A
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IODIRB, 0xFF)  # all inputs on port B
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPIOA, 0x00)  # output register to 0
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPIOB, 0x00)  # output register to 0

        # read the current direction of all pins into instance variable
        # self.direction used for assertions in a few methods methods
        self.direction = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.IODIRA)
        self.direction |= self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.IODIRB) << 8

        # disable the pull-ups on all ports
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPPUA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPPUB, 0x00)

        # clear the IOCON configuration register, which is chip default
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IOCON, 0x00)

        ##### interrupt defaults
        # disable interrupts on all pins by default
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPINTENA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPINTENB, 0x00)
        # interrupt on change register set to compare to previous value by default
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.INTCONA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.INTCONB, 0x00)
        # interrupt compare value registers
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.DEFVALA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.DEFVALB, 0x00)
        # clear any interrupts to start fresh
        self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOA)
        self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOB)

    def _changeBit(self, bitmap, bit, value):
        """change a specific bit in a byte"""
        assert value in (0,1), "Value is %s must be 0 or 1" % value
        return bitmap & ~(1 << bit) if value == 0 else bitmap | (1 << bit)

    def _readAndChangePin(self, register, pin, value, curValue=None):
        """
        set an output pin to a specific value
        pin value is relative to a bank, so must be be between 0 and 7
        """
        assert 0 <= pin < 8, "Pin number %s is invalid, only 0-%s are valid" % (pin, 7)
        # if we don't know what the current register's full value is then get it first
        if curValue is None:
            curValue = self.pig.i2c_read_byte(register)
        # set the single bit that corresponds to the specific pin within the full register value
        newValue = self._changeBit(curValue, pin, value)
        # write and return the full register value
        self.pig.i2c_write_byte_data(self.i2c_handle, register, newValue)
        return newValue

    def set_pull_up(self, pin, value):
        """
        used to set the pullUp resistor setting for a pin
        pin value is relative to the total number of gpio, so 0-15 on mcp23017
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        # if the pin is < 8, use register from first bank else second bank
        self._readAndChangePin(IC_MCP23017.GPPUA if pin < 8 else IC_MCP23017.GPPUB, pin if pin < 8 else pin - 8, value)
        # if (pin < 8):
        #     return self._readAndChangePin(IC_MCP23017.GPPUA, pin, value)
        # else:
        #     # otherwise use register from second bank
        #     return self._readAndChangePin(IC_MCP23017.GPPUB, pin - 8, value) << 8

    def set_pin_mode(self, pin, mode):
        """
        Set pin to either input or output mode
        pin value is relative to the total number of gpio, so 0-15 on mcp23017
        returns the value of the combined IODIRA and IODIRB registers

        :mode:   IC_MCP23017.OUTPUT = 0, IC_MCP23017.INPUT = 1
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        # split the direction variable into bytes representing each gpio bank
        gpioa = self.direction & 0xff
        gpiob = (self.direction >> 8) & 0xff
        # if the pin is < 8, use register from first bank
        if (pin < 8):
            gpioa = self._readAndChangePin(IC_MCP23017.IODIRA, pin, mode)
        else:
            # otherwise use register from second bank
            # readAndChangePin accepts pin relative to register though, so subtract
            gpiob = self._readAndChangePin(IC_MCP23017.IODIRB, pin - 8, mode)
            # re-set the direction variable using the new pin modes
        self.direction = gpioa + (gpiob << 8)
        return self.direction

    def output(self, pin, value):
        """set an output pin to a specific value"""
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        # if the pin is < 8, use register from first bank
        if (pin < 8):
            self.outputvalue = self._readAndChangePin(IC_MCP23017.GPIOA, pin, value, self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.OLATA))
        else:
            # otherwise use register from second bank
            # readAndChangePin accepts pin relative to register though, so subtract
            self.outputvalue = self._readAndChangePin(IC_MCP23017.GPIOB, pin - 8, value, self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.OLATB))
        return self.outputvalue

    def input(self, pin):
        """
        read the value of a pin - the pin can be either set as INPUT or OUTPUT -
        return a 1 or 0
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        regValue = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOA if pin<8 else IC_MCP23017.GPIOB)
        if pin >= 8: pin -= 8
        return int(regValue & (1 << pin) != 0)
        # value = 0
        # # reads the whole register then compares the value of the specific pin
        # if (pin < 8):
        #     regValue = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOA)
        #     if regValue & (1 << pin) != 0: value = 1
        # else:
        #     regValue = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOB)
        #     if regValue & (1 << pin - 8) != 0: value = 1
        # # 1 or 0
        # return value


        # configure system interrupt settings

    # mirror - are the int pins mirrored? True=yes, False=INTA associated with PortA, INTB associated with PortB
    # intpol - polarity of the int pin. 1=active-high, 0=active-low
    def configSystemInterrupt(self, mirror, intpol):
        assert isinstance(mirror, bool), "Valid options for MIRROR: False or True"
        assert intpol in (0,1), "Valid options for INTPOL: 0 or 1"
        # get current register settings
        registerValue = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.IOCON)
        # set mirror bit
        registerValue = self._changeBit(registerValue, self.IOCONMIRROR, mirror)
        self.mirrorEnabled = mirror
        # set the intpol bit
        registerValue = self._changeBit(registerValue, self.IOCONINTPOL, intpol)
        # set ODR pin
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IOCON, registerValue)

    # configure interrupt setting for a specific pin. set on or off
    def configPinInterrupt(self, pin, enabled, compareMode=0, defval=0):
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        assert self.direction & (1 << pin) != 0, "Pin %s not set to input! Must be set to input before you can change interrupt config." % pin
        assert enabled in (0,1), "Valid options: 0 or 1"
        is_bank_A = pin < 8
        if not is_bank_A: pin -= 8
        # first, interrupt on change feature
        self._readAndChangePin(IC_MCP23017.GPINTENA if is_bank_A else IC_MCP23017.GPINTENB, pin, enabled)
        # then, compare mode (previous value or default value?)
        self._readAndChangePin(IC_MCP23017.INTCONA if is_bank_A else IC_MCP23017.INTCONB, pin, compareMode)
        # last, the default value. set it regardless if compareMode requires it, in case the requirement has changed since program start
        self._readAndChangePin(IC_MCP23017.DEFVALA if is_bank_A else IC_MCP23017.DEFVALB, pin, defval)
        # if (pin < 8):
        #     # first, interrupt on change feature
        #     self._readAndChangePin(IC_MCP23017.GPINTENA, pin, enabled)
        #     # then, compare mode (previous value or default value?)
        #     self._readAndChangePin(IC_MCP23017.INTCONA, pin, compareMode)
        #     # last, the default value. set it regardless if compareMode requires it, in case the requirement has changed since program start
        #     self._readAndChangePin(IC_MCP23017.DEFVALA, pin, defval)
        # else:
        #     self._readAndChangePin(IC_MCP23017.GPINTENB, pin - 8, enabled)
        #     self._readAndChangePin(IC_MCP23017.INTCONB, pin - 8, compareMode)
        #     self._readAndChangePin(IC_MCP23017.DEFVALB, pin - 8, defval)

    # private function to return pin and value from an interrupt
    def _readInterruptRegister(self, port):
        assert port in (0,1), "Port to get interrupts from must be 0 or 1!"
        interrupted = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFA if port==0 else IC_MCP23017.INTCAPB)
        if interrupted:
            pin = int(math.log(interrupted, 2))  # first non 0 pin having triggered the interrupt
            # get the value of the pin
            value_register = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTCAPA if port==0 else IC_MCP23017.INTCAPB)
            return pin if port==0 else pin + 8, int(value_register & (1 << pin) != 0)
        else:
            return None, 0

        # value = 0
        # pin = None
        # if port == 0:
        #     interruptedA = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFA)
        #     if interruptedA != 0:
        #         pin = int(math.log(interruptedA, 2))
        #         # get the value of the pin
        #         valueRegister = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTCAPA)
        #         if valueRegister & (1 << pin) != 0: value = 1
        # else:
        #     interruptedB = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFB)
        #     if interruptedB != 0:
        #         pin = int(math.log(interruptedB, 2))
        #         # get the value of the pin
        #         valueRegister = self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTCAPB)
        #         if valueRegister & (1 << pin) != 0: value = 1
        #         # want return 0-15 pin value, so add 8
        #         pin = pin + 8
        # return pin, value

    def readInterrupt(self, port=None):
        """
        this function should be called when INTA or INTB is triggered to indicate an interrupt occurred
        optionally accepts the bank number that caused the interrupt (0 or 1)
        the function determines the pin that caused the interrupt and gets its value
        the interrupt is cleared
        returns pin and the value
        pin is 0 - 15, not relative to bank
        """
        assert self.mirrorEnabled or port in (0,1), "Mirror not enabled and port not specified - call with port (0 or 1) or set mirrored."
        # default value of pin. will be set to 1 if the pin is high
        # if the mirror is enabled, we don't know what port caused the interrupt, so read both
        if self.mirrorEnabled:
            # read port 0 first, if no pin, then read and return port 1
            pin, value = self._readInterruptRegister(0)
            return pin, value if pin else self._readInterruptRegister(1)
        else:
            return self._readInterruptRegister(port)


    # check to see if there is an interrupt pending 3 times in a row (indicating it's stuck)
    # and if needed clear the interrupt without reading values
    # return 0 if everything is ok
    # return 1 if the interrupts had to be forcefully cleared
    def clearInterrupts(self):
        if self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFA) > 0 or self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFB) > 0:
            iterations = 3
            count = 1
            # loop to check multiple times to lower chance of false positive
            while count <= iterations:
                if self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFA) == 0 and self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.INTFB) == 0:
                    return 0
                else:
                    time.sleep(.5)
                    count += 1
            # if we made it to the end of the loop, reset
            if count >= iterations:
                self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOA)
                self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOB)
                return 1

    # cleanup function - set values everything to safe values
    # should be called when program is exiting
    def cleanup(self):
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IODIRA, 0xFF)  # all inputs on port A
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IODIRB, 0xFF)  # all inputs on port B
        # make sure the output registers are set to off
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPIOA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPIOB, 0x00)
        # disable the pull-ups on all ports
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPPUA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPPUB, 0x00)
        # clear the IOCON configuration register, which is chip default
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.IOCON, 0x00)

        # disable interrupts on all pins 
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPINTENA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.GPINTENB, 0x00)
        # interrupt on change register set to compare to previous value by default
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.INTCONA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.INTCONB, 0x00)
        # interrupt compare value registers
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.DEFVALA, 0x00)
        self.pig.i2c_write_byte_data(self.i2c_handle, IC_MCP23017.DEFVALB, 0x00)
        # clear any interrupts to start fresh
        self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOA)
        self.pig.i2c_read_byte_data(self.i2c_handle, IC_MCP23017.GPIOB)

if __name__ == "__main__":
    import pigpio

    pig = pigpio.pi()
    test_IC = IC_MCP23017(pig, 0x20)

    IN_PIN, OUT_PIN = 0, 8
    test_IC.set_pin_mode(IN_PIN, IC_MCP23017.INPUT)
    test_IC.set_pin_mode(OUT_PIN, IC_MCP23017.OUTPUT)
    test_IC.set_pull_up(8, IC_MCP23017.LOW)
    v = 0
    while True:
        nv = test_IC.input(IN_PIN)
        if v != nv:
            test_IC.output(OUT_PIN, nv)
            print("new value=", nv)
            v = nv
        time.sleep(0.5)