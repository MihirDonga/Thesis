import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from pyuvm import *
from apbuart_config_test import apbuart_config_test  

# Simple version without interface classes - direct signal access
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
    ConfigDB().set(None, "*", "dut", dut)  # You can pass entire DUT for convenience

    # Start UVM test (equivalent to run_test())
    await uvm_root().run_test(apbuart_config_test)