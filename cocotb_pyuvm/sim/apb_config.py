from pyuvm import uvm_object
from vsc import *
from enum import Enum, auto

# Constants (SystemVerilog `define`s)
UART_START_ADDR = 0
UART_END_ADDR   = 5

class uvm_active_passive_enum(Enum):
    UVM_ACTIVE = auto()
    UVM_PASSIVE = auto()

class apb_config(uvm_object):
    def __init__(self, name="apb_config"):
        super().__init__(name)

        # Randomized field
        self.slave_Addr = vsc.rand_uint32_t()  

        # Static fields
        self.psel_Index = 0
        self.is_active = uvm_active_passive_enum.UVM_ACTIVE

        self._setup_constraints()
        
    # Constrained randomization
    def _setup_constraints(self):
        @vsc.constraint 
        def addr_cst(self):
            self.slave_Addr.inside(vsc.rangelist(UART_START_ADDR, UART_END_ADDR))

    def randomize(self):
        """Randomize with constraints"""
        try:
            if not vsc.randomize(self):
                self.uvm_report_error("RAND_FAIL", "Randomization failed")
                return 0
            self.AddrCalcFunc()  # Update psel_Index after randomization
            return 1
        except Exception as e:
            self.uvm_report_error("RAND_EXCEPT", f"Randomization exception: {str(e)}")
            return 0
         
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
