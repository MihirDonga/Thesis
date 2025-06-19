from pyuvm import *
from cocotb.triggers import RisingEdge, Timer
import random

class UartTransaction(uvm_sequence_item):
    def __init__(self, name="UartTransaction"):
        super().__init__(name)
        self.payload = 0
        self.bad_parity = False
        self.sb_corr = False
        self.sb_corr_bit = 0
        self.start_bit = 0
        self.stop_bits = [1, 1]  # Default two stop bits
        self.payld_func = []
        
    def calc_parity(self, payload, frame_len, bad_parity, parity_type, bad_parity_frame):
        # Implement your parity calculation logic here
        return 0  # Return calculated parity bits

class UartConfig(uvm_object):
    def __init__(self, name="UartConfig"):
        super().__init__(name)
        self.frame_len = 8  # Default 8-bit frame
        self.baud_rate = 1  # Default baud rate (in clock cycles)
        self.parity = [0, 0]  # [type, enable]
        self.n_sb = 1  # Number of stop bits (1 or 2)

class UartDriver(uvm_driver):
    def build_phase(self):
        self.cfg = UartConfig()
        self.item_collected_port_drv = uvm_analysis_port("item_collected_port_drv", self)
        self.trans_collected = UartTransaction()
        self.LT = 0  # Line Type
        
        # Get configuration from config_db
        if not uvm_config_db.get(self, "", "cfg", self.cfg):
            self.logger.warning("No configuration found, using defaults")
            
        # Get virtual interface
        if not uvm_config_db.get(self, "", "vif", self.vif):
            self.logger.error("Virtual interface not found!")
            raise Exception("Virtual interface not found")

    async def run_phase(self):
        await self.get_and_drive()

    def cfg_settings(self):
        # For payload 32 bits we have LT =7. Calculation : 32 ÷ 5 = 6.4 → 7
        if self.cfg.frame_len == 5:
            self.LT = 7
        elif self.cfg.frame_len == 6:
            self.LT = 6
        elif self.cfg.frame_len == 7:
            self.LT = 5
        elif self.cfg.frame_len == 8:
            self.LT = 4
        elif self.cfg.frame_len == 9:
            self.LT = 4
        else:
            self.logger.error("Incorrect frame length selected")

    async def get_and_drive(self):
        while True:
            # Set RX to idle state
            self.vif.RX.value = 1
            
            # Wait for reset to be inactive
            await RisingEdge(self.vif.PCLK)
            if not self.vif.PRESETn.value:
                continue
                
            # Get transaction from sequencer
            req = await self.seq_item_port.get_next_item()
            
            # Store collected transaction
            self.trans_collected.payload = req.payload
            self.trans_collected.bad_parity = req.bad_parity
            self.trans_collected.sb_corr = req.sb_corr
            self.trans_collected.sb_corr_bit = req.sb_corr_bit
            
            # Configure settings
            self.cfg_settings()
            
            # Drive the transaction
            await self.drive_rx(req)
            
            # Send collected transaction
            self.item_collected_port_drv.write(self.trans_collected)
            
            # Complete the transaction
            self.seq_item_port.item_done()

    async def drive_rx(self, req):
        # Transmitter Model
        no_bits_sent = 0
        pay_offset = 0
        parity_of_frame = 0
        temp = req.calc_parity(req.payload, self.cfg.frame_len, 
                             req.bad_parity, self.cfg.parity[0], 
                             req.bad_parity_frame)
        
        for i in range(self.LT):
            while no_bits_sent < (1 + self.cfg.frame_len + self.cfg.parity[1] + (self.cfg.n_sb + 1)):
                # Wait for baud rate period
                for _ in range(self.cfg.baud_rate):
                    await RisingEdge(self.vif.PCLK)
                
                if no_bits_sent == 0:
                    # Send start bit
                    self.vif.RX.value = req.start_bit
                    no_bits_sent += 1
                elif (no_bits_sent > 0) and (no_bits_sent < (1 + self.cfg.frame_len)):
                    # Send data bits
                    bit_pos = pay_offset + (no_bits_sent - 1)
                    self.vif.RX.value = req.payld_func[bit_pos]
                    self.logger.debug(f"Driver Sending Data bits: {req.payld_func[bit_pos]}")
                    no_bits_sent += 1
                elif (no_bits_sent == (1 + self.cfg.frame_len)) and self.cfg.parity[1]:
                    # Send parity bit
                    self.vif.RX.value = temp[parity_of_frame]
                    parity_of_frame += 1
                    no_bits_sent += 1
                else:
                    # Send stop bits
                    for j in range(self.cfg.n_sb + 1):
                        if j == 1:
                            for _ in range(self.cfg.baud_rate):
                                await RisingEdge(self.vif.PCLK)
                        
                        if req.sb_corr and req.sb_corr_bit[j] and req.sb_corr_frame[i]:
                            # Corrupt stop bit
                            self.vif.RX.value = 0
                            no_bits_sent += 1
                            self.logger.debug(f"Driver intentionally corrupting Stop bit since error_bits[{j}] is {req.sb_corr}")
                        else:
                            # Send correct stop bit
                            self.vif.RX.value = req.stop_bits[j]
                            self.logger.debug(f"Driver Sending Frame Stop bit#{j}: {req.stop_bits[j]}")
                            no_bits_sent += 1
            
            pay_offset += self.cfg.frame_len
            no_bits_sent = 0
        
        # Return to idle state
        for _ in range(self.cfg.baud_rate):
            await RisingEdge(self.vif.PCLK)
        self.vif.RX.value = 1