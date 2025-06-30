from pyuvm import *
from uart_config import uart_config
from apb_config import apb_config
from apbuart_environment import APBUARTEnv
from pyuvm import UVM_FATAL, UVM_ERROR, UVM_NONE, UVM_MEDIUM, UVM_LOW
from pyuvm import uvm_report_server

class apbuart_base_test(uvm_test):
    def __init__(self, name="apbuart_base_test", parent=None):
        super().__init__(name, parent)
        self.env_sq = None
        self.cfg = uart_config()
        self.apb_cfg = apb_config()

    def build_phase(self, phase):
        self.logger.info(f"{self.get_name()} - Inside build_phase", UVM_MEDIUM)
        
        # uvm_component, uvm_env, uvm_agent, scoreboard, sequencer	Yes (standard way)
        # uvm_sequence	hsas No, instantiate directly via constructor
        self.env_sq =  APBUARTEnv("env_sq", self) 

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

        self.logger.info(f"{self.get_name()} - UART Config after set_config_params:\n{self.cfg}", UVM_LOW)

    def set_apbconfig_params(self, addr, flag):
        if flag:
            self.apb_cfg.randomize()
        else:
            self.apb_cfg.slave_Addr = addr
            self.apb_cfg.AddrCalcFunc()

        self.logger.info(f"{self.get_name()} - APB Config after set_apbconfig_params:\n{self.apb_cfg}", UVM_LOW)

    def end_of_elaboration_phase(self, phase):
        self.print_obj()

    def report_phase(self, phase):
        super().report_phase(phase)

        svr = uvm_report_server.get_server()

        if svr.get_severity_count(UVM_FATAL) + svr.get_severity_count(UVM_ERROR) > 0:
            self.logger.info(f"{self.get_name()} - -" * 39, UVM_NONE)
            self.logger.info(f"{self.get_name()} - ----            TEST FAIL          ----", UVM_NONE)
            self.logger.info(f"{self.get_name()} - -" * 39, UVM_NONE)
        else:
            self.logger.info(f"{self.get_name()} - -" * 39, UVM_NONE)
            self.logger.info(f"{self.get_name()} - ----           TEST PASS           ----", UVM_NONE)
            self.logger.info(f"{self.get_name()} - -" * 39, UVM_NONE)
