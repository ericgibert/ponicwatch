#!/bin/python3
"""
    Model for the table tb_hardware
    Created by Eric Gibert on 31 Aug 2016

    Define the IC (probes, sensors, other...) that are present on the control board.
    Each hardware will have a driver to interact with defined in the 'drivers' module
"""
from model.model import Ponicwatch_Table
from drivers.hardware_DHT import Hardware_DHT
from drivers.hardware_DS18B20 import Hardware_DS18B20
from drivers.hardware_RPI3 import Hardware_RPI3, CALLBACKS as RPI3_CALLBACKS
from drivers.hardware_MCP23017 import Hardware_MCP23017
from drivers.hardware_MCP3208 import Hardware_MCP3208
from drivers.hardware_Gravity_pH import Hardware_Gravity_pH
from drivers.hardware_Gravity_TDS import Hardware_Gravity_TDS

class Hardware(Ponicwatch_Table):
    """
    - 'hardware_id' and 'name' identify uniquely a hardware IC within a Controller database.
    - 'mode': indicates if the switch should be 'READ' or 'WRITE' or 'R/W'
    - 'value': current state of the switch ( 0 = OFF, 1 = OFF )
    - 'hardware': serial number of the chip or other relevant identification
    - 'init': free string passed to the __init__ function to perform hardware initialization
    """
    MODE = {
       -1: "INACTIVE",# IC is no longer accessible
        0: "READ",    # IC can only be access for reading data
        1: "WRITE",   # IC can only accessed for writing data
        2: "R/W",     # IC supports for 'read' and 'write' modes
    }

    META = {"table": "tb_hardware",
            "id": "hardware_id",
            "columns": (
                         "hardware_id", # INTEGER NOT NULL,
                         "name", #  TEXT NOT NULL,
                         "mode", #  INTEGER NOT NULL DEFAULT (0),
                         "hardware", #  TEXT NOT NULL,
                         "init", #  TEXT NOT NULL,
                         "updated_on", #  TIMESTAMP,
                         "synchro_on", #  TIMESTAMP
                         "value",       # REAL DEFAULT (0.0)
                        )
            }

    def __init__(self, controller, system_name, db=None, *args, **kwargs):
        super().__init__(db or controller.db, Hardware.META, *args, **kwargs)
        self.debug = controller.debug
        self.controller = controller
        self.system_name = system_name + "/" + self["name"]
        if self["mode"] > self.INACTIVE:
            hardware, hw_init = self["hardware"], self.init_dict
            if hardware in Hardware_DHT.supported_models:  # DHT11|DHT22|AM2302
                self.driver = Hardware_DHT(pig=controller.pig, model=hardware, pin=translate_pin(hw_init["pin"]))
            elif hardware == "DS18B20":
                self.driver = Hardware_DS18B20(pig=controller.pig, device_folder=hw_init["path"])
            elif hardware == "RPI3":
                self.driver = Hardware_RPI3(pig=controller.pig, in_out=hw_init)
            elif hardware == "MCP23017":
                self.driver = Hardware_MCP23017(pig=controller.pig, hw_init_dict=hw_init)
            elif hardware == "MCP3208":
                self.driver = Hardware_MCP3208(pig=controller.pig, init_dict=hw_init)
            elif hardware == "GRAVITY_pH":
                self.driver = Hardware_Gravity_pH(pig=controller.pig,
                                                  init_dict=hw_init,
                                                  ADC=controller.get_pwo("Hardware", hw_init["ADC"]))
            elif hardware == "GRAVITY_TDS":
                self.driver = Hardware_Gravity_TDS(pig=controller.pig,
                                                   init_dict=hw_init,
                                                   ADC=controller.get_pwo("Hardware", hw_init["ADC"]),
                                                   water_temp_sensor=controller.get_pwo("Sensor", hw_init["water_temp_sensor"]))
            else:
                raise ValueError("Unknown hardware declared: {0} {1}".format(self["id"], hardware))

    def read(self, pin, param):
        """
        Fetch a two values tuple from the driver
        :param pin: pin number on the driver
        :param param: optional
        :return: (read raw value, calculated value) must be returned by the driver
        """
        if self.debug >= 3:
            print("Hardware read (pin, param) =", (pin, param))
        return self.driver.read(translate_pin(pin), param)

    def write(self, pin, value):
        """param is a tuple (pin, value)"""
        new_val = self.driver.write(translate_pin(pin), value)
        if new_val != self["value"]:
            self.update(value=new_val)
        self.controller.log.add_log(system_name=self.system_name, param=self)

    def average(self, pin, samples, param):
        """read many inpt and average"""
        if self.debug >= 3:
            print("Hardware average (pin, samples, param) =", (pin, samples, param))
        return self.driver.average(translate_pin(pin), samples, param)


    def cleanup(self):
        try:
            self.driver.cleanup()
        except AttributeError:
            pass

    def set_pin_as_input(self, pin):
        self.driver.set_pin_as_input(translate_pin(pin))

    def set_pin_as_output(self, pin):
        self.driver.set_pin_as_output(translate_pin(pin))

    def register_interrupt(self, pin, callback):
        # attach the Interrupt on the IC pin if requested
        pin = translate_pin(pin)
        if pin in RPI3_CALLBACKS:
            RPI3_CALLBACKS[pin].append(callback)
        else:
            RPI3_CALLBACKS[pin] = [callback]
        # if self.is_debug:
        #     print("Add to RPI3_CALLBACKS:")
        #     print(RPI3_CALLBACKS)

    def get_callbacks(self):
        try:
            callbacks = self.driver.get_callbacks()
        except AttributeError:
            callbacks = {}
        return callbacks

    @classmethod
    def all_keys(cls, db):
        return super().all_keys(db, Hardware.META)

    def __str__(self):
        return "{} ({})".format(self["name"], Hardware.MODE[self["mode"]])

    def get_html(self):
        """return a HTML string for extra information associated to a IC"""
        try:
            html_col1, html_col2 = "Extra Data", self.driver.get_html(with_javascript=True)
        except AttributeError:
            html_col1, html_col2 = "Extra Data", "No extra data"
        return (html_col1, html_col2)


# helper function #
def translate_pin(str_pin):
    """Accept a string representing an integer (base 10 or Hex) or A0,...,A7,B0,...,B7"""
    try:
        pin = int(str_pin)
    except TypeError:
        pin = None
    except ValueError:
        if str_pin.startswith("0x"):
            pin = int(str_pin, 16)
        elif str_pin[0] in ('A', 'B') and '0' <= str_pin[1] <= '7':
            pin = 8 * (str_pin[0] == 'B') + int(str_pin[1])
        else:
            pin = None
    return pin
