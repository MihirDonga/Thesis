
SIM ?= xcelium
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES =$(wildcard rtl/*.sv)
TOPLEVEL = tbench_top
MODULE = testbench

# Critical Python paths
export PYTHONPATH := $(shell pwd):$(PYTHONPATH)
export LD_LIBRARY_PATH := $(shell python3 -c "import pyuvm; print(pyuvm.get_lib_path())"):$(LD_LIBRARY_PATH)

# Xcelium flags
XRUN_ARGS += -disable_sem2009 -nocopyright

include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	rm -rf sim_build __pycache__ results.xml *.vcd *.log