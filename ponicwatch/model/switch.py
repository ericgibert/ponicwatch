#!/bin/python3
"""
    Model for the table tb_switch.

    Swicthes are objects linked to a hardware pin (with or without a relay) to control an pieceof equipement (pump, light,...).
    They belong to one Controller that controls their state.
    A switch is either set manually ON/OFF while in AUTO mode,the controler will tabulate the current time on the 'timer' string.

    - 'switch_id' and 'name' identify uniquely a switch withon a Controller database.
    - 'mode': indicates if the switch should be 'ON' or 'OFF' or 'AUTO'
        * at starting time, a switch of mode 'ON' will be set on, 'OFF' will be turn off (default)
        * in 'AUTO' mode, the state of the switch is define by the current time tabulated in the 'timer' sting --> 0 = OFF, 1 = OFF
    - 'value': current state of the switch ( 0 = OFF, 1 = OFF )
    - 'hardware': identification of the hardware undelying the switch. Usually a pin number within an IC.
    - 'timer': list of 0 (OFF) and 1 (ON), each representing a position for a given time.
    - 'timer_interval': duration in  minutes of one timer unit, usually 15 minutes.
"""

class Switch(object):
    """

    """
    OFF = 0    # either the switch mode or the timer off
    ON = 1     # either the switch mode or the timer on
    AUTO = 2   # switch mode to automatic i.e. relies on current time & 'timer' to know the current value

    def __init__(self, db, name=None, id=None):
        self.db = db
        (self.switch_id, self.name, self.mode, self.hardware,
         self.timer, self.value, self.timer_interval) = None, None, None, None, None, None, None
        if name:
            self.get_switch(name=name)
        elif id:
            self.get_switch(id=id)

    def get_switch(self, name=None, id=None):
        """
        Fetch one record from tb_switch matching either of the given parameters
        :param name: tb_switch.name (string)
        :param id: tb_switch.switch_id (int)
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if name and type(name) is str:
                    curs.execute("SELECT * from tb_switch where name=?", (name,))
                elif id and type(id) is int:
                    curs.execute("SELECT * from tb_switch where switch_id=?", (id,))
                else:
                    raise ValueError
                switch_row = curs.fetchall()
                if len(switch_row) == 1:
                    (self.switch_id, self.name, self.mode, self.hardware,
                     self.timer, self.value, self.timer_interval) = switch_row[0]
            finally:
                curs.close()

    def __str__(self):
        return "{} ({})".format(self.name, self.mode)