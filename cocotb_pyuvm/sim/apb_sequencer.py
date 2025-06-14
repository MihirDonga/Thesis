from pyuvm import *

@uvm_component_utils
class apb_sequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
