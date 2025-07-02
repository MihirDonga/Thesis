import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from pyuvm import *
from apbuart_base_test import apbuart_base_test  
# from apbuart_config_test import apbuart_config_test
# Simple version without interface classes - direct signal access
@cocotb.test()
async def tbench_top(dut):
    
    # # Clock Generation: 50 MHz (20 ns period)
    # cocotb.start_soon(Clock(dut.PCLK, 20, units="ns").start())

    # # Reset Generation (Active Low)
    # dut.PRESETn.value = 0
    # await Timer(100, units="ns")  # Hold reset low for 100 ns
    # dut.PRESETn.value = 1
    # await RisingEdge(dut.PCLK)

    # # Store signals in ConfigDB for access by UVM components
    # ConfigDB().set(None, "*", "dut", dut)  # You can pass entire DUT for convenience

    # # Start UVM test (equivalent to run_test())
    # await uvm_root().run_test(apbuart_base_test)
# @cocotb.test()
# async def tbench_top(dut):
    from pyuvm import uvm_root
    root = uvm_root()
    print("Registered test classes:", factory._registry.keys())
    await uvm_root().run_test("apbuart_config_test")


# | Where           | Action                                   | Example                                          |
# | --------------- | ---------------------------------------- | ------------------------------------------------ |
# | **Test**        | Set config objects globally              | `ConfigDB().set(None, "*", "cfg", self.cfg)`     |
# | **Env**         | Set real sequencers for virtual sqr      | `ConfigDB().set(self, "*", "apb_sqr", apb_seqr)` |
# | **Agent**       | Get config (`cfg`)                       | `cfg = ConfigDB.get(None, "", "cfg")`            |
# | **VSequencer**  | Get handles to child sequencers          | `apb_sqr = ConfigDB.get(None, "", "apb_sqr")`    |
# | **Virtual Seq** | Use `self.seqr.apb_sqr` to run sequences | `await my_seq.start(self.seqr.apb_sqr)`          |
