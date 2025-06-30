from pyuvm import *
from pyuvm import uvm_component_utils

@uvm_component_utils
class UARTSequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
