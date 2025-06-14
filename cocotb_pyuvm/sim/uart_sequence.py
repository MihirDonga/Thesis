from pyuvm import *

# ------------------------
# UART Transaction Class
# ------------------------
@uvm_object_utils
class UARTTransaction(uvm_sequence_item):
    def __init__(self, name="UARTTransaction"):
        super().__init__(name)
        self.bad_parity = None
        self.sb_corr = None
        # self.payload = None  # Optional

# ------------------------
# Sequence: Stop Bit Corruption
# ------------------------
@uvm_object_utils
class RecDrvTestUART(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction("uart_sq")
        await self.start_item(uart_sq)
        uart_sq.sb_corr = False      # Stop bit corrupted
        uart_sq.bad_parity = True  # Good parity
        await self.finish_item(uart_sq)

# ------------------------
# Sequence: Frame Error (Stop bit error only)
# ------------------------
@uvm_object_utils
class FETestUART(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction("uart_sq")
        await self.start_item(uart_sq)
        uart_sq.sb_corr = True      # Stop bit corrupted
        uart_sq.bad_parity = True  # Good parity
        await self.finish_item(uart_sq)

# ------------------------
# Sequence: Parity Error
# ------------------------
@uvm_object_utils
class PETestUART(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction("uart_sq")
        await self.start_item(uart_sq)
        uart_sq.bad_parity = True   # Parity error
        uart_sq.sb_corr = False     # Good stop bit
        await self.finish_item(uart_sq)

# ------------------------
# Sequence: Error-Free
# ------------------------
@uvm_object_utils
class ErrFreeTestUART(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction("uart_sq")
        await self.start_item(uart_sq)
        uart_sq.bad_parity = False  # Good parity
        uart_sq.sb_corr = False     # Good stop bit
        # uart_sq.payload = 0x11223344  # Optional
        await self.finish_item(uart_sq)
