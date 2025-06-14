from pyuvm import *
from cocotb.triggers import RisingEdge, Timer
import random
from dataclasses import dataclass

@dataclass
class UartCovData:
    transmitter_reg: int = 0
    parity_en: bool = False
    frame_len: int = 8
    n_sb: int = 1

class UartMonitor(uvm_monitor):
    def build_phase(self):
        self.cfg = None
        self.item_collected_port_mon = uvm_analysis_port("item_collected_port_mon", self)
        self.trans_collected = UartTransaction()
        self.count = 0
        self.count1 = 1
        self.receive_reg = 0
        self.LT = 0
        self.parity_en = False
        
        # Get configuration from config_db
        if not uvm_config_db.get(self, "", "cfg", self.cfg):
            self.logger.warning("No configuration found, using defaults")
            
        # Get virtual interface
        if not uvm_config_db.get(self, "", "vif", self.vif):
            self.logger.error("Virtual interface not found!")
            raise Exception("Virtual interface not found")
        
        # Initialize coverage
        self.uart_cov = self.create_coverage()

    def create_coverage(self):
        # Create coverage points using Python coverage library
        # This is a placeholder - actual implementation would use a Python coverage library
        # like coverage.py or implement custom coverage tracking
        class UartCoverage:
            def __init__(self):
                self.coverage_data = {
                    'transmitter_reg': set(),
                    'parity_en': set(),
                    'frame_len': set(),
                    'n_sb': set()
                }
                
            def sample(self, data: UartCovData):
                self.coverage_data['transmitter_reg'].add(data.transmitter_reg)
                self.coverage_data['parity_en'].add(data.parity_en)
                self.coverage_data['frame_len'].add(data.frame_len)
                self.coverage_data['n_sb'].add(data.n_sb)
                
            def get_coverage(self):
                total = 0
                covered = 0
                for key, values in self.coverage_data.items():
                    if key == 'transmitter_reg':
                        # Special bins for transmitter_reg
                        bins = {
                            'all_zero': 0x00000000,
                            'all_ones': 0xFFFFFFFF,
                            'alternating': [0xAAAAAAAA, 0x55555555]
                        }
                        total += len(bins) + 1  # +1 for misc
                        covered += sum(1 for bin_val in bins.values() 
                                    if (isinstance(bin_val, list) and any(v in values for v in bin_val) or
                                    (not isinstance(bin_val, list) and bin_val in values))
                        if len(values) > covered:  # Misc bin
                            covered += 1
                    else:
                        # Simple bins for other coverage points
                        if key == 'parity_en':
                            total = 2
                            covered = len(values)
                        elif key == 'frame_len':
                            total = 5
                            covered = len({v for v in values if 5 <= v <= 9})
                        elif key == 'n_sb':
                            total = 2
                            covered = len(values)
                return (covered / total) * 100 if total > 0 else 0.0
        
        return UartCoverage()

    async def run_phase(self):
        while True:
            await RisingEdge(self.vif.PCLK)
            self.cfg_settings()  # Update configuration settings
            await self.monitor_and_send()

    def cfg_settings(self):
        """Extract parity enable (parity_en) and loop time (LT) from config"""
        if not self.cfg:
            return
            
        self.parity_en = self.cfg.parity[1]
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

    async def monitor_and_send(self):
        cov_data = UartCovData()
        self.count = 0
        self.receive_reg = 0

        for i in range(self.LT):
            # Wait for start bit (falling edge)
            while self.vif.Tx.value == 1:
                await RisingEdge(self.vif.PCLK)
            
            # Sample in middle of bit period
            await Timer(self.cfg.baud_rate * self.vif.PCLK.period / 2)
            
            # Sample data bits
            for _ in range(self.cfg.frame_len):
                await Timer(self.cfg.baud_rate * self.vif.PCLK.period)
                self.receive_reg = (self.receive_reg << 1) | self.vif.Tx.value
                self.count += 1
            
            # Sample parity bit if enabled
            if self.parity_en:
                await Timer(self.cfg.baud_rate * self.vif.PCLK.period)
                # parity_bit = self.vif.Tx.value
            
            # Sample stop bits
            for _ in range(self.cfg.n_sb + 1):
                await Timer(self.cfg.baud_rate * self.vif.PCLK.period)
                # stop_bit = self.vif.Tx.value
            
            # Store collected data
            self.trans_collected.transmitter_reg = self.receive_reg
            
            # Sample coverage
            cov_data.transmitter_reg = self.trans_collected.transmitter_reg
            cov_data.parity_en = self.parity_en
            cov_data.frame_len = self.cfg.frame_len
            cov_data.n_sb = self.cfg.n_sb
            self.uart_cov.sample(cov_data)
        
        # Send transaction to scoreboard
        self.item_collected_port_mon.write(self.trans_collected)
        self.receive_reg = 0  # Reset for next transaction

    def print_coverage_UART_summary(self):
        coverage_percentage = self.uart_cov.get_coverage()
        self.logger.info(f"UART Covergroup coverage: {coverage_percentage:.2f}%")