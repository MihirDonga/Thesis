from pyuvm import *
from uart_sequencer import UARTSequencer
class VSequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.apb_sqr = None
        self.uart_sqr = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apb_sqr = ConfigDB().get(None, "", "apb_sqr")
        self.uart_sqr = ConfigDB().get(None, "", "uart_sqr")        
        if not self.apb_sqr:
            uvm_fatal("VSQR/CFG/NOAPB", "No apb_sqr specified for this instance")

        if not self.uart_sqr:
            uvm_fatal("VSQR/CFG/NOUART", "No uart_sqr specified for this instance")
