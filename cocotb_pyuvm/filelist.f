+sv
+incdir+./rtl
+access+rwc
-coverage all
// -covdut apb_uart_tb
-covoverwrite
-covwork cov_work
+incdir+./tb
+incdir+./rtl
-loadvpi libcocotbvpi.so:vlog_startup_routines_bootstrap

// RTL files (make sure to list all needed RTL files here)
rtl/Defines.sv
rtl/apb_slave.sv
rtl/apb_uart.sv
rtl/apb_uart_top.sv
rtl/tick_generator.sv
rtl/uart_rx_BB.sv
rtl/uart_transmitter.sv

tb/apbinterface.sv
tb/uartinterface.sv

// Testbench package and UVM components
tb/testbench_pkg.sv

// Top level testbench
tb/testbench.sv


