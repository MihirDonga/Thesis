from pyuvm import *
from uart_sequencer import UARTSequencer
class VSequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.apb_sqr = None
        self.uart_sqr = None

    def end_of_elaboration_phase(self):
        super().end_of_elaboration_phase()
        self.apb_sqr = ConfigDB().get(self, "", "apb_sqr", self.apb_sqr)
        self.uart_sqr = ConfigDB().get(self, "", "uart_sqr", self.uart_sqr)        
        if self.apb_sqr is None:
            uvm_fatal("VSQR/CFG/NOAPB", "No apb_sqr specified for this instance")

        if self.uart_sqr is None:
            uvm_fatal("VSQR/CFG/NOUART", "No uart_sqr specified for this instance")
