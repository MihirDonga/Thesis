from pyuvm import *
from cocotb.triggers import Timer


class apbuart_free_error_test(apbuart_base_test):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_no_err_sq = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apbuart_no_err_sq = apbuart_NoError_seq.create("apbuart_no_err_sq", self)

    async def run_phase(self, phase):
        for _ in range(self.cfg.loop_time):
            self.set_config_params(9600, 8, 3, 1, 1)  # Baud Rate, Frame Len, Parity, Stop Bit, Randomize=1
            print(self.cfg)

            phase.raise_objection(self)
            await self.apbuart_no_err_sq.start(self.env_sq.v_sqr)
            phase.drop_objection(self)

        await Timer(20, "ns")  # Equivalent of drain time
