from pyuvm import *

class UARTSequencer(uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
