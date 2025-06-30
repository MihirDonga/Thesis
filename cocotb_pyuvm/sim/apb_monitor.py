from pyuvm import *
from cocotb.triggers import RisingEdge

class APBMonitor(uvm_monitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.item_collected_port_mon = None
        self.trans_collected = None

    def build_phase(self):        
        super().build_phase()
        self.item_collected_port_mon = uvm_analysis_port("item_collected_port_mon", self)
        self.dut = ConfigDB().get(self, "", "dut")

    async def run_phase(self):
        while True:
            # Wait for transaction start
            await RisingEdge(self.dut.PCLK)
            if not (self.dut.PSELx.value and self.dut.PENABLE.value):
                continue
            
            # Wait for completion (PREADY or PSLVERR)
            while not (self.dut.PREADY.value or self.dut.PSLVERR.value):
                await RisingEdge(self.dut.PCLK)
            
            # Capture transaction data
            self.trans_collected.PWRITE = bool(self.dut.PWRITE.value)
            self.trans_collected.PWDATA = self.dut.PWDATA.value.integer
            self.trans_collected.PADDR = self.dut.PADDR.value.integer
            self.trans_collected.PRDATA = self.dut.PRDATA.value.integer
            self.trans_collected.PREADY = bool(self.dut.PREADY.value)
            self.trans_collected.PSLVERR = bool(self.dut.PSLVERR.value)
            
            self.logger.debug(f"APB Monitor Collected Transaction:\n{self.trans_collected}")
            
            # Wait for transaction completion
            while self.dut.PREADY.value:
                await RisingEdge(self.dut.PCLK)
            
            # Send to scoreboard
            self.item_collected_port_mon.write(self.trans_collected)
