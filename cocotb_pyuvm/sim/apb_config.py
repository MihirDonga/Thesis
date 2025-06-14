# apb_config.py
from pyuvm import *
import random
from enum import Enum

# Constants (SystemVerilog `define`s)
UART_START_ADDR = 0
UART_END_ADDR   = 5

class uvm_active_passive_enum(Enum):
    UVM_ACTIVE = 0
    UVM_PASSIVE = 1

class apb_config(uvm_object):
    def __init__(self, name="apb_config"):
        super().__init__(name)

        # Randomized field
        self.slave_Addr = None
        
        # Static fields
        self.psel_Index = 0
        self.is_active = uvm_active_passive_enum.UVM_ACTIVE

    def randomize(self):
        # Constrained randomization
        self.slave_Addr = random.randint(UART_START_ADDR, UART_END_ADDR)
        self.AddrCalcFunc()

    def AddrCalcFunc(self):
        if UART_START_ADDR <= self.slave_Addr <= UART_END_ADDR:
            self.psel_Index = 0b001
        else:
            self.psel_Index = 0b000

    def __str__(self):
        return (f"APB Config:\n"
                f"  slave_Addr: {self.slave_Addr}\n"
                f"  psel_Index: {self.psel_Index:03b}\n"
                f"  is_active: {self.is_active.name}")
