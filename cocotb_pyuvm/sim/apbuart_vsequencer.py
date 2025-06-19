from pyuvm import *

class VSequencer(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.apb_sqr = None
        self.uart_sqr = None

    def end_of_elaboration_phase(self):
        success, self.apb_sqr = ConfigDB().get(self, "", "apb_sqr")
        if not success:
            uvm_fatal("VSQR/CFG/NOAPB", "No apb_sqr specified for this instance")

        success, self.uart_sqr = ConfigDB().get(self, "", "uart_sqr")
        if not success:
            uvm_fatal("VSQR/CFG/NOUART", "No uart_sqr specified for this instance")
