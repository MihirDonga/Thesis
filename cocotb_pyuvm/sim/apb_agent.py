from pyuvm import *
from apb_driver import APBDriver
from apb_monitor import APBMonitor
from apb_sequencer import APBSequencer
from apb_config import apb_config

class APBAgent(uvm_agent):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.driver = None
        self.sequencer = None
        self.monitor = None
        self.apb_cfg = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apb_cfg = ConfigDB().get(None, "", "apb_cfg", apb_config())    
        if not self.apb_cfg:
            self.logger.error("UART config not found_APB_AGENT")
            raise Exception("ConfigError")  
        
        self.monitor = APBMonitor("monitor", self)

        if self.apb_cfg.is_active:
            self.driver = APBDriver("driver", self)
            self.sequencer = APBSequencer("sequencer", self)

    def connect_phase(self, phase):
        super().connect_phase(phase)
        if self.apb_cfg.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
