#!/bin/python3
"""
  An interrupt is defined by:
  - a trigger --> usually a pin on a IC
  - a threshold --> LOW, HIGH or float
  Once both conditions are fulfilled then a callback function is called
"""

from model.model import Ponicwatch_Table

class Interrupt(Ponicwatch_Table):
    """
    - name: to identify the system easily withion an area
    - location: where is the system installed
    - sys_type: NFT, aeroponic, Ebb and Flow, etc
    - nb_plants:  *important* number of plants is necessary to track the timing of plantations --> to do list
    """
    META = {"table": "tb_interrupt",
            "id": "interrupt_id",
            "columns": (
                "interrupt_id", # INTEGER NOT NULL,
                "name", # TEXT NOT NULL,
                "init" , #TEXT,
                "threshold", # INTEGER NOT NULL DEFAULT (0),
                "updated_on", # TIMESTAMP,
                "synchro_on", # TIMESTAMP
                )
            }

    def __init__(self, controller, system_name, hardware, db=None, *args, **kwargs):
        super().__init__(db or controller.db, Interrupt.META, *args, **kwargs)
        self.controller = controller
        self.hardware = hardware
        self.system_name = system_name + "/" + self["name"]
        # link the interrupt to the associated hardware pin if applicable
        if self["hardware"] != "N/A":
            self.hardware.register_interrupt(self.init_dict["pin"], self.on_interrupt)
        elif "timer" in self.init_dict: # special interrupt based on timer
            self.controller.add_cron_job(self.on_interrupt, self.init_dict["timer"])


    def on_interrupt(self):
        """Callback function for the 'init' dictionary entry
        - email_notification: to send an email listing all the PWO
        - reduce_log_table: drop rows in tb_log
        """
        if self.controller.debug >= 3:
            print("Call back on interrupt:", self, self.init_dict)
        # what to do?
        try:
            if self.init_dict["action"] == "email_notification":
                self.controller.ponicwatch_notification()
                msg = {
                    "text_value": "Notification email sent",
                    "value": self["id"]
                }
            elif self.init_dict["action"] == "reduce_log_table":
                nb_rows = self.controller.log.reduce_size(keep_days=self.init_dict.get('days', 90))
                msg = {
                    "text_value": "Log reduced",
                    "value": nb_rows
                }
        except KeyError as err:
            # no action? Really??
            self.controller.log.add_error(msg="Interrupt %s has NO action declared in its init field." % self.system_name)
            print(err)
        else:
            self.update()  # just to get the last updated_on timestamp
            msg["id"] = self["id"]
            msg["cls_name"] = self.__class__.__name__.upper()
            self.controller.log.add_log(system_name=self.system_name, param=msg)

    def __str__(self):
        return "{}".format(self["name"])
