# Choose simulator: xcelium (default) or icarus
SIM ?= xcelium
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = hello_world.sv
TOPLEVEL = hello_world
MODULE = hello_test

# Python & pyuvm paths
PYTHONPATH := $(shell pwd):$(PYTHONPATH)
PYUVM_LIB := $(shell python3 -c "import pyuvm; print(pyuvm.get_lib_path())")
export LD_LIBRARY_PATH := $(PYUVM_LIB):$(LD_LIBRARY_PATH)

# Simulator-specific flags
ifeq ($(SIM),xcelium)
    SIM_ARGS = -64bit -access +rw -sv_lib python3
else ifeq ($(SIM),icarus)
    SIM_ARGS = -g2012
endif

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: clean
clean::
	rm -rf sim_build __pycache__ results.xml *.vcd *.log *.vpd