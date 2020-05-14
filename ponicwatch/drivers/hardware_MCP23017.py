#!/usr/bin/python3
"""
MCP23017 - i2c 16 input/output port expander

The MCP23017 uses two i2c pins (these can be shared with other i2c devices), and in exchange gives you 16 general purpose pins.
You can set each of 16 pins to be input, output, or input with a pullup. There's even the ability to get an interrupt
via an external pin when any of the inputs change so you don't have to keep polling the chip.

Original development from Dan Woodruff
https://bitbucket.org/dewoodruff/mcp23017-python-3-library-with-interrupts

Adapted to work with pigpio and python3 by Eric Gibert

Checking i2c bus:
    sudo i2cdetect -y 1
from https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

"""
import time
import math

class Hardware_MCP23017(object):
    # constants
    OUTPUT = 0
    INPUT = 1
    LOW = 0
    HIGH = 1

    INTMIRRORON = True
    INTMIRROROFF = False
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

    def __init__(self, pig, init_dict, num_gpios=16, debug=0):
        """
        Create the driver to communicate with the MCP23017 chip by i2c
        :param pig: pigpio from the controller
        :param init_dict: 1.0x20.16 when the 3 address pins are grounded and INTA is connected to RASPI pin 16
        :param num_gpios: up to 16 for MCP23017
        """
        assert 0 <= num_gpios <= 16, "Number of GPIOs must be between 0 and 16"
        self.pig = pig
        self.hw_init_dict = init_dict
        self.debug = max(debug, init_dict.get("debug", 0))
        busnum, self.address, interrupt = (init_dict["bus"],
                                           init_dict["address"] if isinstance(init_dict["address"], int) else int(init_dict["address"], 16),
                                           init_dict["interrupt"])
        self.i2c_handle = self.pig.i2c_open(busnum, self.address)
        self.num_gpios = num_gpios

        # set defaults
        self._write_byte(Hardware_MCP23017.IODIRA, 0xFF)  # all inputs on port A
        self._write_byte(Hardware_MCP23017.IODIRB, 0xFF)  # all inputs on port B
        self._write_byte(Hardware_MCP23017.GPIOA, 0x00)  # output register to 0
        self._write_byte(Hardware_MCP23017.GPIOB, 0x00)  # output register to 0

        # read the current direction of all pins into instance variable
        # self.direction used for assertions in a few methods methods
        self.direction = self._read_byte(Hardware_MCP23017.IODIRA) | (self._read_byte(Hardware_MCP23017.IODIRB) << 8)

        # disable the pull-ups on all ports
        self._write_byte(Hardware_MCP23017.GPPUA, 0x00)
        self._write_byte(Hardware_MCP23017.GPPUB, 0x00)

        # clear the IOCON configuration register, which is chip default
        self._write_byte(Hardware_MCP23017.IOCON, 0x00)

        ##### interrupt defaults
        # disable interrupts on all pins by default
        self._write_byte(Hardware_MCP23017.GPINTENA, 0x00)
        self._write_byte(Hardware_MCP23017.GPINTENB, 0x00)
        # interrupt on change register set to compare to previous value by default
        self._write_byte(Hardware_MCP23017.INTCONA, 0x00)
        self._write_byte(Hardware_MCP23017.INTCONB, 0x00)
        # interrupt compare value registers
        self._write_byte(Hardware_MCP23017.DEFVALA, 0x00)
        self._write_byte(Hardware_MCP23017.DEFVALB, 0x00)
        # clear any interrupts to start fresh
        self._read_byte(Hardware_MCP23017.GPIOA)
        self._read_byte(Hardware_MCP23017.GPIOB)

        # define interruption
        if interrupt:
            self.config_system_interrupt(mirror=Hardware_MCP23017.INTMIRROROFF, intpol=Hardware_MCP23017.INTPOLACTIVEHIGH)

    def _write_byte(self, register, value):
        """helper function"""
        self.pig.i2c_write_byte_data(self.i2c_handle, register, value)
        
    def _read_byte(self, register):
        """helper function"""
        return self.pig.i2c_read_byte_data(self.i2c_handle, register)

    def _change_bit(self, bitmap, bit, value):
        """change a specific bit in a byte"""
        assert value in (0,1), "Value is %s must be 0 or 1" % value
        return bitmap & ~(1 << bit) if value == 0 else bitmap | (1 << bit)

    def _read_and_change_pin(self, register, pin, value, curValue=None):
        """
        set an output pin to a specific value
        pin value is relative to a bank, so must be be between 0 and 7
        """
        assert 0 <= pin < 8, "Pin number %s is invalid, only 0-%s are valid" % (pin, 7)
        # if we don't know what the current register's full value is then get it first
        if curValue is None:
            curValue = self._read_byte(register)
        # set the single bit that corresponds to the specific pin within the full register value
        newValue = self._change_bit(curValue, pin, value)
        # write and return the full register value
        self._write_byte(register, newValue)
        return newValue

    def set_pull_up(self, pin, value):
        """
        used to set the pullUp resistor setting for a pin
        pin value is relative to the total number of gpio, so 0-15 on mcp23017
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        # if the pin is < 8, use register from first bank else second bank
        self._read_and_change_pin(Hardware_MCP23017.GPPUA if pin < 8 else Hardware_MCP23017.GPPUB, pin if pin < 8 else pin - 8, value)

    def set_pin_mode(self, pin, mode):
        """
        Set pin to either input or output mode
        pin value is relative to the total number of gpio, so 0-15 on mcp23017
        returns the value of the combined IODIRA and IODIRB registers

        :mode:   Hardware_MCP23017.OUTPUT = 0, Hardware_MCP23017.INPUT = 1
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        # split the direction variable into bytes representing each gpio bank
        gpioa = self.direction & 0xff
        gpiob = (self.direction >> 8) & 0xff
        # if the pin is < 8, use register from first bank
        if (pin < 8):
            gpioa = self._read_and_change_pin(Hardware_MCP23017.IODIRA, pin, mode)
        else:
            # otherwise use register from second bank ; radAndChangePin accepts pin relative to register so subtract 8
            gpiob = self._read_and_change_pin(Hardware_MCP23017.IODIRB, pin - 8, mode)
        # re-set the direction variable using the new pin modes
        self.direction = gpioa + (gpiob << 8)
        return self.direction

    def set_pin_as_input(self, pin):
        self.set_pin_mode(pin, Hardware_MCP23017.INPUT)

    def set_pin_as_output(self, pin):
        self.set_pin_mode(pin, Hardware_MCP23017.OUTPUT)

    def write(self, pin, value):
        """set an output pin to a specific value"""
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        # assert self.direction & (1 << pin) == 0, "Pin %s not set to output" % pin
        # if the pin is < 8, use register from first bank
        if (pin < 8):
            self.outputvalue = self._read_and_change_pin(Hardware_MCP23017.GPIOA, pin, value, self._read_byte(Hardware_MCP23017.OLATA))
        else:
            # otherwise use register from second bank ; readAndChangePin accepts pin relative to register so subtract 8
            self.outputvalue = self._read_and_change_pin(Hardware_MCP23017.GPIOB, pin - 8, value, self._read_byte(Hardware_MCP23017.OLATB))
        return self.outputvalue

    def read(self, pin, param=None):
        """
        read the value of a pin - the pin can be either set as INPUT or OUTPUT -
        return a 1 or 0
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        regValue = self._read_byte(Hardware_MCP23017.GPIOA if pin < 8 else Hardware_MCP23017.GPIOB)
        value = int(regValue & (1 << (pin if pin < 8 else pin - 8)) != 0)
        return (value, value)


    ### configure system  - interrupt settings ###

    def config_system_interrupt(self, mirror, intpol):
        """
        :param mirror: are the int pins mirrored? True=yes, False=INTA associated with PortA, INTB associated with PortB
        :param intpol: polarity of the int pin. 1=active-high, 0=active-low
        :return:
        """
        assert isinstance(mirror, bool), "Valid options for MIRROR: False or True"
        assert intpol in (0,1), "Valid options for INTPOL: 0 or 1"
        # get current register settings
        registerValue = self._read_byte(Hardware_MCP23017.IOCON)
        # set mirror bit
        registerValue = self._change_bit(registerValue, self.IOCONMIRROR, mirror)
        self.mirrorEnabled = mirror
        # set the intpol bit
        registerValue = self._change_bit(registerValue, self.IOCONINTPOL, intpol)
        # set ODR pin
        self._write_byte(Hardware_MCP23017.IOCON, registerValue)

    def config_pin_interrupt(self, pin, enabled, compareMode=0, defval=0):
        """
        configure interrupt setting for a specific pin. set on or off
        :param pin:
        :param enabled: boolean to enable/disable
        :param compareMode:
        :param defval:
        :return:
        """
        assert 0 <= pin < self.num_gpios, "Pin number %s is invalid, only 0-%s are valid" % (pin, self.num_gpios)
        assert self.direction & (1 << pin) != 0, "Pin %s not set to input! Must be set to input before you can change interrupt config." % pin
        assert isinstance(enabled, bool), "enabled must be boolean: True or False"
        is_bank_A = pin < 8
        if not is_bank_A: pin -= 8
        # first, interrupt on change feature
        self._read_and_change_pin(Hardware_MCP23017.GPINTENA if is_bank_A else Hardware_MCP23017.GPINTENB, pin, enabled)
        # then, compare mode (previous value or default value?)
        self._read_and_change_pin(Hardware_MCP23017.INTCONA if is_bank_A else Hardware_MCP23017.INTCONB, pin, compareMode)
        # last, the default value. set it regardless if compareMode requires it, in case the requirement has changed since program start
        self._read_and_change_pin(Hardware_MCP23017.DEFVALA if is_bank_A else Hardware_MCP23017.DEFVALB, pin, defval)

    def _read_interrupt_register(self, port):
        """
        private function to return pin and value from an interrupt
        :param port:
        :return:
        """
        assert port in (0,1), "Port to get interrupts from must be 0 or 1!"
        interrupted = self._read_byte(Hardware_MCP23017.INTFA if port==0 else Hardware_MCP23017.INTCAPB)
        if interrupted:
            pin = int(math.log(interrupted, 2))  # first non 0 pin having triggered the interrupt
            # get the value of the pin
            value_register = self._read_byte(Hardware_MCP23017.INTCAPA if port == 0 else Hardware_MCP23017.INTCAPB)
            return pin if port==0 else pin + 8, int(value_register & (1 << pin) != 0)
        else:
            return None, None

    def on_interrupt(self, port=None):
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
            pin, value = self._read_interrupt_register(0)
            return pin, value if pin else self._read_interrupt_register(1)
        else:
            return self._read_interrupt_register(port)

    def clear_interrupts(self):
        """
        check to see if there is an interrupt pending 3 times in a row (indicating it's stuck)
        and if needed clear the interrupt without reading values
        return 0 if everything is ok
        return 1 if the interrupts had to be forcefully cleared
        :return:
        """
        if self._read_byte(Hardware_MCP23017.INTFA) > 0 or self._read_byte(Hardware_MCP23017.INTFB) > 0:
            iterations = 3
            count = 1
            # loop to check multiple times to lower chance of false positive
            while count <= iterations:
                if self._read_byte(Hardware_MCP23017.INTFA) == 0 and self._read_byte(Hardware_MCP23017.INTFB) == 0:
                    return 0
                else:
                    time.sleep(.5)
                    count += 1
            # if we made it to the end of the loop, reset
            if count >= iterations:
                self._read_byte(Hardware_MCP23017.GPIOA)
                self._read_byte(Hardware_MCP23017.GPIOB)
                return 1

    def cleanup(self):
        """
        cleanup function - set values everything to safe values
        should be called when program is exiting
        :return:
        """
        self._write_byte(Hardware_MCP23017.IODIRA, 0xFF)  # all inputs on port A
        self._write_byte(Hardware_MCP23017.IODIRB, 0xFF)  # all inputs on port B
        # make sure the output registers are set to off
        self._write_byte(Hardware_MCP23017.GPIOA, 0x00)
        self._write_byte(Hardware_MCP23017.GPIOB, 0x00)
        # disable the pull-ups on all ports
        self._write_byte(Hardware_MCP23017.GPPUA, 0x00)
        self._write_byte(Hardware_MCP23017.GPPUB, 0x00)
        # clear the IOCON configuration register, which is chip default
        self._write_byte(Hardware_MCP23017.IOCON, 0x00)

        # disable interrupts on all pins 
        self._write_byte(Hardware_MCP23017.GPINTENA, 0x00)
        self._write_byte(Hardware_MCP23017.GPINTENB, 0x00)
        # interrupt on change register set to compare to previous value by default
        self._write_byte(Hardware_MCP23017.INTCONA, 0x00)
        self._write_byte(Hardware_MCP23017.INTCONB, 0x00)
        # interrupt compare value registers
        self._write_byte(Hardware_MCP23017.DEFVALA, 0x00)
        self._write_byte(Hardware_MCP23017.DEFVALB, 0x00)
        # clear any interrupts to start fresh
        self._read_byte(Hardware_MCP23017.GPIOA)
        self._read_byte(Hardware_MCP23017.GPIOB)

    def get_html(self, with_javascript=False):
        """return the radiobutton list to set the pins IN/OUT"""
        radio_IN_html = """
            <td>{}<input type="radio"{}/> IN</td>"""
        radio_OUT_html = """<td>{3}
            <input type="radio" name="out{0}" onclick="handleClick(this);" {1} value="ON"/> ON
            <input type="radio" name="out{0}" onclick="handleClick(this);" {2} value="OFF"/> OFF</td>"""
        html = """\n<table border="1">\n"""
        for port in ("A", "B"):
            html += """<tr><td>%s0..7</td>""" % port
            dir = self.direction & 255 if port == "A" else (self.direction >> 8) & 0xff
            for i in range(8):
                i_or_o = dir & (1 << i)
                pin = port + str(i)
                pin_val = self.read(self.translate_pin(pin))[0]
                try:
                    pin_name = self.hw_init_dict["names"][pin] + "<br/>"
                except KeyError:
                    pin_name = ""
                try:
                    ON_value = self.hw_init_dict["ON_value"]
                except KeyError:
                    ON_value = 1
                if i_or_o:  # output = 0 ; input != 0
                    html += radio_IN_html.format(pin_name, " checked" if pin_val else "")
                else:
                    html += radio_OUT_html.format(pin,
                                                  " checked" if pin_val==ON_value else "",
                                                  "" if pin_val==ON_value else " checked",
                                                  pin_name)
            html += "</tr>\n"
        html += "</table>\n"
        if with_javascript:
            html += """
            <script>
                function handleClick(myRadio) {
                    var xhttp = new XMLHttpRequest();
                    xhttp.open("POST", 
                               "/hardware/" + document.getElementsByName('hardware_id')[0].value + "/" +myRadio.name + "/" + myRadio.value, 
                               true);
                    xhttp.setRequestHeader("Content-type", "application/json");
                    xhttp.send();
                    var response = JSON.parse(xhttp.responseText);
                    alert('New value: ' + myRadio.value);
                }
            </script>
            """
        return html

    # helper function #
    def translate_pin(self, str_pin):
        """Accept a string representing an integer (base 10 or Hex) or A0,...,A7,B0,...,B7"""
        if str_pin[0] in ('A', 'B') and '0' <= str_pin[1] <= '7':
            return 8 + int(str_pin[1]) if str_pin[0] == 'B' else int(str_pin[1])
        elif str_pin.startswith("0x"):
            return int(str_pin, 16)
        else:
            return int(str_pin)

if __name__ == "__main__":
    import pigpio
    pig = pigpio.pi()
    test_IC = Hardware_MCP23017(pig, { "bus":1, "address": "0x20", "interrupt": ""})
    #IN_PIN, OUT_PIN = test_IC.translate_pin("B0"), test_IC.translate_pin("A0")
    for IN_PIN in range(8):
        in_pin = test_IC.translate_pin("B{}".format(IN_PIN))
        test_IC.write(in_pin, 0)
        test_IC.set_pin_as_input(in_pin)
        test_IC.set_pull_up(in_pin, Hardware_MCP23017.LOW)
    for OUT_PIN in range(4):
        test_IC.set_pin_mode(OUT_PIN, Hardware_MCP23017.OUTPUT)
    v = 0
    last_in = -1
    try:
        while True:
            for IN_PIN in range(8):
                in_pin = test_IC.translate_pin("B{}".format(IN_PIN))
                new_in = test_IC.read(in_pin)
                print("pin {}: {}  -> {}".format(in_pin, new_in, "OFF" if new_in[0]==0 else "ON"))
                
            for OUT_PIN in range(4):
                print("Set pin {} to {}".format(OUT_PIN,v))
                test_IC.write(OUT_PIN, v)
            v = 0 if v==1 else 1
            
            time.sleep(2)
    finally:
        test_IC.cleanup()
