from pyuvm import *
from cocotb.triggers import Timer

class apbuart_rec_readreg_test(apbuart_base_test):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.apbuart_confg_sq = None
        self.apbuart_no_err_sq = None
        self.apbuart_part_err_sq = None
        self.apbuart_frm_err_sq = None
        self.apbuart_drv_random_sq = None
        self.apbuart_read_rcv_reg_sq = None
        self.apbuart_transmission_sq = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apbuart_confg_sq = apbuart_config_seq.type_id.create("apbuart_confg_sq", self)
        self.apbuart_no_err_sq = apbuart_NoError_seq.type_id.create("apbuart_no_err_sq", self)
        self.apbuart_part_err_sq = apbuart_parityError_seq.type_id.create("apbuart_part_err_sq", self)
        self.apbuart_frm_err_sq = apbuart_frameError_seq.type_id.create("apbuart_frm_err_sq", self)
        self.apbuart_transmission_sq = apbuart_singlebeat_seq.type_id.create("apbuart_transmission_sq", self)
        self.apbuart_drv_random_sq = apbuart_recdrv_seq.type_id.create("apbuart_drv_random_sq", self)
        self.apbuart_read_rcv_reg_sq = apbuart_recreadreg_seq.type_id.create("apbuart_read_rcv_reg_sq", self)

    async def run_phase(self, phase):
        for _ in range(self.cfg.loop_time):
            self.set_config_params(9600, 7, 3, 1, 1)  # Randomized flag = 1
            print(self.cfg)

            phase.raise_objection(self)

            await self.apbuart_confg_sq.start(self.env_sq.v_sqr)
            await self.apbuart_no_err_sq.start(self.env_sq.v_sqr)
            await self.apbuart_read_rcv_reg_sq.start(self.env_sq.v_sqr)

            await self.apbuart_part_err_sq.start(self.env_sq.v_sqr)
            await self.apbuart_read_rcv_reg_sq.start(self.env_sq.v_sqr)

            await self.apbuart_frm_err_sq.start(self.env_sq.v_sqr)
            await self.apbuart_read_rcv_reg_sq.start(self.env_sq.v_sqr)

            await self.apbuart_drv_random_sq.start(self.env_sq.v_sqr)
            await self.apbuart_read_rcv_reg_sq.start(self.env_sq.v_sqr)

            phase.drop_objection(self)

        await Timer(20, "NS")  # Drain time equivalent
