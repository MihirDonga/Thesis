from pyuvm import *

class apbuart_config_test(apbuart_base_test):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_confg_sq = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apbuart_confg_sq = apbuart_config_seq.type_id.create("apbuart_confg_sq", self)

    async def run_phase(self, phase):
        # Raise objection before running test
        for _ in range(self.cfg.loop_time):
            # Apply random config
            self.set_config_params(9600, 8, 3, 1, 1)  # Randomize enabled
            print(self.cfg)

            self.set_apbconfig_params(2, 1)  # Randomize APB address
            print(self.apb_cfg)

            phase.raise_objection(self)

            await self.apbuart_confg_sq.start(self.env_sq.v_sqr)

            phase.drop_objection(self)

        await Timer(20, "NS")  # Equivalent to phase_done.set_drain_time
