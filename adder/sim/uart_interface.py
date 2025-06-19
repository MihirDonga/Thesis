from cocotb.triggers import RisingEdge

class UartInterface:
    """Python implementation of UART interface with modport-like functionality"""
    
    def __init__(self, dut, clock_name="PCLK", reset_name="PRESETn"):
        self.dut = dut
        self.clock = getattr(dut, clock_name)
        self.reset = getattr(dut, reset_name)
        
        # UART signals
        self.Tx = dut.Tx
        self.RX = dut.RX
    
    async def wait_clock(self):
        """Wait for rising edge of clock"""
        await RisingEdge(self.clock)

    # Modport-like functionality through separate classes
    class DriverModport:
        """Provides driver view of the interface (like SV modport DRIVER)"""
        def __init__(self, uart_if):
            self.uart_if = uart_if
        
        async def send_bit(self, value):
            """Drive RX signal"""
            self.uart_if.RX.value = value
            await self.uart_if.wait_clock()
        
        def get_clock(self):
            return self.uart_if.clock
        
        def get_reset(self):
            return self.uart_if.reset

    class MonitorModport:
        """Provides monitor view of the interface (like SV modport MONITOR)"""
        def __init__(self, uart_if):
            self.uart_if = uart_if
        
        async def sample_tx(self):
            """Sample Tx signal"""
            await self.uart_if.wait_clock()
            return self.uart_if.Tx.value
        
        def get_clock(self):
            return self.uart_if.clock
        
        def get_reset(self):
            return self.uart_if.reset
        
from pyuvm import uvm_driver
from uart_interface import UartInterface

#                               ````For  uart driver ````

# class UartDriver(uvm_driver):
#     def build_phase(self):
#         self.if_driver = UartInterface.DriverModport(self.cdb.get("uart_if"))
    
#     async def run_phase(self):
#         while True:
#             item = await self.seq_item_port.get_next_item()
#             await self.if_driver.send_bit(item.RX)
#             self.seq_item_port.item_done()

# from pyuvm import uvm_monitor
# from uart_interface import UartInterface


#                                ````For  uart monitor ````

# class UartMonitor(uvm_monitor):
#     def build_phase(self):
#         self.if_monitor = UartInterface.MonitorModport(self.cdb.get("uart_if"))
#         self.ap = uvm_analysis_port("ap", self)
    
#     async def run_phase(self):
#         while True:
#             tx_value = await self.if_monitor.sample_tx()
#             # Create and send transaction
#             tr = UartTransaction()
#             tr.Tx = tx_value
#             self.ap.write(tr)