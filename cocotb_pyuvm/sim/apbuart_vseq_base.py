from pyuvm import *
from apb_sequence import *
from uart_sequence import *
from apbuart_environment import *
import logging
class vseq_base(uvm_sequence):

    def __init__(self, name="vseq_base"):
        super().__init__(name)
        self.apb_sqr = None
        self.uart_sqr = None

    async def body(self):
        # First check if we have a virtual sequencer
            self.apb_sqr = self.env_sq.v_sqr.apbuart_sq
            self.uart_sqr = self.seqr.uart_sqr.v_sqr.uart_sq

class apbuart_config_seq(vseq_base):
    # def __init__(self, name="apbuart_config_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        print(f"[DEBUG][apbuart_config_seq] p_sequencer after super().body(): {self.p_sequencer}")
        self.logger.info("Executing sequence")
        apbuart_seq = config_apbuart.create("config_apbuart")
        await apbuart_seq.start(self.apb_sqr)
        await apbuart_seq.finish_item(self.apb_sqr)
        self.logger.info("Sequence complete")

class apbuart_singlebeat_seq(vseq_base):
    # def __init__(self, name="apbuart_singlebeat_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = transmit_single_beat.create("transmit_single_beat")
        await apbuart_seq.start(self.apb_sqr)
        # await apbuart_seq.finish_item(self.apb_sqr)
        self.logger.info("Sequence complete")

class apbuart_recdrv_seq(vseq_base):
    # def __init__(self, name="apbuart_recdrv_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = recdrv_test_uart.create("recdrv_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")

class apbuart_recreadreg_seq(vseq_base):
    # def __init__(self, name="apbuart_recreadreg_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = rec_reg_test.create("rec_reg_test")
        await apbuart_seq.start(self.apb_sqr)
        # await apbuart_seq.finish_item(self.apb_sqr)
        self.logger.info("Sequence complete")

class apbuart_frameError_seq(vseq_base):
    # def __init__(self, name="apbuart_frameError_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = fe_test_uart.create("fe_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")

class apbuart_parityError_seq(vseq_base):
    # def __init__(self, name="apbuart_parityError_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = pe_test_uart.create("pe_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")

class apbuart_NoError_seq(vseq_base):
    # def __init__(self, name="apbuart_NoError_seq"):
    #     super().__init__(name)

    async def body(self):
        await super().body()
        self.logger.info("Executing sequence")
        apbuart_seq = err_free_test_uart.create("err_free_test_uart")
        await apbuart_seq.start(self.uart_sqr)
        # await apbuart_seq.finish_item(self.uart_sqr)
        self.logger.info("Sequence complete")
