from pyuvm import *

# Configuration Class
class UARTConfig(uvm_object):
    def __init__(self, name="cfg"):
        super().__init__(name)
        self.driver = None
        self.sequencer = None
        self.monitor = None
        self.cfg = None


# UART Agent
class UARTAgent(uvm_agent):
    def build_phase(self):
        success, self.cfg = ConfigDB().get(self, "", "cfg")
        if not success:
            uvm_fatal("NO_CFG", f"Configuration must be set for: {self.get_full_name()}.cfg")
        
        self.monitor = UARTMonitor("monitor", self)
        
        if self.cfg.is_active:
            self.driver = UARTDriver("driver", self)
            self.sequencer = UARTSequencer("sequencer", self)

    def connect_phase(self):
        if self.cfg.is_active:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)

# Example Test Environment
class UARTEnv(uvm_env):
    def build_phase(self):
        self.agent = UARTAgent("uart_agent", self)
        cfg = UARTConfig()
        ConfigDB().set(self, "uart_agent", "cfg", cfg)