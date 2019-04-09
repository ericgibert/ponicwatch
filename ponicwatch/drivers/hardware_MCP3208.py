#/bin/python3
"""
MCP3008/ MCP3208

12 Bit Analog to Digital Converter 4, 8 Input 1 SAR 16-PDIP


Pin Signal  Description                 GPIO        RPI Pin
1   CH0     10K NTC Sensor              -           -
2   CH1     10K POT-                    -           -

9   DGND    Digital Ground              GND         6
10  CS/SHDN Chip Select/Shut Down       CE0         24
11  DIN     Digital Serial Input        MOSI        19
12  DOUT    Digital Serial Output       MISO        21
13  CLK     Clock                       SCLK        23
14  AGND    Analogue Input Ground       GND         6
15  VREF    Reference Voltage           5 Volts     2
16  VDD     Positive Supply Voltage     3.3 Volts   1

spi_channel should be 0 (chip connected to CE0) or 1 (CE1)
baud should be 50000
"""

class Hardware_MCP3208(object):
    """
    12bits ADC driver
    """
    def __init__(self, pig, init_dict, debug=0):
        """

        :param pig: instance of a pigpio object created by the controller
        :param init_dict: parameters provided at initialization time
                { "channel": 0, "baud": 50000, "flags":0 }
                - channel: 0 (default) or 1
                - baud: int. default 50_000
                - flags: check the doc. def 0
        """
        self.pig = pig
        spi_channel, baud, spi_flags = (init_dict.get("channel", 0),
                                        init_dict.get("baud", 50000),
                                        init_dict.get("flags", 0))
        self.debug = max(debug, init_dict.get("debug", 0))
        try:
            self.spi_handle = self.pig.spi_open(spi_channel, baud, spi_flags)
            if self.debug >= 3: print("spi_handle open OK")
        except AttributeError as err:
            print("Unable to open SPI\n", err)

    def read(self, channel, param=5.0):
        """
        First send three bytes
        - byte 0 has 7 zeros and a start bit
        - byte 1 has the top bit set to indicate single rather than differential operation
                the next three bits contain the channel
                the bottom four bits are zero
        - byte 2 contains zeros (don't care)
        Then 3 bytes are returned:
        - byte 0 is ignored
        - byte 1 contains the high 4 bits
        - byte 2 contains the low 8 bits
        :param channel: channel corresponds to pins 0 (ch0 for pin=0) to 7 (ch7 for pin=7)
        :param param: 3.3V or 5.0V as the max Volt given on Vref (float)
        :return:

            r = spi.xfer2([4 | 2 |(channel>>2), (channel &3) << 6,0])
            adc_out = ((r[1]&15) << 8) + r[2]

        """
        # count, adc = self.pig.spi_xfer(self.spi_handle, [6 + ((4 & channel) >> 2), (3 & channel) << 6, 0])  # for 10 bits: [1,(8 + channel) << 4,0]
        try:
            count, adc = self.pig.spi_xfer(self.spi_handle, [4 | 2 |(channel>>2), (channel &3) << 6,0])
        except AttributeError:
            # REPLACE BY SIMULATION
            print("all zeroes for simulation")
            count, adc = 0, [0,0,0,0]
        if self.debug >= 3: print("read from MCP3208:", (count, adc))
        data = ((adc[1] & 15) << 8) + adc[2]
        volts12bits = (data * param) / 4095.0
        return (data, volts12bits)

    def cleanup(self):
        self.pig.spi_close(self.spi_handle)

    def write(self):
        raise NotImplementedError("MCP3208 is 12bits ADC: read only IC i.e. cannot write")

    def average(self, channel, samples, param=5.0):
        """read 'samples' measures and returns the average ignoring the lowest and highest ones"""
        readings = []
        for s in range(samples+2):
            readings.append(self.read(channel, param))
            #sleep(0.1)
        sampling = sorted(readings)[1:-1]
        return sum([s[0] for s in sampling]) / len(sampling), sum([s[1] for s in sampling]) / len(sampling)

    def __str__(self):
        return "ADC MCP3208"

if __name__ == "__main__":
    import pigpio
    from time import sleep
    pig = pigpio.pi()
    mcp3208 = Hardware_MCP3208(pig, { "channel": 0, "baud": 50000, "flags":0 }, debug=3)
    try:
        while True:
            for i in range(4):
                d, v = mcp3208.average(channel=i, samples=10)
                print("{}: {} => {:.2f}V \t".format(i, d, v), end="")
            print("\r", end="")
            sleep(2)
    finally:
        mcp3208.cleanup()
