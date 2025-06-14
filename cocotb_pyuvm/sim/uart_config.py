# uart_config.py
from pyuvm import *
import random

from enum import Enum
class uvm_active_passive_enum(Enum):
    UVM_ACTIVE = 0
    UVM_PASSIVE = 1

class uart_config(uvm_object):
    def __init__(self, name="uart_config"):
        super().__init__(name)
        # From APB AGENTs (randomizable)
        self.frame_len = None
        self.n_sb = None
        self.parity = None
        self.bRate = None

        # To UART Monitor
        self.baud_rate = None

        # Constants (Addresses)
        self.baud_config_addr      = 0
        self.frame_config_addr     = 4
        self.parity_config_addr    = 8
        self.stop_bits_config_addr = 12
        self.trans_data_addr       = 16
        self.receive_data_addr     = 20
        self.loop_time             = 10

        # UVM active/passive enum equivalent
        self.is_active = uvm_active_passive_enum.UVM_ACTIVE

    def randomize(self):
        # Apply constraints
        self.frame_len = random.choice([5, 6, 7, 8])
        self.n_sb = random.choice([0, 1])
        self.parity = random.choice([0, 1, 2, 3])
        self.bRate = random.choice([4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 63, 0])
        self.baudRateFunc()

    def baudRateFunc(self):
        bRate_to_baud = {
            4800:   10416,
            9600:   5208,
            14400:  3472,
            19200:  2604,
            38400:  1302,
            57600:   868,
            115200:  434,
            128000:  392,
        }
        self.baud_rate = bRate_to_baud.get(self.bRate, 5208)

    def __str__(self):
        return (f"UART Config:\n"
                f"  frame_len: {self.frame_len}\n"
                f"  n_sb: {self.n_sb}\n"
                f"  parity: {self.parity}\n"
                f"  bRate: {self.bRate}\n"
                f"  baud_rate: {self.baud_rate}\n"
                f"  is_active: {self.is_active.name}")


