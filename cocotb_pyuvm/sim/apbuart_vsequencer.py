from pyuvm import *

class VSequencer(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.apb_sqr = None
        self.uart_sqr = None

    def end_of_elaboration_phase(self, phase):
        super().end_of_elaboration_phase(phase)
        self.apb_sqr = ConfigDB().get(None, "", "apb_sqr", None)
        self.uart_sqr = ConfigDB().get(None, "", "uart_sqr", None)        
        if not self.apb_sqr:
            uvm_fatal("VSQR/CFG/NOAPB", "No apb_sqr specified for this instance")

        if not self.uart_sqr:
            uvm_fatal("VSQR/CFG/NOUART", "No uart_sqr specified for this instance")
