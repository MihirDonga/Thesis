from pyuvm import *
from uart_transaction import *

# ------------------------
# Sequence: Stop Bit Corruption
# ------------------------
class recdrv_test_uart(uvm_sequence):
    def __init__(self, name="recdrv_test_uart"):
        super().__init__(name)
        self.uart_sq = None

    async def body(self):
        uart_sq = UARTTransaction.create("uart_sq")
        uart_sq.sb_corr = 0      # Stop bit corrupted
        uart_sq.bad_parity = 1  # Good parity
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)

# recdrv_test_uart.type_id = UVMFactory().register(recdrv_test_uart)
# ------------------------
# Sequence: Frame Error (Stop bit error only)
# ------------------------
class fe_test_uart(uvm_sequence):
    def __init__(self, name="fe_test_uart"):
        super().__init__(name)
        self.uart_sq = None

    async def body(self):
        uart_sq = UARTTransaction.create("uart_sq")
        uart_sq.sb_corr = 1      # Stop bit corrupted
        uart_sq.bad_parity = 1  # Good parity
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)
# fe_test_uart.type_id = UVMFactory().register(fe_test_uart)

# ------------------------
# Sequence: Parity Error
# ------------------------
class pe_test_uart(uvm_sequence):
    def __init__(self, name="pe_test_uart"):
        super().__init__(name)
        self.uart_sq = None

    async def body(self):
        uart_sq = UARTTransaction.create("uart_sq")
        uart_sq.bad_parity = 1   # Parity error
        uart_sq.sb_corr = 0     # Good stop bit
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)
# pe_test_uart.type_id = UVMFactory().register(pe_test_uart)
# ------------------------
# Sequence: Error-Free
# ------------------------
class err_free_test_uart(uvm_sequence):
    def __init__(self, name="err_free_test_uart"):
        super().__init__(name)
        self.uart_sq = None

    async def body(self):
        uart_sq = UARTTransaction.create("uart_sq")
        uart_sq.bad_parity = 0  # Good parity
        uart_sq.sb_corr = 0     # Good stop bit
        # uart_sq.payload = 0x11223344  # Optional
        await self.start_item(uart_sq)
        await self.finish_item(uart_sq)
# err_free_test_uart.type_id = UVMFactory().register(err_free_test_uart)