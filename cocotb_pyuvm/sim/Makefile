# Language and Simulator
TOPLEVEL_LANG = verilog
SIM = verilator

# RTL and Testbench
VERILOG_SOURCES = ../rtl/full_adder.v
TOPLEVEL = full_adder
MODULE = test_full_adder

# Enable waveform dumping (VCD)
SIM_ARGS += --trace --trace-fst --trace-file full_adder.vcd
VERILATOR_TRACE = 1

# Enable waveform viewing from cocotb
export COCOTB_WAVES = 1

# Include cocotb's makefile infrastructure
include $(shell cocotb-config --makefiles)/Makefile.sim
