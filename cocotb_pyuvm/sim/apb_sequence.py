from pyuvm import *
from apb_transaction import APBTransaction
from uart_config import uart_config
# ---------------------------
# Sequence: ConfigAPBUART
# ---------------------------
class config_apbuart(uvm_sequence):
    def __init__(self, name="config_apbuart"):
        super().__init__(name)
        self.cfg = None
    async def body(self):
        cfg = uart_config("cfg")

        for addr in [cfg.baud_config_addr,
                     cfg.frame_config_addr,
                     cfg.parity_config_addr,
                     cfg.stop_bits_config_addr]:

            apbuart_sq = APBTransaction("apbuart_sq")
            await self.start_item(apbuart_sq)
            apbuart_sq.PWRITE = 1
            apbuart_sq.PADDR = addr
            await self.finish_item(apbuart_sq)

            apbuart_sq = APBTransaction("apbuart_sq")
            await self.start_item(apbuart_sq)
            apbuart_sq.PWRITE = 0
            apbuart_sq.PADDR = addr
            await self.finish_item(apbuart_sq)

# ---------------------------
# Sequence: TransmitSingleBeat
# ---------------------------
class transmit_single_beat(uvm_sequence):
    def __init__(self, name="transmit_single_beat"):
        super().__init__(name)

    async def body(self):
        cfg = uart_config("cfg")
        apbuart_sq = APBTransaction("apbuart_sq")

        await self.start_item(apbuart_sq)
        apbuart_sq.PWRITE = 1
        apbuart_sq.PADDR = cfg.trans_data_addr
        await self.finish_item(apbuart_sq)

# ---------------------------
# Sequence: RecRegTest
# ---------------------------
class rec_reg_test(uvm_sequence):
    def __init__(self, name="rec_reg_test"):
        super().__init__(name)

    async def body(self):
        cfg = uart_config("cfg")
        apbuart_sq = APBTransaction("apbuart_sq")

        await self.start_item(apbuart_sq)
        apbuart_sq.PWRITE = 0
        apbuart_sq.PADDR = cfg.receive_data_addr
        await self.finish_item(apbuart_sq)
