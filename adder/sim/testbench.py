import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge
from pyuvm import *

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

    # Store interfaces in ConfigDB (direct DUT access)
    ConfigDB().set(None, "*", "PCLK", dut.PCLK)
    ConfigDB().set(None, "*", "PRESETn", dut.PRESETn)
    
    # Store individual signals as needed
    apb_signals = {
        'PSELx': dut.PSELx,
        'PENABLE': dut.PENABLE,
        'PWRITE': dut.PWRITE,
        'PADDR': dut.PADDR,
        'PWDATA': dut.PWDATA,
        'PRDATA': dut.PRDATA,
        'PREADY': dut.PREADY,
        'PSLVERR': dut.PSLVERR
    }
    ConfigDB().set(None, "*", "vifapb", apb_signals)
    
    uart_signals = {
        'Tx': dut.Tx,
        'RX': dut.RX
    }
    ConfigDB().set(None, "*", "vifuart", uart_signals)

    # Start UVM test (equivalent to run_test())
    await uvm_root().run_test()