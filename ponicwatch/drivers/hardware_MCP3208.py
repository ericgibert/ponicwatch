#/bin/python3
"""
MCP3008/ MCP3208
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
    def __init__(self, pig, trx_flags):
        self.pig = pig
        flags = trx_flags.split('.')  # like 0.50000.0  with the last .0 optional
        spi_channel, baud, spi_flags = int(flags[0]), int(flags[1]), int(flags[2]) if len(flags)==3 else 0
        self.spi_handle = self.pig.spi_open(spi_channel, baud, spi_flags)

    def read(self, channel, param=None):
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
        :param channel: channel corresponds to pins 1 (ch0) to 8 (ch7)
        :param param: N/A
        :return:
        """
        count, adc = self.pig.spi_xfer(self.spi_handle, [6 + ((4 & channel) >> 2), (3 & channel) << 6, 0])  # for 10 bits: [1,(8 + channel) << 4,0]
        print("read from MCP3208:", (count, adc))
        data = ((adc[1] & 15) << 8) + adc[2]
        volts12bits = (data * 3.3) / 4095.0
        return (data, volts12bits)

    def cleanup(self):
        self.pig.spi_close(self.spi_handle)