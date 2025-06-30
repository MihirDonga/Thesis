
SIM ?= xcelium
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES =$(wildcard rtl/*.sv)
TOPLEVEL = tbench_top
MODULE = testbench

# Critical Python paths
export PYTHONPATH := $(shell pwd):$(PYTHONPATH)

# Xcelium flags
XRUN_ARGS += -incdir rtl
XRUN_ARGS += -disable_sem2009 -nocopyright
XRUN_ARGS += -access +rwc -timescale 1ns/1ps

# PyUVM/Cocotb integration
ifeq ($(SIM),xcelium)
    EXTRA_ARGS += -loadvpi $(shell cocotb-config --lib-name-path vpi xcelium)
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf sim_build __pycache__ results.xml *.vcd *.log