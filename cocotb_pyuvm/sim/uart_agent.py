from pyuvm import *
from uart_driver import UARTDriver
from uart_monitor import UARTMonitor
from uart_sequencer import UARTSequencer

# UART Agent
class UARTAgent(uvm_agent):
    def __init__(self, name, parent):
        super().__init__(name)
        self.driver = None
        self.sequencer = None
        self.monitor = None
        self.cfg = None

    def build_phase(self):
        success, self.cfg = ConfigDB().get(self, "", "cfg")
        if not success:
            uvm_fatal("NO_CFG", f"Configuration must be set for: {self.get_full_name()}.cfg")
        
        self.monitor = UARTMonitor.create("monitor", self)
        
        if self.cfg.is_active:
            self.driver = UARTDriver.create("driver", self)
            self.sequencer = UARTSequencer.create("sequencer", self)

    def connect_phase(self):
        if self.cfg.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
