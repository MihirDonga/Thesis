from pyuvm import *

# ---------------------------
# Dummy uart_config Object
# ---------------------------
@uvm_object_utils
class UARTConfig(uvm_object):
    def __init__(self, name="UARTConfig"):
        super().__init__(name)

# ---------------------------
# Dummy apb_transaction
# ---------------------------
@uvm_object_utils
class APBTransaction(uvm_sequence_item):
    def __init__(self, name="APBTransaction"):
        super().__init__(name)
        self.PWRITE = None
        self.PADDR = None

# ---------------------------
# Sequence: ConfigAPBUART
# ---------------------------
@uvm_object_utils
class ConfigAPBUART(uvm_sequence):
    async def body(self):
        cfg = UARTConfig("cfg")

        for addr in [cfg.baud_config_addr,
                     cfg.frame_config_addr,
                     cfg.parity_config_addr,
                     cfg.stop_bits_config_addr]:

            apbuart_sq = APBTransaction("apbuart_sq")
            await self.start_item(apbuart_sq)
            apbuart_sq.PWRITE = True
            apbuart_sq.PADDR = addr
            await self.finish_item(apbuart_sq)

            apbuart_sq = APBTransaction("apbuart_sq")
            await self.start_item(apbuart_sq)
            apbuart_sq.PWRITE = False
            apbuart_sq.PADDR = addr
            await self.finish_item(apbuart_sq)

# ---------------------------
# Sequence: TransmitSingleBeat
# ---------------------------
@uvm_object_utils
class TransmitSingleBeat(uvm_sequence):
    async def body(self):
        cfg = UARTConfig("cfg")
        apbuart_sq = APBTransaction("apbuart_sq")

        await self.start_item(apbuart_sq)
        apbuart_sq.PWRITE = True
        apbuart_sq.PADDR = cfg.trans_data_addr
        await self.finish_item(apbuart_sq)

# ---------------------------
# Sequence: RecRegTest
# ---------------------------
@uvm_object_utils
class RecRegTest(uvm_sequence):
    async def body(self):
        cfg = UARTConfig("cfg")
        apbuart_sq = APBTransaction("apbuart_sq")

        await self.start_item(apbuart_sq)
        apbuart_sq.PWRITE = False
        apbuart_sq.PADDR = cfg.receive_data_addr
        await self.finish_item(apbuart_sq)
