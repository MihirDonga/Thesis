from pyuvm import *
from cocotb.triggers import RisingEdge
from uart_config import uart_config
from apb_config import apb_config

class APBDriver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None
        self.cfg = None
        self.apb_cfg = None

    def build_phase(self):
        super().build_phase()
        # Get configurations from config_db
        self.cfg = ConfigDB().get(None, "", "cfg", uart_config())
        self.apb_cfg = ConfigDB().get(None, "", "apb_cfg", apb_config())
        self.dut = ConfigDB().get(None, "", "dut", cocotb.top)
        
        if self.cfg is None:
            self.logger.error("UART config not found APB_Driver")
            raise Exception("ConfigError APB_Driver")
        if self.apb_cfg is None:
            self.logger.error("APB config not found APB_Driver")
            raise Exception("APBConfigError APB_Driver")
        if self.dut is None:
            self.logger.error("DUT handle not found in ConfigDB APB_Driver")
            raise Exception("dut APB_Driver")
        
    async def run_phase(self):
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