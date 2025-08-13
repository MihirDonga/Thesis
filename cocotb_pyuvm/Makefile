
SIM ?= xcelium
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES =$(wildcard rtl/*.sv)
TOPLEVEL = apb_uart_top
MODULE = testbench

# Critical Python paths
export PYTHONPATH := $(PWD)/sim:$(PYTHONPATH)

# Xcelium flags
XRUN_ARGS += -incdir $(PWD)/rtl
XRUN_ARGS +=  -sv_lib $(shell cocotb-config --lib-name-path vpi xcelium)
XRUN_ARGS += -access +rwc -timescale 1ns/1ps


include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf sim_build __pycache__ results.xml *.vcd *.log