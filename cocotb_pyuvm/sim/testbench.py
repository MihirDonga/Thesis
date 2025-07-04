import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from pyuvm import *
from apbuart_base_test import apbuart_base_test  
# from apbuart_config_test import apbuart_config_test
# Simple version without interface classes - direct signal access
# from pyuvm import *
# from uart_config import uart_config
# from apb_config import apb_config
# from apbuart_environment import APBUARTEnv
# from cocotb.triggers import Timer
# # from apbuart_vseq_base import apbuart_config_seq

# class apbuart_base_test(uvm_test):
#     def __init__(self, name="apbuart_base_test", parent=None):
#         super().__init__(name, parent)
#         self.env_sq = None
#         self.cfg = None
#         self.apb_cfg = None
#         self.error_count = 0  # Manual error counter

#     def build_phase(self):
#         super().build_phase()
#         self.logger.info(f"{self.get_name()} - Inside build_phase")
        
#         # uvm_component, uvm_env, uvm_agent, scoreboard, sequencer	Yes (standard way)
#         # uvm_sequence	hsas No, instantiate directly via constructor
#         self.env_sq =  APBUARTEnv.create("env_sq",self) 
#         self.cfg = uart_config()
#         self.apb_cfg = apb_config()
#         for _ in range(self.cfg.loop_time):
#                 self.set_config_params(9600, 8, 3, 1, 1)
#                 self.set_apbconfig_params(2, 1)
        
#         ConfigDB().set(None, "*", "cfg", self.cfg)
#         ConfigDB().set(None, "*", "apb_cfg", self.apb_cfg)        

#     def set_config_params(self, bd_rate, frm_len, parity, sb, flag):
#         if flag:
#             self.cfg.randomize()
#         else:
#             self.cfg.frame_len = frm_len
#             self.cfg.n_sb = sb
#             self.cfg.parity = parity
#             self.cfg.bRate = bd_rate
#             self.cfg.baudRateFunc()

#         self.logger.info(f"{self.get_name()} - UART Config after set_config_params:\n{self.cfg}")

#     def set_apbconfig_params(self, addr, flag):
#         if flag:
#             self.apb_cfg.randomize()
#         else:
#             self.apb_cfg.slave_Addr = addr
#             self.apb_cfg.AddrCalcFunc()

#         self.logger.info(f"{self.get_name()} - APB Config after set_apbconfig_params:\n{self.apb_cfg}")

#     def report_error(self, msg):
#         self.logger.error(msg)
#         self.error_count += 1

#     # def end_of_elaboration_phase(self, phase):
#     #     super().end_of_elaboration_phase(phase)
#     #     self.print_obj()

#     def report_phase(self):
#         super().report_phase()

#         if self.error_count> 0:
#             self.logger.critical(f"{self.get_name()} - -" * 39)
#             self.logger.critical(f"{self.get_name()} - ----            TEST FAIL          ----")
#             self.logger.critical(f"{self.get_name()} - -" * 39)
#         else:
#             self.logger.critical(f"{self.get_name()} - -" * 39)
#             self.logger.critical(f"{self.get_name()} - ----           TEST PASS           ----")
#             self.logger.critical(f"{self.get_name()} - -" * 39)

@cocotb.test()
async def tbench_top(dut):
    
    # Clock Generation: 50 MHz (20 ns period)
    cocotb.start_soon(Clock(dut.PCLK, 20, units="ns").start())

    # Reset Generation (Active Low)
    dut.PRESETn.value = 0
    await Timer(100, units="ns")  # Hold reset low for 100 ns
    dut.PRESETn.value = 1
    await RisingEdge(dut.PCLK)

    # Store signals in ConfigDB for access by UVM components
    ConfigDB().set(None, "*", "dut", cocotb.top)  # You can pass entire DUT for convenience

    # Start UVM test (equivalent to run_test())
    await uvm_root().run_test(apbuart_base_test)
# # @cocotb.test()
# # async def tbench_top(dut):
#     from pyuvm import uvm_root
#     root = uvm_root()
#     print("Registered test classes:", factory._registry.keys())
#     await uvm_root().run_test("apbuart_config_test")


# | Where           | Action                                   | Example                                          |
# | --------------- | ---------------------------------------- | ------------------------------------------------ |
# | **Test**        | Set config objects globally              | `ConfigDB().set(None, "*", "cfg", self.cfg)`     |
# | **Env**         | Set real sequencers for virtual sqr      | `ConfigDB().set(self, "*", "apb_sqr", apb_seqr)` |
# | **Agent**       | Get config (`cfg`)                       | `cfg = ConfigDB.get(None, "", "cfg")`            |
# | **VSequencer**  | Get handles to child sequencers          | `apb_sqr = ConfigDB.get(None, "", "apb_sqr")`    |
# | **Virtual Seq** | Use `self.seqr.apb_sqr` to run sequences | `await my_seq.start(self.seqr.apb_sqr)`          |
