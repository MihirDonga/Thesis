from pyuvm import *
from cocotb.triggers import Timer
from apbuart_base_test import apbuart_base_test
from apbuart_vseq_base import apbuart_config_seq

class apbuart_config_test(apbuart_base_test):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_config_sq = None

    def build_phase(self):
        # uvm_factory().set_inst_override_by_type(apbuart_base_test,apbuart_config_test)
        print(f"Entering build_phase for {self.get_name()}")
        super().build_phase()
        self.apbuart_config_sq = apbuart_config_seq.create("apbuart_config_sq")
        if not self.apbuart_config_sq:
            raise Exception("Failed to create apbuart_config_seq from factory")

    async def run_phase(self):
        super().run_phase()
        for _ in range(self.cfg.loop_time):
            self.set_config_params(9600, 8, 3, 1, 1)  # Baud Rate, Frame Len, Parity, Stop Bit, Randomize Flag
            self.logger.info(f"UART Config:\n{self.cfg}")       #prints __str__ from uart_config

            self.set_apbconfig_params(2, 1)  # Slave Bus Address, Randomize Flag
            self.logger.info(f"APB Config:\n{self.apb_cfg}")    #prints __str__ from apb_config

            self.raise_objection()
            print(f"[DEBUG] v_sqr type: {type(self.env_sq.v_sqr)}")
            print(f"[DEBUG] is uvm_sequencer? {isinstance(self.env_sq.v_sqr, uvm_sequencer)}")
            await self.apbuart_config_sq.start(self.env_sq.v_sqr)
            self.drop_objection()

        # Wait 20 time units after dropping objection before test finishes
        await Timer(20, "ns")
