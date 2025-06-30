from pyuvm import *
from cocotb.triggers import Timer
import apbuart_base_test
from apbuart_vseq_base import apbuart_config_seq
class apbuart_config_test(apbuart_base_test):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_config_sq = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apbuart_config_sq = apbuart_config_seq.type_id.create("apbuart_config_sq")

    async def run_phase(self, phase):
        for _ in range(self.cfg.loop_time):
            self.set_config_params(9600, 8, 3, 1, 1)  # Baud Rate, Frame Len, Parity, Stop Bit, Randomize Flag
            self.logger.info(f"UART Config:\n{self.cfg}")       #prints __str__ from uart_config

            self.set_apbconfig_params(2, 1)  # Slave Bus Address, Randomize Flag
            self.logger.info(f"APB Config:\n{self.apb_cfg}")    #prints __str__ from apb_config

            phase.raise_objection(self)
            await self.apbuart_config_sq.start(self.env_sq.v_sqr)
            phase.drop_objection(self)

        # Wait 20 time units after dropping objection before test finishes
        await Timer(20, "ns")
uvm_component_utils(apbuart_config_test)