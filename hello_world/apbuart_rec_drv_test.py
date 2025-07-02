from pyuvm import *

class apbuart_rec_drv_test(apbuart_base_test):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_confg_sq = None
        self.apbuart_drv_sq = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apbuart_confg_sq = apbuart_config_seq.create("apbuart_confg_sq", self)
        self.apbuart_drv_sq = apbuart_recdrv_seq.create("apbuart_drv_sq", self)

    async def run_phase(self, phase):
        for _ in range(1):
            self.set_config_params(9600, 8, 3, 1, 0)  # Randomize flag = 0 (directed)
            print(self.cfg)

            phase.raise_objection(self)

            await self.apbuart_confg_sq.start(self.env_sq.v_sqr)
            await self.apbuart_drv_sq.start(self.env_sq.v_sqr)

            phase.drop_objection(self)

        await Timer(20, "NS")  # Equivalent to set_drain_time
