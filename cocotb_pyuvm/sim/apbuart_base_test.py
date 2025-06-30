from pyuvm import *
from uart_config import uart_config
from apb_config import apb_config
from apbuart_environment import APBUARTEnv

class apbuart_base_test(uvm_test):
    def __init__(self, name="apbuart_base_test", parent=None):
        super().__init__(name, parent)
        self.env_sq = None
        self.cfg = uart_config()
        self.apb_cfg = apb_config()
        self.error_count = 0  # Manual error counter

    def build_phase(self, phase):
        self.logger.info(f"{self.get_name()} - Inside build_phase")
        
        # uvm_component, uvm_env, uvm_agent, scoreboard, sequencer	Yes (standard way)
        # uvm_sequence	hsas No, instantiate directly via constructor
        self.env_sq =  APBUARTEnv.type_id.create("env_sq") 

        ConfigDB().set(self, "*", "cfg", self.cfg)
        self.set_config_params(9600, 8, 3, 1, 0)

        ConfigDB().set(self, "*", "apb_cfg", self.apb_cfg)
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

    def end_of_elaboration_phase(self, phase):
        self.print_obj()

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
