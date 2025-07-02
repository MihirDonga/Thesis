from pyuvm import *
from apb_driver import APBDriver
from apb_monitor import APBMonitor
from apb_sequencer import APBSequencer

class APBAgent(uvm_agent):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.driver = None
        self.sequencer = None
        self.monitor = None
        self.apb_cfg = None

    def build_phase(self, phase):
        super().build_phase(phase)
        success, self.apb_cfg = ConfigDB().get(self, "", "apb_cfg")
        if not success:
            uvm_fatal("NO_CFG", f"Configuration must be set for: {self.get_full_name()}.apb_cfg")

        self.monitor = APBMonitor.create("monitor", self)

        if self.apb_cfg.is_active:
            self.driver = APBDriver.create("driver", self)
            self.sequencer = APBSequencer.create("sequencer", self)

    def connect_phase(self,phase):
        super().connect_phase(phase)
        if self.apb_cfg.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
