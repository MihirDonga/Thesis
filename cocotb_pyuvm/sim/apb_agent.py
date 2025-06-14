from pyuvm import *

class APBAgent(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.driver = None
        self.sequencer = None
        self.monitor = None
        self.apb_cfg = None

    def build_phase(self):
        success, self.apb_cfg = ConfigDB().get(self, "", "apb_cfg")
        if not success:
            uvm_fatal("NO_CFG", f"Configuration must be set for: {self.get_full_name()}.apb_cfg")

        self.monitor = APBMonitor("monitor", self)

        if self.apb_cfg.is_active:
            self.driver = APBDriver("driver", self)
            self.sequencer = APBSequencer("sequencer", self)

    def connect_phase(self):
        if self.apb_cfg.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)
