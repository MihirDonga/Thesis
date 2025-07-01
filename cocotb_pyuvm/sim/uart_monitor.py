from pyuvm import *
from cocotb.triggers import RisingEdge, Timer
from uart_transaction import UARTTransaction

class UARTMonitor(uvm_monitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.cfg = None
        self.trans_collected = None
        self.count = 0
        self.count1 = 1
        self.receive_reg = 0
        self.LT = 0
        self.parity_en = False
    
    def build_phase(self, phase):
        super().build_phase(phase)
        
        # Get configuration from config_db
        self.cfg = ConfigDB().get(self, "", "cfg")  
        if not self.cfg:
            self.logger.error("UART config not found")
            raise Exception("ConfigError")
        
        self.dut = ConfigDB().get(self, "", "dut")

        self.item_collected_port_mon = uvm_analysis_port("item_collected_port_mon", self)
        self.trans_collected = UARTTransaction()

    async def run_phase(self):
        while True:
            await RisingEdge(self.dut.PCLK)
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
        self.count = 0

        for i in range(self.LT):
            # Wait for start bit (falling edge)
            while self.dut.Tx.value == 1:
                await RisingEdge(self.dut.PCLK)
            
            # Sample in middle of bit period
            await Timer(self.cfg.baud_rate // 2)     

            # Sample data bits
            for _ in range(self.cfg.frame_len):
                await Timer(self.cfg.baud_rate * self.dut.PCLK.period)
                self.receive_reg = (self.receive_reg << 1) | self.dut.Tx.value
                self.count += 1
            
            # Sample parity bit if enabled
            if self.parity_en:
                await Timer(self.cfg.baud_rate * self.dut.PCLK.period)
                # parity_bit = self.dut.Tx.value
            
            # Sample stop bits
            for _ in range(self.cfg.n_sb + 1):
                await Timer(self.cfg.baud_rate * self.dut.PCLK.period)
                # stop_bit = self.dut.Tx.value
            
            # Store collected data
            self.trans_collected.transmitter_reg = self.receive_reg
            
        # Send transaction to scoreboard
        self.item_collected_port_mon.write(self.trans_collected)
        self.receive_reg = 0  # Reset for next transaction
