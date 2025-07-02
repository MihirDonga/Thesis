from pyuvm import *
from uart_driver import UARTDriver
from uart_monitor import UARTMonitor
from uart_sequencer import UARTSequencer
from uart_config import uart_config
# UART Agent
class UARTAgent(uvm_agent):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.driver = None
        self.sequencer = None
        self.monitor = None
        self.cfg = None

    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(None, "", "cfg", uart_config())
        if not self.cfg:
            self.logger.error("UART config not found_UART_AGENT")
            raise Exception("ConfigError")
        self.monitor = UARTMonitor.create("monitor", self)
        
        if self.cfg.is_active:
            self.driver = UARTDriver.create("driver", self)
            self.sequencer = UARTSequencer.create("sequencer", self)

    def connect_phase(self):
        super().connect_phase()
        if self.cfg.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
