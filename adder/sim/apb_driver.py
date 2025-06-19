from pyuvm import *
from cocotb.triggers import RisingEdge

class APBTransaction(uvm_sequence_item):
    def __init__(self, name="APBTransaction"):
        super().__init__(name)
      
class APBConfig(uvm_object):
    def __init__(self, name="APBConfig"):
        super().__init__(name)
        

class UARTConfig(uvm_object):
    def __init__(self, name="UARTConfig"):
        super().__init__(name)

class APBDriver(uvm_driver):
    def build_phase(self):
        self.cfg = UARTConfig()
        self.apb_cfg = APBConfig()
        
        # Get configurations from config_db
        if not uvm_config_db.get(self, "", "cfg", self.cfg):
            self.logger.warning("No UART config found, using defaults")
        if not uvm_config_db.get(self, "", "apb_cfg", self.apb_cfg):
            self.logger.warning("No APB config found, using defaults")
            
        # Get virtual interface
        if not uvm_config_db.get(self, "", "vif", self.vif):
            self.logger.error("Virtual interface not found!")
            raise Exception("Virtual interface not found")

    async def run_phase(self):
        while True:
            # Wait for clock edge and reset to be inactive
            await RisingEdge(self.vif.PCLK)
            if not self.vif.PRESETn.value:
                continue
                
            # Initialize signals
            self.vif.PSELx.value = 0
            self.vif.PENABLE.value = 0
            self.vif.PWRITE.value = 0
            self.vif.PWDATA.value = 0
            self.vif.PADDR.value = 0
            
            # Get transaction from sequencer
            req = await self.seq_item_port.get_next_item()
            
            # Drive the transaction
            await self.drive(req)
            
            self.logger.debug(f"APB Finished Driving Transfer:\n{req}")
            self.seq_item_port.item_done()

    async def drive(self, req):
        # Phase 1: Setup phase
        self.vif.PSELx.value = self.apb_cfg.psel_Index
        self.vif.PWRITE.value = req.PWRITE
        self.vif.PADDR.value = req.PADDR
        
        # Handle special register writes
        if req.PADDR == self.cfg.baud_config_addr:
            self.vif.PWDATA.value = self.cfg.bRate
        elif req.PADDR == self.cfg.frame_config_addr:
            self.vif.PWDATA.value = self.cfg.frame_len
        elif req.PADDR == self.cfg.parity_config_addr:
            self.vif.PWDATA.value = self.cfg.parity
        elif req.PADDR == self.cfg.stop_bits_config_addr:
            self.vif.PWDATA.value = self.cfg.n_sb
        else:
            self.vif.PWDATA.value = req.PWDATA
        
        # Wait for next clock edge (Phase 2: Enable phase)
        await RisingEdge(self.vif.PCLK)
        self.vif.PENABLE.value = 1
        
        # Wait for PREADY
        while not self.vif.PREADY.value:
            await RisingEdge(self.vif.PCLK)
        
        # Transaction complete
        self.vif.PSELx.value = 0
        self.vif.PENABLE.value = 0
        
        # Wait for PREADY to go low
        while self.vif.PREADY.value:
            await RisingEdge(self.vif.PCLK)