from pyuvm import *
from cocotb.triggers import RisingEdge

class APBDriver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.cfg = None
        self.apb_cfg = None

    def build_phase(self, phase):
        super().build_phase(phase)
        # Get configurations from config_db
        self.cfg = ConfigDB().get(self, "", "cfg")
        self.apb_cfg = ConfigDB().get(self, "", "apb_cfg")
        self.dut = ConfigDB().get(self, "", "dut")
        
        if not self.cfg:
            self.logger.error("UART config not found")
            raise Exception("ConfigError")
        if not self.apb_cfg:
            self.logger.error("APB config not found")
            raise Exception("APBConfigError")
        if self.dut is None:
            self.logger.error("DUT handle not found in ConfigDB")
            raise Exception("dut")
        
    async def run_phase(self,phase):
        super().run_phase(phase)
        while True:
            # Wait for clock edge and reset to be inactive
            await RisingEdge(self.dut.PCLK)
            if not self.dut.PRESETn.value:
                continue
                
            # Initialize signals
            self.dut.PSELx.value = 0
            self.dut.PENABLE.value = 0
            self.dut.PWRITE.value = 0
            self.dut.PWDATA.value = 0
            self.dut.PADDR.value = 0
            
            # Get transaction from sequencer
            req = await self.seq_item_port.get_next_item()
            
            # Drive the transaction
            await self.drive(req)
            
            self.logger.debug(f"APB Finished Driving Transfer:\n{req}")
            self.seq_item_port.item_done()

    async def drive(self, req):
        # Phase 1: Setup phase
        self.dut.PSELx.value = self.apb_cfg.psel_Index
        self.dut.PWRITE.value = req.PWRITE
        self.dut.PADDR.value = req.PADDR
        
        # Handle special register writes
        if req.PADDR == self.cfg.baud_config_addr:
            self.dut.PWDATA.value = self.cfg.bRate
        elif req.PADDR == self.cfg.frame_config_addr:
            self.dut.PWDATA.value = self.cfg.frame_len
        elif req.PADDR == self.cfg.parity_config_addr:
            self.dut.PWDATA.value = self.cfg.parity
        elif req.PADDR == self.cfg.stop_bits_config_addr:
            self.dut.PWDATA.value = self.cfg.n_sb
        else:
            self.dut.PWDATA.value = req.PWDATA
        
        # Wait for next clock edge (Phase 2: Enable phase)
        await RisingEdge(self.dut.PCLK)
        self.dut.PENABLE.value = 1
        
        # Wait for PREADY
        while not self.dut.PREADY.value:
            await RisingEdge(self.dut.PCLK)
        
        # Transaction complete
        self.dut.PSELx.value = 0
        self.dut.PENABLE.value = 0
        
        # Wait for PREADY to go low
        while self.dut.PREADY.value:
            await RisingEdge(self.dut.PCLK)
    # PCLK    __|--|__|--|__|--|__|--|__
    # PSELx   0    1    1    0    0
    # PENABLE 0    0    1    0    0
    # PREADY  X    X    0    1    0