import pyuvm
from pyuvm import *
from uart_config import uart_config
from apb_config import apb_config
from apbuart_environment import APBUARTEnv
from cocotb.triggers import Timer
from apbuart_vseq_base import apbuart_config_seq

# @pyuvm.test()
class apbuart_base_test(uvm_test):
    def __init__(self, name="apbuart_base_test", parent=None):
        super().__init__(name, parent)
        self.env_sq = None
        self.cfg = uart_config()
        self.apb_cfg = apb_config()
        self.error_count = 0  # Manual error counter

    def build_phase(self, phase):
        super().build_phase(phase)
        self.logger.info(f"{self.get_name()} - Inside build_phase")
        
        # uvm_component, uvm_env, uvm_agent, scoreboard, sequencer	Yes (standard way)
        # uvm_sequence	hsas No, instantiate directly via constructor
        self.env_sq =  APBUARTEnv("env_sq",self) 

        ConfigDB().set(None, "*", "cfg", self.cfg)
        self.set_config_params(9600, 8, 3, 1, 0)

        ConfigDB().set(None, "*", "apb_cfg", self.apb_cfg)        
        self.set_apbconfig_params(2, 0)

    def set_config_params(self, bd_rate, frm_len, parity, sb, flag):
        if flag:
            self.cfg.randomize()
        else:
            self.cfg.frame_len = frm_len
            self.cfg.n_sb = sb
            self.cfg.parity = parity
            self.cfg.bRate = bd_rate
            self.cfg.baudRateFunc()

        self.logger.info(f"{self.get_name()} - UART Config after set_config_params:\n{self.cfg}")

    def set_apbconfig_params(self, addr, flag):
        if flag:
            self.apb_cfg.randomize()
        else:
            self.apb_cfg.slave_Addr = addr
            self.apb_cfg.AddrCalcFunc()

        self.logger.info(f"{self.get_name()} - APB Config after set_apbconfig_params:\n{self.apb_cfg}")

    def report_error(self, msg):
        self.logger.error(msg)
        self.error_count += 1

    # def end_of_elaboration_phase(self, phase):
    #     super().end_of_elaboration_phase(phase)
    #     self.print_obj()

    def report_phase(self, phase):
        super().report_phase(phase)

        if self.error_count> 0:
            self.logger.critical(f"{self.get_name()} - -" * 39)
            self.logger.critical(f"{self.get_name()} - ----            TEST FAIL          ----")
            self.logger.critical(f"{self.get_name()} - -" * 39)
        else:
            self.logger.critical(f"{self.get_name()} - -" * 39)
            self.logger.critical(f"{self.get_name()} - ----           TEST PASS           ----")
            self.logger.critical(f"{self.get_name()} - -" * 39)

@pyuvm.test()
# class apbuart_config_test(apbuart_base_test):

#     def __init__(self, name, parent=None):
#         super().__init__(name, parent)
#         self.apbuart_config_sq = None

#     def build_phase(self, phase):
#         # uvm_factory().set_inst_override_by_type(apbuart_base_test,apbuart_config_test)
#         print(f"Entering build_phase for {self.get_name()}")
#         super().build_phase(phase)
#         self.apbuart_config_sq = apbuart_config_seq.create("apbuart_config_sq")
#         if self.apbuart_config_sq is None:
#             raise Exception("Failed to create apbuart_config_seq from factory")

#     async def run_phase(self, phase):
#         for _ in range(self.cfg.loop_time):
#             self.set_config_params(9600, 8, 3, 1, 1)  # Baud Rate, Frame Len, Parity, Stop Bit, Randomize Flag
#             self.logger.info(f"UART Config:\n{self.cfg}")       #prints __str__ from uart_config

#             self.set_apbconfig_params(2, 1)  # Slave Bus Address, Randomize Flag
#             self.logger.info(f"APB Config:\n{self.apb_cfg}")    #prints __str__ from apb_config

#             phase.raise_objection(self)
#             await self.apbuart_config_sq.start(self.env_sq.v_sqr)
#             phase.drop_objection(self)

#         # Wait 20 time units after dropping objection before test finishes
#         await Timer(20, "ns")
@pyuvm.test()
class apbuart_config_test(apbuart_base_test):
    """APBUART configuration test"""

    async def run_phase(self, phase):
        phase.raise_objection(self)
        
        try:
            # Run configuration sequence multiple times
            for _ in range(self.cfg.loop_time):
                # Randomize configurations
                self._set_uart_config(9600, 8, 3, 1, randomize=True)
                self._set_apb_config(2, randomize=True)
                
                # Execute configuration sequence
                seq = apbuart_config_seq("apbuart_config_seq")
                await seq.start(self.env_sq.v_sqr)
                
        finally:
            # Ensure objection is dropped even if error occurs
            await Timer(20, "ns")  # Cleanup period
            phase.drop_objection(self)