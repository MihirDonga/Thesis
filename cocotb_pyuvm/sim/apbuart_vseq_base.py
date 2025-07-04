from pyuvm import *
from apb_sequence import *
from uart_sequence import *
import logging
class vseq_base(uvm_sequence):

    def __init__(self, name="vseq_base"):
        super().__init__(name)
        self.apb_sqr = None
        self.uart_sqr = None
        self.logger = logging.getLogger(name)

    async def body(self):
        # First check if we have a virtual sequencer
        print(f"[DEBUG] p_sequencer attribute? {hasattr(self, 'p_sequencer')}")
        print(f"[DEBUG] p_sequencer: {getattr(self, 'p_sequencer', None)}")
        if hasattr(self, "p_sequencer") and self.p_sequencer:
            self.logger.info(f"[VSEQ_BASE] p_sequencer: {self.p_sequencer.get_full_name()}")
            self.apb_sqr = getattr(self.p_sequencer, "apb_sqr", None)
            self.uart_sqr = getattr(self.p_sequencer, "uart_sqr", None)
        else:
            self.logger.error("Virtual sequence not connected to virtual sequencer!")
            raise RuntimeError("Virtual sequence not connected to virtual sequencer!")
class apbuart_config_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = config_apbuart("config_apbuart")
        await apbuart_seq.start(self.apb_sqr)
        # await apbuart_seq.finish_item(self.apb_sqr)
        self.logger.info("Sequence complete")

class apbuart_singlebeat_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = transmit_single_beat("transmit_single_beat")
        await apbuart_seq.start(self.apb_sqr)
        # await apbuart_seq.finish_item(self.apb_sqr)
        self.logger.info("Sequence complete")

class apbuart_recdrv_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = recdrv_test_uart("recdrv_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")

class apbuart_recreadreg_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = rec_reg_test("rec_reg_test")
        await apbuart_seq.start(self.apb_sqr)
        # await apbuart_seq.finish_item(self.apb_sqr)
        self.logger.info("Sequence complete")

class apbuart_frameError_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = fe_test_uart("fe_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")

class apbuart_parityError_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = pe_test_uart("pe_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")

class apbuart_NoError_seq(vseq_base):

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = err_free_test_uart("err_free_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")
