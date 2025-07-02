from pyuvm import *
from uart_transaction import UARTTransaction
from cocotb.triggers import RisingEdge
from uart_config import uart_config

# Python uses __init__ instead of new()
# Type declarations are dynamic in Python

class UARTDriver(uvm_driver):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = cocotb.top
        self.cfg = None
        self.item_collected_port_drv = None
        self.trans_collected = None
        self.LT = 0  # Line Type
        
    def build_phase(self, phase):
        super().build_phase(phase)
        # Get configuration from config_db
        self.cfg = ConfigDB().get(None, "", "cfg", uart_config())
        self.dut = ConfigDB().get(None, "", "dut", cocotb.top)        
        if not self.cfg:
            self.logger.error("UART config not found")
            raise Exception("ConfigError")
        if not self.dut:
            self.logger.error("UART dut not found")
            raise Exception("dut_error")
        
        # uvm_config_db becomes ConfigDB in PyUVM
        # uvm_fatal becomes logger.error + exception
        # Port creation syntax is similar but Python-style   
        
        self.item_collected_port_drv = uvm_analysis_port("item_collected_port_drv", self)
        self.trans_collected = UARTTransaction()

    async def run_phase(self, phase):
        super().run_phase(phase)
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
            self.dut.RX.value = 1
            
            # Wait for reset to be inactive
            await RisingEdge(self.dut.PCLK)
            if not self.dut.PRESETn.value:
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
                    await RisingEdge(self.dut.PCLK)
                
                if no_bits_sent == 0:
                    # Send start bit
                    self.dut.RX.value = req.start_bit
                    no_bits_sent += 1
                elif (no_bits_sent > 0) and (no_bits_sent < (1 + self.cfg.frame_len)):
                    # Send data bits
                    bit_pos = pay_offset + (no_bits_sent - 1)
                    self.dut.RX.value = req.payld_func[bit_pos]
                    self.logger.debug(f"Driver Sending Data bits: {req.payld_func[bit_pos]}")
                    no_bits_sent += 1
                elif (no_bits_sent == (1 + self.cfg.frame_len)) and self.cfg.parity[1]:
                    # Send parity bit
                    self.dut.RX.value = temp[parity_of_frame]
                    parity_of_frame += 1
                    no_bits_sent += 1
                else:
                    # Send stop bits
                    for j in range(self.cfg.n_sb + 1):
                        if j == 1:
                            for _ in range(self.cfg.baud_rate):
                                await RisingEdge(self.dut.PCLK)
                        
                        if req.sb_corr and req.sb_corr_bit[j] and req.sb_corr_frame[i]:
                            # Corrupt stop bit
                            self.dut.RX.value = 0
                            no_bits_sent += 1
                            self.logger.debug(f"Driver intentionally corrupting Stop bit since error_bits[{j}] is {req.sb_corr}")
                        else:
                            # Send correct stop bit
                            self.vdutif.RX.value = req.stop_bits[j]
                            self.logger.debug(f"Driver Sending Frame Stop bit#{j}: {req.stop_bits[j]}")
                            no_bits_sent += 1
            
            pay_offset += self.cfg.frame_len
            no_bits_sent = 0
        
        # Return to idle state
        for _ in range(self.cfg.baud_rate):
            await RisingEdge(self.dut.PCLK)
        self.dut.RX.value = 1