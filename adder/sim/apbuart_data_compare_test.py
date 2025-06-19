from pyuvm import *
from cocotb.triggers import Timer


class apbuart_data_compare_test(apbuart_base_test):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_confg_sq = None
        self.apbuart_transmt_sq = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apbuart_confg_sq = apbuart_config_seq.type_id.create("apbuart_confg_sq", self)
        self.apbuart_transmt_sq = apbuart_singlebeat_seq.type_id.create("apbuart_transmt_sq", self)

    async def run_phase(self, phase):
        for _ in range(self.cfg.loop_time):
            self.set_config_params(9600, 8, 3, 1, 1)  # Baud Rate, Frame Len, Parity, Stop Bit, Randomize Flag
            print("UART Config:")
            print(self.cfg)

            self.set_apbconfig_params(2, 1)  # Slave Bus Address, Randomize Flag
            print("APB Config:")
            print(self.apb_cfg)

            phase.raise_objection(self)
            await self.apbuart_confg_sq.start(self.env_sq.v_sqr)
            await self.apbuart_transmt_sq.start(self.env_sq.v_sqr)
            phase.drop_objection(self)

        # Delay similar to UVM's drain time
        await Timer(75000 * 7, "ns")
