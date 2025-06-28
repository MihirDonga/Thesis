# # Choose simulator: xcelium (default) or icarus
# SIM ?= xcelium
# TOPLEVEL_LANG ?= verilog
# VERILOG_SOURCES = hello_world.sv
# TOPLEVEL = helloworld
# MODULE = hello_test

# # Python & pyuvm paths
# PYTHONPATH := $(shell pwd):$(PYTHONPATH)
# PYUVM_LIB := $(shell python3 -c "import pyuvm; print(pyuvm.get_lib_path())")
# export LD_LIBRARY_PATH := $(PYUVM_LIB):$(LD_LIBRARY_PATH)

# # Simulator-specific flags
# ifeq ($(SIM),xcelium)
#     SIM_ARGS = -64bit -access +rw -sv_lib python3
# else ifeq ($(SIM),icarus)
#     SIM_ARGS = -g2012
# endif

# include $(shell cocotb-config --makefiles)/Makefile.sim

# .PHONY: clean
# clean::
# 	rm -rf sim_build __pycache__ results.xml *.vcd *.log *.vpd


SIM ?= xcelium
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = hello_world.sv
TOPLEVEL = full_adder
MODULE = hello_test


# Xcelium coverage options (VCS-like)
XRUN_ARGS += -coverage all
XRUN_ARGS += -covdut full_adder
XRUN_ARGS += -covoverwrite
XRUN_ARGS += -covfile cov.ccf  # Coverage configuration file

# Python coverage collection
export PYTHON_COVERAGE=1

include $(shell cocotb-config --makefiles)/Makefile.sim

cov_report:
    imc -load test_cov/work -execcmd "report -detail -both -out cov_report.txt"
    python -m coverage html -d coverage_html

clean::
    rm -rf sim_build __pycache__ results.xml *.vcd *.log *.ucd *.ucm cov_report.txt coverage_html