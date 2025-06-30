from pyuvm import *
from uart_transaction import *
from pyuvm import uvm_object_utils
# ------------------------
# Sequence: Stop Bit Corruption
# ------------------------
@uvm_object_utils
class recdrv_test_uart(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction.type_id.create("uart_sq")
        uart_sq.sb_corr = 0      # Stop bit corrupted
        uart_sq.bad_parity = 1  # Good parity
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)

# ------------------------
# Sequence: Frame Error (Stop bit error only)
# ------------------------
@uvm_object_utils
class fe_test_uart(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction.type_id.create("uart_sq")
        uart_sq.sb_corr = 1      # Stop bit corrupted
        uart_sq.bad_parity = 1  # Good parity
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)

# ------------------------
# Sequence: Parity Error
# ------------------------
@uvm_object_utils
class pe_test_uart(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction.type_id.create("uart_sq")
        uart_sq.bad_parity = 1   # Parity error
        uart_sq.sb_corr = 0     # Good stop bit
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)

# ------------------------
# Sequence: Error-Free
# ------------------------
@uvm_object_utils
class err_free_test_uart(uvm_sequence):
    async def body(self):
        uart_sq = UARTTransaction.type_id.create("uart_sq")
        uart_sq.bad_parity = 0  # Good parity
        uart_sq.sb_corr = 0     # Good stop bit
        # uart_sq.payload = 0x11223344  # Optional
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)
