from pyuvm import *
from cocotb.triggers import RisingEdge
from apb_transaction import*
class APBMonitor(uvm_monitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None
        self.item_collected_port_mon = None
        self.trans_collected = None

    def build_phase(self):
        super().build_phase()
        self.item_collected_port_mon = uvm_analysis_port("item_collected_port_mon", self)
        self.dut = ConfigDB().get(None, "", "dut", cocotb.top)
        self.logger.info(f"DUT found: {self.dut}")
        if self.dut is None:
            self.logger.error("DUT handle not found APB_Monitor")
            raise Exception("DUTError APB_Monitor")
        
    # ✅ Safe conversion helper
    def safe_int(self, signal_val, default=0):
        val_str = str(signal_val)
        if any(ch in val_str for ch in ('x', 'z', '?')):
            return default
        return signal_val.integer
    
    async def run_phase(self):
        while True:
            # Wait for transaction start
            await RisingEdge(self.dut.PCLK)
            if not (self.dut.PSELx.value and self.dut.PENABLE.value):
                continue
            
            # Wait for completion (PREADY or PSLVERR)
            while not (self.dut.PREADY.value or self.dut.PSLVERR.value):
                await RisingEdge(self.dut.PCLK)
            self.trans_collected = APBTransaction()

            # Capture transaction data
            self.trans_collected.PWRITE = bool(self.dut.PWRITE.value)
            self.trans_collected.PWDATA = self.safe_int(self.dut.PWDATA.value)
            self.trans_collected.PADDR = self.safe_int(self.dut.PWDATA.value)
            self.trans_collected.PRDATA = self.safe_int(self.dut.PWDATA.value)
            self.trans_collected.PREADY = bool(self.dut.PREADY.value)
            self.trans_collected.PSLVERR = bool(self.dut.PSLVERR.value)
            
            self.logger.debug(f"APB Monitor Collected Transaction:\n{self.trans_collected}")
            
            # Send to scoreboard
            self.item_collected_port_mon.write(self.trans_collected)

            # Wait for transaction completion
            while self.dut.PREADY.value:
                await RisingEdge(self.dut.PCLK)
            
