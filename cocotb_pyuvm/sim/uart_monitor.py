from pyuvm import *
from cocotb.triggers import RisingEdge, Timer
from uart_transaction import UARTTransaction
from uart_config import uart_config

class UARTMonitor(uvm_monitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = None
        self.cfg = None
        self.trans_collected = None
        self.count = 0
        self.count1 = 1
        self.receive_reg = 0
        self.LT = 0
        self.parity_en = 0
    
    def build_phase(self):
        super().build_phase()
        
        # Get configuration from config_db
        self.cfg = ConfigDB().get(None, "", "cfg", uart_config())        
        if self.cfg is None:
            self.logger.error("UART config not found UART_Monitor")
            raise Exception("ConfigError UART_Monitor")
        
        self.dut = ConfigDB().get(self, "", "dut",cocotb.top)
        if self.dut is None:
            self.logger.error("UART dut not found UART_Monitor")
            raise Exception("dut error UART_Monitor")
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
        for _ in range(self.LT):
            # Wait for falling edge on Tx (start bit)
            while int(self.dut.Tx.value) == 1:
                await RisingEdge(self.dut.PCLK)

            bit_time_ns = int(1e9 / self.cfg.bRate)

            # Mid-bit sample for start bit alignment
            await Timer(bit_time_ns // 2, units='ns')

            reg = 0
            for bit_idx in range(self.cfg.frame_len):
                await Timer(bit_time_ns, units='ns')
                bit_val = int(self.dut.Tx.value)
                reg = (reg >> 1) | (bit_val << (self.cfg.frame_len - 1))

            if self.parity_en:
                await Timer(bit_time_ns, units='ns')  # Parity bit

            for _ in range(self.cfg.n_sb):
                await Timer(bit_time_ns, units='ns')
                if int(self.dut.Tx.value) != 1:
                    self.logger.warning("Stop bit error detected")
            
            # Store collected data
            txn = UARTTransaction()
            txn.transmitter_reg = reg
            self.item_collected_port_mon.write(txn)            
        # Send transaction to scoreboard
        self.item_collected_port_mon.write(self.trans_collected)
        self.receive_reg = 0  # Reset for next transaction
